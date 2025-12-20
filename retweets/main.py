import os
import json
import math

import cudf
import dask_cudf as dc

from dask_cuda import LocalCUDACluster
from dask.distributed import Client

import cugraph.dask as dcg
from cugraph.dask.comms import comms as Comms


# =========================
# EDIT THESE SETTINGS
# =========================
INPUT_PATH = "/workspace/retweet_network2017.csv"     # <-- your no-header CSV path (can be glob too)
OUTDIR = "/workspace/network_desc_TSLA"

COMPANY_FILTER = "TSLA"

# You can use "2021-01-01" or "2021-01-01 00:00:00"
START_TIME = "2021-01-01"
END_TIME   = "2021-12-31"

DIRECTED = True
DROP_SELF_LOOPS = True

NGPUS = 8
RMM_POOL_GB = 24

# If timestamp is unix int, set True + unit
TIMESTAMP_IS_UNIX = False
UNIX_UNIT = "s"  # "s" or "ms"
# =========================

COLS = ["company", "edgeA", "edgeB", "year", "month", "timestamp"]


def safe_float(x, default=float("nan")):
    try:
        return float(x)
    except Exception:
        return default


def gini_from_cudf(s: cudf.Series) -> float:
    s = s.dropna().astype("float64")
    s = s[s >= 0]
    if len(s) == 0:
        return float("nan")
    total = float(s.sum())
    if total <= 0:
        return 0.0
    s = s.sort_values()
    n = len(s)
    idx = cudf.Series(range(1, n + 1), dtype="float64")
    g = (2.0 * float((idx * s).sum()) / (n * total)) - ((n + 1.0) / n)
    return float(g)


def herfindahl_from_cudf(s: cudf.Series) -> float:
    s = s.dropna().astype("float64")
    if len(s) == 0:
        return float("nan")
    total = float(s.sum())
    if total <= 0:
        return 0.0
    p = s / total
    return float((p * p).sum())


def top_share_from_cudf(s: cudf.Series, top_frac: float) -> float:
    s = s.dropna().astype("float64")
    if len(s) == 0:
        return float("nan")
    total = float(s.sum())
    if total <= 0:
        return 0.0
    k = max(1, int(math.ceil(top_frac * len(s))))
    return float(s.sort_values(ascending=False).head(k).sum() / total)


def normalize_end_of_day(ts: cudf.Timestamp) -> cudf.Timestamp:
    # if end time is date-only interpreted as midnight, expand to end-of-day
    if ts.hour == 0 and ts.minute == 0 and ts.second == 0 and ts.microsecond == 0:
        return ts + cudf.Timedelta(days=1) - cudf.Timedelta(microseconds=1)
    return ts


