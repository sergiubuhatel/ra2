#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, csv, glob, json, math, argparse, traceback
from datetime import datetime, timedelta
from multiprocessing import get_context
from typing import Dict, Any, Tuple, Optional

import pandas as pd
import cudf
import numpy as np
import re
import cupy as cp


# ----------------------------
# CLI
# ----------------------------
def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument("--parquet-root", required=True)
    p.add_argument("--windows-file", required=True)
    p.add_argument("--outroot", required=True)

    p.add_argument("--ngpus", type=int, default=8)
    p.add_argument("--queue-max", type=int, default=20000)

    p.add_argument("--src-col", default="edgeA")
    p.add_argument("--dst-col", default="edgeB")
    p.add_argument("--timestamp-col", default="timestamp")

    p.add_argument("--drop-self-loops", action="store_true")
    p.add_argument("--skip-existing", action="store_true")
    p.add_argument("--max-tasks", type=int, default=0)

    # robustness / validation
    p.add_argument("--validation-tol", type=float, default=1e-6)
    p.add_argument("--fail-fast-window", action="store_true")
    p.add_argument("--fail-fast-global", action="store_true")

    # variants: robustness to weight definition / noise
    p.add_argument("--variants", default="base,unweighted,thr2",
                   help="Comma-separated: base,unweighted,thr2,thr3")

    # diffusion (time binning)
    p.add_argument("--diff-bin", default="10min", help="e.g., 1min,5min,10min,1H")
    p.add_argument("--growth-window-hours", type=float, default=2.0,
                   help="Fit early growth rate on first X hours from first event")

    # extras (may be heavy; version dependent)
    p.add_argument("--extra-centrality", action="store_true")
    p.add_argument("--save-node-tables", action="store_true")

    return p.parse_args()


def safe_float(x, default=float("nan")):
    try:
        return float(x)
    except Exception:
        return default


def month_iter(start_dt: datetime, end_dt: datetime):
    y, m = start_dt.year, start_dt.month
    while True:
        yield y, m
        if (y == end_dt.year) and (m == end_dt.month):
            break
        m += 1
        if m == 13:
            m = 1
            y += 1


# ----------------------------
# GPU helpers (require cudf)
# ----------------------------
def normalize_end_of_day_cudf(cudf, end_ts):
    # Convert numpy.datetime64 / cudf scalar to Python datetime
    if isinstance(end_ts, (pd.Timestamp, pd.DatetimeTZDtype)):
        end_ts = end_ts.to_pydatetime()
    elif hasattr(end_ts, "astype"):  # numpy.datetime64 or cudf scalar
        end_ts = pd.Timestamp(end_ts).to_pydatetime()

    # If end is date-only midnight, include full day
    if end_ts.hour == 0 and end_ts.minute == 0 and end_ts.second == 0 and end_ts.microsecond == 0:
        return end_ts + timedelta(days=1) - timedelta(microseconds=1)
    return end_ts


def gini_cudf(cudf, s):
    s = s.dropna().astype("float64")
    s = s[s >= 0]
    n = len(s)
    if n == 0:
        return float("nan")
    total = float(s.sum())
    if total <= 0:
        return 0.0
    s = s.sort_values()
    idx = cudf.Series(range(1, n + 1), dtype="float64")
    g = (2.0 * float((idx * s).sum()) / (n * total)) - ((n + 1.0) / n)
    if g < 0 and g > -1e-12:
        g = 0.0
    return float(g)


def hhi_cudf(s):
    s = s.dropna().astype("float64")
    if len(s) == 0:
        return float("nan")
    tot = float(s.sum())
    if tot <= 0:
        return 0.0
    p = s / tot
    return float((p * p).sum())


def entropy_share_cudf(s):
    # entropy of shares p_i = s_i/sum(s)
    s = s.dropna().astype("float64")
    tot = float(s.sum())
    if len(s) == 0 or tot <= 0:
        return float("nan")
    p = (s / tot).astype("float64")
    # avoid log(0)
    p = p[p > 0]
    if len(p) == 0:
        return float("nan")
    return float(-(p * cp.log(p)).sum())


def theil_share_cudf(s):
    # Theil index on shares: T = sum p_i * log(p_i * n)
    s = s.dropna().astype("float64")
    tot = float(s.sum())
    n = len(s)
    if n == 0 or tot <= 0:
        return float("nan")
    p = (s / tot).astype("float64")
    p = p[p > 0]
    if len(p) == 0:
        return float("nan")
    return float((p * cp.log(p * float(n))).sum())


def top_share_cudf(s, frac):
    s = s.dropna().astype("float64")
    n = len(s)
    if n == 0:
        return float("nan")
    tot = float(s.sum())
    if tot <= 0:
        return 0.0
    k = max(1, int(math.ceil(frac * n)))
    return float(s.sort_values(ascending=False).head(k).sum() / tot)


def quantiles_cudf(s, qs=(0.25, 0.5, 0.75, 0.9, 0.95, 0.99)):
    s = s.dropna().astype("float64")
    if len(s) == 0:
        return {f"q{int(q*100)}": float("nan") for q in qs}
    qv = s.quantile(list(qs))
    return {f"q{int(q*100)}": safe_float(qv.loc[q]) for q in qs}


