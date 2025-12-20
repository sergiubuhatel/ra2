import os
import json
import math

import cudf
import dask_cudf as dc

from dask_cuda import LocalCUDACluster
from dask.distributed import Client

import cugraph.dask as dcg
from cugraph.dask.comms import comms as Comms

import numpy as np
import pandas as pd

import cugraph

# =========================
# EDIT THESE SETTINGS
# =========================
INPUT_PATH = "/workspace/retweet_network2017.csv"
OUTDIR = "/workspace/output/network_desc_TSLA"

COMPANY_FILTER = "TSLA"

START_TIME = "2017-01-01"
END_TIME = "2017-12-31"

DIRECTED = True
DROP_SELF_LOOPS = True

NGPUS = 8
RMM_POOL_GB = 24

TIMESTAMP_IS_UNIX = False
UNIX_UNIT = "s"
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
    return float((2.0 * float((idx * s).sum()) / (n * total)) - ((n + 1.0) / n))


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


def normalize_end_of_day(ts):
    ts = pd.Timestamp(ts)
    if ts.hour == 0 and ts.minute == 0 and ts.second == 0 and ts.microsecond == 0:
        ts = ts + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    return ts


def parse_timestamp_dask_safe(col):
    def _parse_partition(s):
        pdf = s.to_pandas()
        dt = pd.to_datetime(pdf, unit=UNIX_UNIT if TIMESTAMP_IS_UNIX else None, errors="coerce")
        return cudf.Series(dt)

    return col.map_partitions(_parse_partition, meta=col._meta.astype("datetime64[ns]"))


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    cluster = LocalCUDACluster(
        CUDA_VISIBLE_DEVICES=list(range(NGPUS)),
        rmm_pool_size=f"{RMM_POOL_GB}GB",
        protocol="tcp",
    )
    client = Client(cluster)
    Comms.initialize(p2p=True)

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
            "timestamp": "str",
        }
    )

    ddf = ddf[ddf["company"] == COMPANY_FILTER]
    ddf["timestamp"] = parse_timestamp_dask_safe(ddf["timestamp"])
    ddf = ddf.dropna(subset=["edgeA", "edgeB", "timestamp"])

    start_ts = pd.Timestamp(START_TIME)
    end_ts = normalize_end_of_day(pd.Timestamp(END_TIME))
    ddf = ddf[(ddf["timestamp"] >= start_ts) & (ddf["timestamp"] <= end_ts)]

    events = ddf.rename(columns={"edgeA": "src", "edgeB": "dst", "timestamp": "ts"})[["src", "dst", "ts"]]

    n_events = int(events.shape[0].compute())
    summary = {
        "company": COMPANY_FILTER,
        "start_time": START_TIME,
        "end_time": END_TIME,
        "n_retweet_events": n_events,
        "directed": True,
    }

    if n_events == 0:
        json.dump(summary, open(os.path.join(OUTDIR, "summary.json"), "w"), indent=2)
        return

    ev_cu = events[["ts"]].compute().sort_values("ts")
    total = len(ev_cu)
    t0 = ev_cu["ts"].iloc[0]
    summary["t10_hours"] = float((ev_cu["ts"].iloc[int(0.1 * total)] - t0) / pd.Timedelta(hours=1))
    summary["t50_hours"] = float((ev_cu["ts"].iloc[int(0.5 * total)] - t0) / pd.Timedelta(hours=1))
    summary["t90_hours"] = float((ev_cu["ts"].iloc[int(0.9 * total)] - t0) / pd.Timedelta(hours=1))

    edges = events.groupby(["src", "dst"]).size().reset_index().rename(columns={0: "weight"})
    if DROP_SELF_LOOPS:
        edges = edges[edges["src"] != edges["dst"]]

    edges_cu = edges.compute()

    G = cugraph.Graph(directed=True)
    G.from_cudf_edgelist(edges_cu, "src", "dst", edge_attr="weight", renumber=True)

    n_nodes = int(G.number_of_vertices())
    summary["n_nodes"] = n_nodes

    indeg = edges_cu.groupby("dst")["weight"].sum().reset_index().rename(
        columns={"dst": "vertex", "weight": "in_strength"})
    outdeg = edges_cu.groupby("src")["weight"].sum().reset_index().rename(
        columns={"src": "vertex", "weight": "out_strength"})
    deg = indeg.merge(outdeg, on="vertex", how="outer").fillna(0)

    # ---- Concentration measures (FIXED & DGX-safe) ----
    in_s = deg["in_strength"].astype("float64")
    out_s = deg["out_strength"].astype("float64")

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

    # ---- FIX: UNDIRECTED GRAPH FOR WCC ----
    Gu_wcc = cugraph.Graph(directed=False)
    Gu_wcc.from_cudf_edgelist(edges_cu, "src", "dst", edge_attr="weight", renumber=True)

    wcc = cugraph.connected_components(Gu_wcc)
    wcc_sizes = wcc.groupby("labels").size()
    summary["n_wcc"] = int(len(wcc_sizes))
    summary["largest_wcc_share"] = float(wcc_sizes.max() / n_nodes)

    # ---- SCC (directed) ----
    scc = cugraph.strongly_connected_components(G)
    scc_sizes = scc.groupby("labels").size()
    summary["n_scc"] = int(len(scc_sizes))
    summary["largest_scc_share"] = float(scc_sizes.max() / n_nodes)

    json.dump(summary, open(os.path.join(OUTDIR, "summary.json"), "w"), indent=2)

    Comms.destroy()
    client.close()
    cluster.close()


if __name__ == "__main__":
    main()