def parse_timestamp_dask(col):
    # col is a dask_cudf Series
    if TIMESTAMP_IS_UNIX:
        return dc.to_datetime(col, unit=UNIX_UNIT, errors="coerce")
    return dc.to_datetime(col, errors="coerce")


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    cluster = LocalCUDACluster(
        CUDA_VISIBLE_DEVICES=list(range(NGPUS)),
        rmm_pool_size=f"{RMM_POOL_GB}GB",
        protocol="tcp",
    )
    client = Client(cluster)
    Comms.initialize(p2p=True)

    # ---- Read no-header CSV on GPU (distributed) ----
    # IMPORTANT: no header => header=None, names=COLS
    ddf = dc.read_csv(
        INPUT_PATH,
        header=None,
        names=COLS,
        dtype={
            "company": "str",
            "edgeA": "str",
            "edgeB": "str",
            "year": "int32",
            "month": "int8",
            # timestamp read as object/str; parsed next
            "timestamp": "str",
        }
    )

    # ---- Filter company ----
    ddf = ddf[ddf["company"] == COMPANY_FILTER]

    # ---- Parse timestamp + time filter ----
    ddf["timestamp"] = parse_timestamp_dask(ddf["timestamp"])
    ddf = ddf.dropna(subset=["edgeA", "edgeB", "timestamp"])

    start_ts = cudf.to_datetime(START_TIME)
    end_ts = cudf.to_datetime(END_TIME)
    end_ts = normalize_end_of_day(end_ts)

    ddf = ddf[(ddf["timestamp"] >= start_ts) & (ddf["timestamp"] <= end_ts)]

    # Rename for graph logic
    events = ddf.rename(columns={"edgeA": "src", "edgeB": "dst", "timestamp": "ts"})[["src", "dst", "ts"]]

    # Count events (retweet rows)
    n_events = int(events.shape[0].compute())

    summary = {
        "company": COMPANY_FILTER,
        "start_time": START_TIME,
        "end_time": END_TIME,
        "n_retweet_events": n_events,
        "directed": bool(DIRECTED),
    }

    if n_events == 0:
        with open(os.path.join(OUTDIR, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
        print("No events in range.")
        Comms.destroy(); client.close(); cluster.close()
        return

    # ---- Temporal diffusion metrics (GPU) ----
    # Sort events by ts (bring minimal to single GPU for exact quantiles)
    # If a company-window is enormous, you can compute approx quantiles instead.
    ev_cu = events[["ts"]].compute().sort_values("ts")
    total = len(ev_cu)
    t0 = ev_cu["ts"].iloc[0]
    t10 = ev_cu["ts"].iloc[max(0, int(math.ceil(0.10 * total)) - 1)]
    t50 = ev_cu["ts"].iloc[max(0, int(math.ceil(0.50 * total)) - 1)]
    t90 = ev_cu["ts"].iloc[max(0, int(math.ceil(0.90 * total)) - 1)]

    summary["t10_hours"] = float((t10 - t0).total_seconds() / 3600.0)
    summary["t50_hours"] = float((t50 - t0).total_seconds() / 3600.0)
    summary["t90_hours"] = float((t90 - t0).total_seconds() / 3600.0)

    # Peak hour / 10-min share (GPU bucketing)
    ev_cu["hour_bucket"] = ev_cu["ts"].dt.floor("H")
    ev_cu["tenmin_bucket"] = ev_cu["ts"].dt.floor("10min")
    hourly = ev_cu.groupby("hour_bucket").size()
    tenmin = ev_cu.groupby("tenmin_bucket").size()
    summary["peak_hour_share"] = float(hourly.max() / total) if len(hourly) else float("nan")
    summary["peak_10min_share"] = float(tenmin.max() / total) if len(tenmin) else float("nan")

    # ---- Weighted edges (GPU): weight = count of events per (src,dst) ----
    edges = events.groupby(["src", "dst"]).size().reset_index().rename(columns={0: "weight"})

    if DROP_SELF_LOOPS:
        edges = edges[edges["src"] != edges["dst"]]

    # Persist helps on big runs
    edges = edges.persist()

    n_edges_unique = int(edges.shape[0].compute())
    total_weight = int(edges["weight"].sum().compute())

    summary["n_edges_unique"] = n_edges_unique
    summary["total_weight"] = total_weight
    summary["avg_weight_per_edge"] = safe_float(total_weight / n_edges_unique) if n_edges_unique else float("nan")

    # ---- Build multi-GPU graph ----
    G = dcg.DiGraph() if DIRECTED else dcg.Graph()
    G.from_dask_cudf_edgelist(
        edges, source="src", destination="dst", edge_attr="weight", renumber=True
    )

    n_nodes = int(G.number_of_vertices())
    summary["n_nodes"] = n_nodes
    summary["density"] = float(n_edges_unique / (n_nodes * (n_nodes - 1))) if n_nodes > 1 else float("nan")

    # ---- Strengths (weighted degrees) ----
    indeg = dcg.in_degree(G, weight="weight").compute().rename(columns={"in_degree": "in_strength"})
    outdeg = dcg.out_degree(G, weight="weight").compute().rename(columns={"out_degree": "out_strength"})
    deg = indeg.merge(outdeg, on="vertex", how="outer").fillna(0)

    deg.to_parquet(os.path.join(OUTDIR, "node_strengths.parquet"), index=False)

    in_s = deg["in_strength"].astype("float64")
    out_s = deg["out_strength"].astype("float64")

    # Concentration summaries
    summary.update({
        "in_gini": gini_from_cudf(in_s),
        "in_hhi": herfindahl_from_cudf(in_s),
        "in_top1_share": top_share_from_cudf(in_s, 0.01),
        "in_top5_share": top_share_from_cudf(in_s, 0.05),
        "in_top10_share": top_share_from_cudf(in_s, 0.10),
        "in_max_share": top_share_from_cudf(in_s, 1.0 / max(1, n_nodes)),

        "out_gini": gini_from_cudf(out_s),
        "out_hhi": herfindahl_from_cudf(out_s),
        "out_top1_share": top_share_from_cudf(out_s, 0.01),
        "out_top5_share": top_share_from_cudf(out_s, 0.05),
        "out_top10_share": top_share_from_cudf(out_s, 0.10),
        "out_max_share": top_share_from_cudf(out_s, 1.0 / max(1, n_nodes)),
    })

    # ---- Components ----
    wcc = dcg.weakly_connected_components(G).compute()
    wcc_sizes = wcc.groupby("labels").size()
    summary["n_wcc"] = int(len(wcc_sizes))
    summary["largest_wcc_share"] = float(wcc_sizes.max() / n_nodes) if n_nodes else float("nan")

    scc = dcg.strongly_connected_components(G).compute()
    scc_sizes = scc.groupby("labels").size()
    summary["n_scc"] = int(len(scc_sizes))
    summary["largest_scc_share"] = float(scc_sizes.max() / n_nodes) if n_nodes else float("nan")

    # ---- PageRank (weighted) ----
    try:
        pr = dcg.pagerank(G, weight="weight").compute()
        pr.to_parquet(os.path.join(OUTDIR, "pagerank.parquet"), index=False)
        summary["pagerank_gini"] = gini_from_cudf(pr["pagerank"])
        summary["pagerank_top1_share"] = top_share_from_cudf(pr["pagerank"], 0.01)
    except Exception:
        summary["pagerank_gini"] = float("nan")
        summary["pagerank_top1_share"] = float("nan")

    # ---- Louvain communities (on undirected projection) ----
    try:
        Gu = dcg.Graph()
        Gu.from_dask_cudf_edgelist(edges, source="src", destination="dst", edge_attr="weight", renumber=True)
        parts, modularity = dcg.louvain(Gu)
        parts = parts.compute()
        parts.to_parquet(os.path.join(OUTDIR, "communities.parquet"), index=False)
        comm_sizes = parts.groupby("partition").size().astype("float64")
        summary["modularity"] = safe_float(modularity)
        summary["n_communities"] = int(len(comm_sizes))
        summary["comm_herf"] = herfindahl_from_cudf(comm_sizes)
        summary["largest_comm_share"] = float(comm_sizes.max() / n_nodes) if n_nodes else float("nan")
    except Exception:
        summary["modularity"] = float("nan")
        summary["n_communities"] = 0
        summary["comm_herf"] = float("nan")
        summary["largest_comm_share"] = float("nan")

    # ---- k-core (on undirected projection) ----
    try:
        Gu = dcg.Graph()
        Gu.from_dask_cudf_edgelist(edges, source="src", destination="dst", edge_attr="weight", renumber=True)
        core = dcg.core_number(Gu).compute()
        summary["max_core"] = float(core["core_number"].max()) if len(core) else float("nan")
        core.to_parquet(os.path.join(OUTDIR, "core_number.parquet"), index=False)
    except Exception:
        summary["max_core"] = float("nan")

    # Save weighted edges too
    edges.compute().to_parquet(os.path.join(OUTDIR, "weighted_edges.parquet"), index=False)

    # Write summary
    with open(os.path.join(OUTDIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("DONE. Wrote outputs to:", OUTDIR)

    Comms.destroy()
    client.close()
    cluster.close()


if __name__ == "__main__":
    main()