def stats_pack_cudf(s, prefix):
    s = s.dropna().astype("float64")
    out = {
        f"{prefix}_mean": safe_float(s.mean()) if len(s) else float("nan"),
        f"{prefix}_std": safe_float(s.std()) if len(s) > 1 else float("nan"),
        f"{prefix}_min": safe_float(s.min()) if len(s) else float("nan"),
        f"{prefix}_max": safe_float(s.max()) if len(s) else float("nan"),
    }
    for k, v in quantiles_cudf(s).items():
        out[f"{prefix}_{k}"] = v
    return out


def conc_pack_cudf(cudf, s, prefix):
    s = s.dropna().astype("float64")
    return {
        f"{prefix}_gini": gini_cudf(cudf, s),
        f"{prefix}_hhi": hhi_cudf(s),
        f"{prefix}_entropy": entropy_share_cudf(s),
        f"{prefix}_theil": theil_share_cudf(s),
        f"{prefix}_top1_share": top_share_cudf(s, 0.01),
        f"{prefix}_top5_share": top_share_cudf(s, 0.05),
        f"{prefix}_top10_share": top_share_cudf(s, 0.10),
        f"{prefix}_max_share": top_share_cudf(s, 1.0 / max(1, len(s))),
    }


# ----------------------------
# I/O: read parquet for a window
# ----------------------------
def read_window_parquet(cudf, parquet_root, company, start_ts, end_ts, timestamp_col) -> Optional[Any]:
    start_py = pd.Timestamp(start_ts).to_pydatetime()
    end_py = pd.Timestamp(end_ts).to_pydatetime()

    files = []
    for y, m in month_iter(start_py, end_py):
        patt = os.path.join(parquet_root, f"company={company}", f"year={y}", f"month={m}", "*.parquet")
        files.extend(glob.glob(patt))
    if not files:
        return None

    df = cudf.read_parquet(files)
    df = df[(df[timestamp_col] >= start_ts) & (df[timestamp_col] <= end_ts)]
    return df


def floor_ts_cudf(ts, diff_bin):
    """
    Floor a cuDF datetime64[ns] Series to a multiple of diff_bin like '10m', '5h', '1d'.
    Fully GPU-compatible and avoids TypeErrors from datetime64 + TimeDeltaColumn.

    Parameters:
        ts (cudf.Series): datetime64[ns] Series
        diff_bin (str): e.g., '10m', '5h', '1d'

    Returns:
        cudf.Series: floored datetime64[ns] Series
    """
    if not isinstance(ts, cudf.Series):
        raise TypeError("ts must be a cudf.Series of datetime64[ns]")

    # Parse diff_bin
    m = re.match(r"(\d+)([smhdSMHD])", diff_bin)
    if m is None:
        raise ValueError(f"Invalid diff_bin: {diff_bin}")

    n, unit = int(m.group(1)), m.group(2).lower()
    unit_seconds = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    if unit not in unit_seconds:
        raise ValueError(f"Unsupported unit in diff_bin: {unit}")

    delta_sec = n * unit_seconds[unit]

    # Use cuDF datetime Series as origin (min timestamp)
    t0_series = cudf.Series([ts.min()] * len(ts))

    # Difference in seconds from t0
    ts_diff_sec = (ts - t0_series).astype("timedelta64[s]").astype("int64")

    # Floor to nearest multiple of delta_sec
    ts_floored_sec = (ts_diff_sec // delta_sec) * delta_sec

    # Convert back to timedelta64[ns] Series and add t0_series
    ts_floored = t0_series + cudf.Series(ts_floored_sec * 1_000_000_000, dtype="timedelta64[ns]")

    return ts_floored

def floor_cudf_series(ts, diff_bin):
    """
    Floor a cuDF datetime Series to a multiple of diff_bin like '10m', '5h', '1d'.
    """
    if not isinstance(ts, cudf.Series):
        raise TypeError("ts must be a cudf.Series")

    # Parse diff_bin
    m = re.match(r"(\d+)([smhdSMHD])", diff_bin)
    if not m:
        raise ValueError(f"Invalid diff_bin: {diff_bin}")

    n, unit = int(m.group(1)), m.group(2).lower()
    unit_seconds = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if unit not in unit_seconds:
        raise ValueError(f"Unsupported unit in diff_bin: {unit}")

    delta_sec = n * unit_seconds[unit]

    # Use a series for the min timestamp as base
    t0_series = cudf.Series([ts.min()] * len(ts))

    # Difference from base in seconds
    ts_diff_sec = (ts - t0_series).astype("timedelta64[s]").astype("int64")

    # Floor
    ts_floored_sec = (ts_diff_sec // delta_sec) * delta_sec

    # Convert back to timedelta64[ns] and add base
    ts_floored = t0_series + cudf.Series(ts_floored_sec * 1_000_000_000, dtype="timedelta64[ns]")

    return ts_floored


# ----------------------------
# Diffusion / timing metrics
# ----------------------------
def diffusion_metrics(cudf, events, diff_bin: str, growth_window_hours: float) -> Dict[str, Any]:
    """
    events columns: src, dst, ts
    Computes:
      - time to reach 10/50/90% of: events, unique nodes, unique sources, unique targets
      - peak timing and post-peak half-life based on binned event counts
      - early growth rate (log cumulative events slope) in first X hours
    """
    out = {}
    if len(events) == 0:
        return {k: float("nan") for k in [
            "t10_hours","t50_hours","t90_hours",
            "nodes_t10_hours","nodes_t50_hours","nodes_t90_hours",
            "src_t10_hours","src_t50_hours","src_t90_hours",
            "dst_t10_hours","dst_t50_hours","dst_t90_hours",
            "time_to_peak_hours","post_peak_half_life_hours","early_log_cum_events_slope"
        ]}

    ev = events.sort_values("ts")
    t0 = ev["ts"].iloc[0]
    total_events = len(ev)

    # helper: time to reach fraction of cumulative series
    def time_to_frac(ts_series, frac):
        k = max(1, int(math.ceil(frac * len(ts_series))))
        return ts_series.iloc[k-1]

    # event t10/t50/t90
    t10 = time_to_frac(ev["ts"], 0.10)
    t50 = time_to_frac(ev["ts"], 0.50)
    t90 = time_to_frac(ev["ts"], 0.90)

    # FIX: replace .total_seconds() with numpy timedelta division
    out["t10_hours"] = float((t10 - t0) / np.timedelta64(1, 's') / 3600.0)
    out["t50_hours"] = float((t50 - t0) / np.timedelta64(1, 's') / 3600.0)
    out["t90_hours"] = float((t90 - t0) / np.timedelta64(1, 's') / 3600.0)

    # binned event counts
    tmp = ev[["src","dst","ts"]].copy()
    tmp["bin"] = floor_ts_cudf(tmp["ts"], diff_bin)
    binc = tmp.groupby("bin").size().reset_index().rename(columns={0:"n_events"})

    # peak timing
    peak_row = binc.sort_values("n_events", ascending=False).head(1)
    peak_t = peak_row["bin"].iloc[0]
    peak_n = int(peak_row["n_events"].iloc[0])
    out["time_to_peak_hours"] = float((peak_t - t0) / np.timedelta64(1, 's') / 3600.0)

    # post-peak half-life: first bin after peak where count <= half peak
    half = 0.5 * peak_n
    after = binc[binc["bin"] > peak_t].sort_values("bin")
    if len(after) == 0:
        out["post_peak_half_life_hours"] = float("nan")
    else:
        hit = after[after["n_events"] <= half]
        if len(hit) == 0:
            out["post_peak_half_life_hours"] = float("nan")
        else:
            t_half = hit["bin"].iloc[0]
            out["post_peak_half_life_hours"] = float((t_half - peak_t) / np.timedelta64(1, 's') / 3600.0)

    # adoption curves: unique nodes, unique sources, unique targets over bins
    # compute cumulative unique counts per bin by taking first appearance time per id
    def first_time(series_id, series_ts):
        g = cudf.DataFrame({"id": series_id, "ts": series_ts})
        g = g.sort_values("ts")
        first = g.groupby("id")["ts"].min().reset_index()
        return first

    src_first = first_time(ev["src"], ev["ts"])
    dst_first = first_time(ev["dst"], ev["ts"])

    # nodes = union(src,dst)
    all_ids = cudf.concat([ev["src"], ev["dst"]], ignore_index=True)
    all_ts = cudf.concat([ev["ts"], ev["ts"]], ignore_index=True)
    node_first = first_time(all_ids, all_ts)

    def times_for_first(first_df, prefix):
        first_df["bin"] = floor_cudf_series(first_df["ts"], diff_bin)
        cnt = first_df.groupby("bin").size().reset_index().rename(columns={0:"n_new"})
        cnt = cnt.sort_values("bin")
        cnt["cum"] = cnt["n_new"].cumsum()
        total = int(cnt["cum"].max()) if len(cnt) else 0
        if total <= 0:
            out[f"{prefix}_t10_hours"] = float("nan")
            out[f"{prefix}_t50_hours"] = float("nan")
            out[f"{prefix}_t90_hours"] = float("nan")
            return
        def t_at(frac):
            target = frac * total
            hit = cnt[cnt["cum"] >= target].head(1)
            t = hit["bin"].iloc[0]
            return float((t - t0) / np.timedelta64(1, 's') / 3600.0)
        out[f"{prefix}_t10_hours"] = t_at(0.10)
        out[f"{prefix}_t50_hours"] = t_at(0.50)
        out[f"{prefix}_t90_hours"] = t_at(0.90)

    times_for_first(node_first, "nodes")
    times_for_first(src_first, "src")
    times_for_first(dst_first, "dst")

    # early growth rate: slope of log(cum events) vs time (hours) in first growth_window_hours
    try:
        bw = binc.sort_values("bin")
        # FIX: replace .total_seconds()
        bw["t_hours"] = (bw["bin"] - t0) / np.timedelta64(1, 's') / 3600.0
        bw = bw[bw["t_hours"] <= float(growth_window_hours)]
        if len(bw) < 3:
            out["early_log_cum_events_slope"] = float("nan")
        else:
            bw["cum"] = bw["n_events"].cumsum().astype("float64")
            bw = bw[bw["cum"] > 0]
            if len(bw) < 3:
                out["early_log_cum_events_slope"] = float("nan")
            else:
                y = cp.log(bw["cum"]).astype("float64")
                x = bw["t_hours"].astype("float64")
                xmu = float(x.mean()); ymu = float(y.mean())
                cov = float(((x - xmu) * (y - ymu)).mean())
                var = float(((x - xmu) * (x - xmu)).mean())
                out["early_log_cum_events_slope"] = float(cov / var) if var > 0 else float("nan")
    except Exception:
        out["early_log_cum_events_slope"] = float("nan")

    return out


# ----------------------------
# Network construction helpers
# ----------------------------
def build_weighted_edges(events, drop_self_loops: bool):
    edges = events.groupby(["src", "dst"]).size().reset_index().rename(columns={0: "weight"})
    n_self = 0
    if drop_self_loops:
        n_self = int((edges["src"] == edges["dst"]).sum())
        edges = edges[edges["src"] != edges["dst"]]
    return edges, n_self


def apply_variant(edges, variant: str):
    if variant == "unweighted":
        e = edges.copy()
        e["weight"] = 1
        return e
    if variant.startswith("thr"):
        thr = int(variant.replace("thr", ""))
        return edges[edges["weight"] >= thr]
    return edges  # base


def freeman_centralization_from_degree(cudf, degree_series):
    # C = sum(max - deg_i) / ((n-1)(n-2)) for undirected or in/out in directed (common adaptation).
    d = degree_series.dropna().astype("float64")
    n = len(d)
    if n < 3:
        return float("nan")
    dmax = float(d.max())
    num = float((dmax - d).sum())
    denom = float((n - 1) * (n - 2))
    return float(num / denom) if denom > 0 else float("nan")


# ----------------------------
# Echo chamber metrics (community mixing)
# ----------------------------
def echo_chamber_metrics(cudf, edges_label, parts, total_weight: float) -> Dict[str, Any]:
    """
    edges_label: src,dst,weight (label space)
    parts: vertex, partition (from Louvain on undirected)
    We compute within/between weights, EI index, mixing entropy, concentration of community attention.
    """
    out = {}
    if len(edges_label) == 0 or len(parts) == 0 or total_weight <= 0:
        return {
            "within_comm_weight_share": float("nan"),
            "between_comm_weight_share": float("nan"),
            "EI_index_weighted": float("nan"),
            "mix_entropy_src_to_dst_comm": float("nan"),
            "comm_size_hhi": float("nan"),
            "comm_size_gini": float("nan"),
            "comm_size_entropy": float("nan"),
            "comm_attention_hhi": float("nan"),
            "comm_attention_gini": float("nan"),
            "comm_attention_entropy": float("nan"),
            "largest_comm_attention_share": float("nan"),
        }

    # attach community ids to src and dst
    p = parts.rename(columns={"vertex": "v", "partition": "c"})
    e = edges_label.merge(p, left_on="src", right_on="v", how="left").rename(columns={"c": "c_src"}).drop(columns=["v"])
    e = e.merge(p, left_on="dst", right_on="v", how="left").rename(columns={"c": "c_dst"}).drop(columns=["v"])

    e = e.dropna(subset=["c_src", "c_dst"])
    e["c_src"] = e["c_src"].astype("int32")
    e["c_dst"] = e["c_dst"].astype("int32")

    e["w"] = e["weight"].astype("float64")

    within = float(e[e["c_src"] == e["c_dst"]]["w"].sum())
    between = float(e[e["c_src"] != e["c_dst"]]["w"].sum())
    tot = float(within + between)

    out["within_comm_weight_share"] = within / tot if tot > 0 else float("nan")
    out["between_comm_weight_share"] = between / tot if tot > 0 else float("nan")
    out["EI_index_weighted"] = (between - within) / tot if tot > 0 else float("nan")

    # community size concentration
    comm_sizes = parts.groupby("partition").size().astype("float64")
    out["comm_size_hhi"] = hhi_cudf(comm_sizes)
    out["comm_size_gini"] = gini_cudf(cudf, comm_sizes)
    out["comm_size_entropy"] = entropy_share_cudf(comm_sizes)

    # community "attention" = total incoming weight staying within each community (or total within weight per comm)
    within_edges = e[e["c_src"] == e["c_dst"]]
    comm_attention = within_edges.groupby("c_src")["w"].sum().astype("float64")
    if len(comm_attention) == 0:
        out["comm_attention_hhi"] = float("nan")
        out["comm_attention_gini"] = float("nan")
        out["comm_attention_entropy"] = float("nan")
        out["largest_comm_attention_share"] = float("nan")
    else:
        out["comm_attention_hhi"] = hhi_cudf(comm_attention)
        out["comm_attention_gini"] = gini_cudf(cudf, comm_attention)
        out["comm_attention_entropy"] = entropy_share_cudf(comm_attention)
        out["largest_comm_attention_share"] = float(comm_attention.max() / comm_attention.sum())

    # mixing entropy: distribution of dst communities given src community, aggregated
    # Build mixing matrix weights
    mix = e.groupby(["c_src", "c_dst"])["w"].sum().reset_index()
    # Normalize row-wise and compute entropy per row, then average weighted by row mass
    row_sum = mix.groupby("c_src")["w"].sum().reset_index().rename(columns={"w": "row_w"})
    mix = mix.merge(row_sum, on="c_src", how="left")
    mix["p"] = (mix["w"] / mix["row_w"]).astype("float64")
    mix = mix[mix["p"] > 0]
    mix["h_piece"] = -(mix["p"] * cp.log(mix["p"]))
    row_h = mix.groupby("c_src")["h_piece"].sum().reset_index().rename(columns={"h_piece": "row_h"})
    row_h = row_h.merge(row_sum, on="c_src", how="left")
    out["mix_entropy_src_to_dst_comm"] = float((row_h["row_h"] * row_h["row_w"]).sum() / row_h["row_w"].sum()) if len(row_h) else float("nan")

    return out


# ----------------------------
# Core graph metrics per variant
# ----------------------------
def compute_variant_metrics(cudf, cugraph, edges_label, variant_name, outdir, save_node_tables, extra_centrality, errors):
    pref = f"{variant_name}__"
    out: Dict[str, Any] = {}

    if len(edges_label) == 0:
        out[pref + "n_nodes"] = 0
        return out
    # directed graph
    Gd = cugraph.Graph(directed=True)
    Gd.from_cudf_edgelist(edges_label, source="src", destination="dst", edge_attr="weight", renumber=True)
    n_nodes = int(Gd.number_of_vertices())
    total_weight = float(edges_label["weight"].sum()) if len(edges_label) else 0.0
    out[pref + "n_nodes"] = n_nodes
    out[pref + "edges_unique"] = int(len(edges_label))
    out[pref + "total_weight"] = float(total_weight)
    out[pref + "density"] = float(len(edges_label) / (n_nodes * (n_nodes - 1))) if n_nodes > 1 else float("nan")

    # degrees (unweighted) for centralization
    try:
        deg_df = Gd.degree(weight=None)  # unweighted
        indeg_u = deg_df[["vertex", "in_degree"]].rename(columns={"in_degree": "in_deg"})
        outdeg_u = deg_df[["vertex", "out_degree"]].rename(columns={"out_degree": "out_deg"})
        d_u = indeg_u.merge(outdeg_u, on="vertex", how="outer").fillna(0)
        out[pref + "in_deg_centralization"] = freeman_centralization_from_degree(cudf, d_u["in_deg"])
        out[pref + "out_deg_centralization"] = freeman_centralization_from_degree(cudf, d_u["out_deg"])
        if save_node_tables:
            d_u.to_parquet(os.path.join(outdir, f"{variant_name}_node_degree_unweighted.parquet"), index=False)
    except Exception as ex:
        errors[pref + "deg_centralization"] = repr(ex)

    # strengths (weighted degrees)
    try:
        deg_df = Gd.degree(weight="weight")  # weighted
        indeg = deg_df[["vertex", "in_degree"]].rename(columns={"in_degree": "in_strength"})
        outdeg = deg_df[["vertex", "out_degree"]].rename(columns={"out_degree": "out_strength"})
        deg = indeg.merge(outdeg, on="vertex", how="outer").fillna(0)
        in_s = deg["in_strength"].astype("float64")
        out_s = deg["out_strength"].astype("float64")

        out.update({pref + k: v for k, v in stats_pack_cudf(in_s, "in").items()})
        out.update({pref + k: v for k, v in stats_pack_cudf(out_s, "out").items()})
        out.update({pref + k: v for k, v in conc_pack_cudf(cudf, in_s, "in").items()})
        out.update({pref + k: v for k, v in conc_pack_cudf(cudf, out_s, "out").items()})

        out[pref + "in_zero_share"] = float((in_s == 0).mean())
        out[pref + "out_zero_share"] = float((out_s == 0).mean())
        out[pref + "check_sum_in_minus_total"] = float(in_s.sum()) - float(total_weight)
        out[pref + "check_sum_out_minus_total"] = float(out_s.sum()) - float(total_weight)

        if save_node_tables:
            deg.to_parquet(os.path.join(outdir, f"{variant_name}_node_strengths.parquet"), index=False)
    except Exception as ex:
        errors[pref + "strengths"] = repr(ex)

    # reciprocity in label space (unique edges)
    try:
        e = edges_label[["src","dst"]]
        mutual = e.merge(e.rename(columns={"src":"dst","dst":"src"}), on=["src","dst"], how="inner")
        out[pref + "reciprocity"] = float(len(mutual) / max(1, len(e)))
    except Exception as ex:
        errors[pref + "reciprocity"] = repr(ex)
        out[pref + "reciprocity"] = float("nan")

    # components
    try:
        wcc = cugraph.weakly_connected_components(Gd)
        sizes = wcc.groupby("labels").size().astype("float64")
        out[pref + "n_wcc"] = int(len(sizes))
        out[pref + "largest_wcc_share"] = float(sizes.max()/n_nodes) if n_nodes else float("nan")
        # fragmentation distribution measures
        out[pref + "wcc_size_hhi"] = hhi_cudf(sizes)
        out[pref + "wcc_size_gini"] = gini_cudf(cudf, sizes)
        out[pref + "wcc_size_entropy"] = entropy_share_cudf(sizes)
        out[pref + "wcc_top5_share"] = top_share_cudf(sizes, 5.0/max(1,len(sizes)))
    except Exception as ex:
        errors[pref + "wcc"] = repr(ex)

    try:
        scc = cugraph.strongly_connected_components(Gd)
        sizes = scc.groupby("labels").size().astype("float64")
        out[pref + "n_scc"] = int(len(sizes))
        out[pref + "largest_scc_share"] = float(sizes.max()/n_nodes) if n_nodes else float("nan")
        out[pref + "scc_size_hhi"] = hhi_cudf(sizes)
        out[pref + "scc_size_gini"] = gini_cudf(cudf, sizes)
        out[pref + "scc_size_entropy"] = entropy_share_cudf(sizes)
    except Exception as ex:
        errors[pref + "scc"] = repr(ex)

    # PageRank (influence)
    try:
        pr = cugraph.pagerank(Gd, weight="weight")
        v = pr["pagerank"].astype("float64")
        out.update({pref + k: v2 for k, v2 in stats_pack_cudf(v, "pagerank").items()})
        out.update({pref + k: v2 for k, v2 in conc_pack_cudf(cudf, v, "pagerank").items()})
        out[pref + "pagerank_sum"] = float(v.sum())
        if save_node_tables:
            pr.to_parquet(os.path.join(outdir, f"{variant_name}_pagerank.parquet"), index=False)
    except Exception as ex:
        errors[pref + "pagerank"] = repr(ex)

    # undirected projection for echo chambers / clustering / core / communities
    try:
        Gu = cugraph.Graph()
        Gu.from_cudf_edgelist(edges_label, source="src", destination="dst", edge_attr="weight", renumber=True)

        # Louvain communities
        parts = None
        try:
            parts, modularity = cugraph.louvain(Gu)
            out[pref + "modularity"] = safe_float(modularity)
            comm_sizes = parts.groupby("partition").size().astype("float64")
            out[pref + "n_communities"] = int(len(comm_sizes))
            out[pref + "comm_size_hhi"] = hhi_cudf(comm_sizes)
            out[pref + "comm_size_gini"] = gini_cudf(cudf, comm_sizes)
            out[pref + "comm_size_entropy"] = entropy_share_cudf(comm_sizes)
            out[pref + "largest_comm_share"] = float(comm_sizes.max()/n_nodes) if n_nodes else float("nan")
            if save_node_tables:
                parts.to_parquet(os.path.join(outdir, f"{variant_name}_communities.parquet"), index=False)
        except Exception as ex:
            errors[pref + "louvain"] = repr(ex)

        # echo chamber metrics (need parts in renumbered space, edges in renumbered space!)
        # IMPORTANT: We have edges_label in label space, but Gu/Gd are renumbered internally.
        # However, cugraph.louvain returns partitions in the renumbered vertex space consistent with Gu.
        # To align, we must also use edges in the renumbered vertex space. Easiest: rebuild edges in renumbered space.
        # cuGraph doesn't expose mapping directly from Graph object cleanly across versions; so we compute echo metrics
        # using the partitions by joining on "vertex" computed from Graph renumbering on a NEW edgelist build.
        #
        # Practical workaround: compute echo metrics in renumbered space by rebuilding an undirected graph from edges_label
        # and using the partition + triangle/degree outputs which are also in renumbered space.
        #
        # We'll approximate echo metrics using the SAME renumbered vertex IDs by:
        #   - creating a temporary graph on edges_label (as above),
        #   - getting its edgelist back is not always supported across versions.
        # So instead, we compute within/between weight using a merge between partitions and a renumbered edgelist we create:
        #
        # Use cugraph.utilities.renumbering is version dependent, so we do a safe approach:
        # Rebuild a DiGraph with renumber=True and request a renumbered edgelist via internal API is risky.
        #
        # Therefore: we compute echo metrics in LABEL SPACE using LABEL-SPACE communities is not available from louvain.
        # Solution: compute echo metrics using label-space communities via a CPU algorithm is too slow.
        #
        # So: we compute echo metrics using renumbered edges by doing louvain on a graph built from a renumbered edgelist
        # that we create ourselves via a cudf factorization (stable and version-agnostic).
        #
        # That’s implemented below.

        # core number (cohesion)
        try:
            core = cugraph.core_number(Gu)
            out[pref + "max_core"] = float(core["core_number"].max()) if len(core) else float("nan")
            for k in range(2, 11):
                out[pref + f"core_size_k{k}"] = int((core["core_number"] >= k).sum())
            if save_node_tables:
                core.to_parquet(os.path.join(outdir, f"{variant_name}_core_number.parquet"), index=False)
        except Exception as ex:
            errors[pref + "core_number"] = repr(ex)

        # triangles / clustering
        try:
            tri = cugraph.triangle_count(Gu)
            deg_u = cugraph.degree(Gu).rename(columns={"degree":"deg"})
            tmp = deg_u.merge(tri, on="vertex", how="left").fillna(0)
            d = tmp["deg"].astype("float64")
            t = tmp["triangle_count"].astype("float64")
            triplets = float((d*(d-1.0)/2.0).sum())
            total_tri = float(t.sum()/3.0)
            out[pref + "total_triangles"] = total_tri
            out[pref + "transitivity"] = float((3.0*total_tri/triplets) if triplets > 0 else float("nan"))
            denom = d*(d-1.0)
            local = cudf.Series([0.0]*len(tmp), dtype="float64")
            mask = denom > 0
            local[mask] = (2.0*t[mask]) / denom[mask]
            out[pref + "avg_clustering"] = float(local.mean()) if len(local) else float("nan")
            # fragmentation proxy: leaf share (degree==1) in undirected
            out[pref + "leaf_share_undirected"] = float((d == 1).mean()) if len(d) else float("nan")
            if save_node_tables:
                tmp.to_parquet(os.path.join(outdir, f"{variant_name}_deg_triangles.parquet"), index=False)
        except Exception as ex:
            errors[pref + "clustering"] = repr(ex)

        # OPTIONAL extra centrality (heavy, version dependent)
        if extra_centrality:
            try:
                # eigenvector
                evc = cugraph.eigenvector_centrality(Gu, weight="weight")
                v = evc["eigenvector_centrality"].astype("float64")
                out.update({pref + "evec_" + k: v2 for k, v2 in stats_pack_cudf(v, "").items() if k != "_mean"})  # keep light
                out[pref + "evec_gini"] = gini_cudf(cudf, v)
                out[pref + "evec_hhi"] = hhi_cudf(v)
                if save_node_tables:
                    evc.to_parquet(os.path.join(outdir, f"{variant_name}_eigenvector.parquet"), index=False)
            except Exception as ex:
                errors[pref + "eigenvector"] = repr(ex)

            try:
                bc = cugraph.betweenness_centrality(Gu, normalized=True)
                v = bc["betweenness_centrality"].astype("float64")
                out[pref + "betweenness_gini"] = gini_cudf(cudf, v)
                out[pref + "betweenness_hhi"] = hhi_cudf(v)
                if save_node_tables:
                    bc.to_parquet(os.path.join(outdir, f"{variant_name}_betweenness.parquet"), index=False)
            except Exception as ex:
                errors[pref + "betweenness"] = repr(ex)

            try:
                cc = cugraph.closeness_centrality(Gu)
                v = cc["closeness_centrality"].astype("float64")
                out[pref + "closeness_gini"] = gini_cudf(cudf, v)
                out[pref + "closeness_hhi"] = hhi_cudf(v)
                if save_node_tables:
                    cc.to_parquet(os.path.join(outdir, f"{variant_name}_closeness.parquet"), index=False)
            except Exception as ex:
                errors[pref + "closeness"] = repr(ex)

    except Exception as ex:
        errors[pref + "undirected_block"] = repr(ex)

    # Echo chamber block (version-agnostic): compute communities + mixing using our own factorization
    try:
        # Factorize all unique nodes to integer ids
        nodes = cudf.concat([edges_label["src"], edges_label["dst"]], ignore_index=True)
        codes, uniques = nodes.factorize()  # codes length 2m, uniques length n
        m = len(edges_label)
        src_code = codes[:m]
        dst_code = codes[m:]

        e_ren = cudf.DataFrame({"src": src_code, "dst": dst_code, "weight": edges_label["weight"].astype("int64")})
        # undirected graph on these integer ids
        Gu2 = cugraph.Graph()
        Gu2.from_cudf_edgelist(e_ren, source="src", destination="dst", edge_attr="weight", renumber=False)

        parts2, modularity2 = cugraph.louvain(Gu2)
        out[pref + "modularity_factorized"] = safe_float(modularity2)

        echo = echo_chamber_metrics(cudf, e_ren, parts2, float(e_ren["weight"].sum()))
        out.update({pref + "echo_" + k: v for k, v in echo.items()})

        if save_node_tables:
            parts2.to_parquet(os.path.join(outdir, f"{variant_name}_communities_factorized.parquet"), index=False)

    except Exception as ex:
        errors[pref + "echo_factorized"] = repr(ex)

    return out


# ----------------------------
# Validation checks
# ----------------------------
def validate_variant(summary: Dict[str, Any], variant: str, tol: float) -> Tuple[bool, Dict[str, Any]]:
    pref = f"{variant}__"
    rep = {"variant": variant, "checks": {}}
    ok = True

    def chk(name, cond, details=None):
        nonlocal ok
        rep["checks"][name] = bool(cond)
        if details is not None:
            rep["checks"][name + "_details"] = details
        if not cond:
            ok = False

    tw = summary.get(pref + "total_weight", float("nan"))
    d_in = summary.get(pref + "check_sum_in_minus_total", float("nan"))
    d_out = summary.get(pref + "check_sum_out_minus_total", float("nan"))

    if not math.isnan(d_in) and not math.isnan(tw):
        chk("sum_in_matches_total", abs(float(d_in)) <= tol * max(1.0, float(tw)), {"diff": d_in, "tw": tw})
    if not math.isnan(d_out) and not math.isnan(tw):
        chk("sum_out_matches_total", abs(float(d_out)) <= tol * max(1.0, float(tw)), {"diff": d_out, "tw": tw})

    dens = summary.get(pref + "density", float("nan"))
    if not math.isnan(dens):
        chk("density_in_0_1", (-1e-12 <= dens <= 1.0 + 1e-12), {"density": dens})

    prsum = summary.get(pref + "pagerank_sum", float("nan"))
    if not math.isnan(prsum):
        chk("pagerank_sum_near_1", abs(float(prsum) - 1.0) <= 1e-3, {"pagerank_sum": prsum})

    rep["ok"] = ok
    return ok, rep


# ----------------------------
# Per-window compute
# ----------------------------
def compute_one_window(cudf, cugraph, args, company, start_str, end_str, window_id, stop_flag):
    if not window_id:
        window_id = f"{company}_{start_str.replace(':','').replace(' ','T')}_{end_str.replace(':','').replace(' ','T')}"
    outdir = os.path.join(args.outroot, f"company={company}", window_id)
    os.makedirs(outdir, exist_ok=True)

    summary_path = os.path.join(outdir, "summary.json")
    errors_path = os.path.join(outdir, "errors.json")
    validation_path = os.path.join(outdir, "validation.json")

    if args.skip_existing and os.path.exists(summary_path):
        return

    summary: Dict[str, Any] = {
        "company": company,
        "window_id": window_id,
        "start_time": start_str,
        "end_time": end_str,
        "variants": args.variants,
        "diff_bin": args.diff_bin,
        "growth_window_hours": args.growth_window_hours,
    }
    errors: Dict[str, str] = {}
    validations = []

    try:
        start_ts = cudf.to_datetime(start_str)
        end_ts = normalize_end_of_day_cudf(cudf, cudf.to_datetime(end_str))

        df = read_window_parquet(cudf, args.parquet_root, company, start_ts, end_ts, args.timestamp_col)
        if df is None or len(df) == 0:
            summary["n_retweet_events"] = 0
            raise RuntimeError("No events found in window.")

        events = df.rename(columns={
            args.src_col: "src",
            args.dst_col: "dst",
            args.timestamp_col: "ts"
        })[["src","dst","ts"]]

        summary["n_retweet_events"] = int(len(events))

        # diffusion / speed metrics
        summary.update(diffusion_metrics(cudf, events, args.diff_bin, args.growth_window_hours))

        # weighted edges
        edges_base, n_self = build_weighted_edges(events, args.drop_self_loops)
        summary["n_self_loops_removed"] = int(n_self)

        # edge weight stats
        try:
            w = edges_base["weight"].astype("float64")
            summary.update(stats_pack_cudf(w, "edge_w"))
            summary.update(conc_pack_cudf(cudf, w, "edge_w"))
        except Exception as ex:
            errors["edge_weight_stats"] = repr(ex)

        # save base edges
        edges_base.to_parquet(os.path.join(outdir, "weighted_edges.parquet"), index=False)

        variants = [v.strip() for v in args.variants.split(",") if v.strip()]
        if "base" not in variants:
            variants = ["base"] + variants

        for vname in variants:
            if args.fail_fast_global and stop_flag.is_set():
                break

            evar = apply_variant(edges_base, vname)

            # Compute variant graph metrics (dominance, fragmentation, echo chambers, influence)
            vm = compute_variant_metrics(
                cudf=cudf,
                cugraph=cugraph,
                edges_label=evar.rename(columns={"src":"src","dst":"dst","weight":"weight"}),
                variant_name=vname,
                outdir=outdir,
                save_node_tables=args.save_node_tables,
                extra_centrality=args.extra_centrality,
                errors=errors,
            )
            summary.update(vm)

            ok, rep = validate_variant(summary, vname, args.validation_tol)
            validations.append(rep)

            if vname == "base":
                summary["base_validation_ok"] = bool(ok)
                if not ok:
                    if args.fail_fast_window:
                        errors["fail_fast_window"] = "Base validation failed; stopped remaining variants for this window."
                        break
                    if args.fail_fast_global:
                        errors["fail_fast_global"] = "Base validation failed; stopping all workers."
                        stop_flag.set()
                        break

        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        with open(errors_path, "w") as f:
            json.dump(errors, f, indent=2)
        with open(validation_path, "w") as f:
            json.dump(validations, f, indent=2)

    except Exception as ex:
        errors["fatal"] = f"{repr(ex)}\n{traceback.format_exc()}"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        with open(errors_path, "w") as f:
            json.dump(errors, f, indent=2)
        with open(validation_path, "w") as f:
            json.dump(validations, f, indent=2)


# ----------------------------
# Worker
# ----------------------------
def worker_main(gpu_id, q, args, stop_flag):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    import cudf  # noqa
    import cugraph  # noqa

    while True:
        if args.fail_fast_global and stop_flag.is_set():
            break
        task = q.get()
        if task is None:
            break
        company, start_str, end_str, window_id = task
        compute_one_window(cudf, cugraph, args, company, start_str, end_str, window_id, stop_flag)


# ----------------------------
# Main
# ----------------------------
def main():
    args = parse_args()
    os.makedirs(args.outroot, exist_ok=True)

    ctx = get_context("spawn")
    q = ctx.Queue(maxsize=args.queue_max)
    stop_flag = ctx.Event()

    procs = []
    for gpu_id in range(args.ngpus):
        p = ctx.Process(target=worker_main, args=(gpu_id, q, args, stop_flag), daemon=True)
        p.start()
        procs.append(p)

    count = 0
    with open(args.windows_file, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            company = row["company"].strip()
            start_str = row["start"].strip()
            end_str = row["end"].strip()
            window_id = row.get("window_id", "").strip()

            q.put((company, start_str, end_str, window_id))
            count += 1
            if args.max_tasks and count >= args.max_tasks:
                break
            if args.fail_fast_global and stop_flag.is_set():
                break

    for _ in range(args.ngpus):
        q.put(None)

    for p in procs:
        p.join()

    print("DONE. Outputs under:", args.outroot)


if __name__ == "__main__":
    main()