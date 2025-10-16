# GPU Graph Toolkit — RAPIDS/cuGraph + optional DGL handoff
# ---------------------------------------------------------
# pip/conda (example):
#   conda create -n rapids-24 python=3.10 -y
#   conda install -c rapidsai -c conda-forge -c nvidia rapids=24.06 cudatoolkit=12.2 -y
#   pip install torch dgl-cu12  # pick wheels matching your CUDA / OS

import math
import cupy as cp
import cudf
import cugraph
from cugraph.utilities import ensure_cupy_array

# -----------------------------
# I/O & Graph construction
# -----------------------------
def load_edgelist_to_graph(path, directed=False, weighted=False, src="src", dst="dst", w="weight"):
    """
    Reads CSV/Parquet into cuDF and builds a cuGraph Graph.
    """
    if path.endswith((".parquet", ".pq")):
        df = cudf.read_parquet(path)
    else:
        df = cudf.read_csv(path)

    if not weighted or w not in df.columns:
        G = cugraph.Graph(directed=directed)
        G.from_cudf_edgelist(df, source=src, destination=dst, renumber=True)
    else:
        G = cugraph.Graph(directed=directed)
        G.from_cudf_edgelist(df, source=src, destination=dst, edge_attr=w, renumber=True)

    return G, df

# -----------------------------
# Centralities & Pagerank
# -----------------------------
def compute_centralities(G, k_betw_approx=None, alpha_katz=0.1, max_iter=100, tol=1e-6):
    """
    Returns a dict of DataFrames keyed by metric name, each with ['vertex', 'value'].
    - k_betw_approx: if set (e.g., 32 or 128), uses sampling for betweenness (much faster)
    """
    results = {}

    # Degree (undirected graph: degree; directed: in/out + total)
    deg = cugraph.degree(G)
    deg = deg.rename({"degree": "value"})
    results["degree"] = deg

    try:
        bc = cugraph.betweenness_centrality(G, k=k_betw_approx, normalized=True)
        bc = bc.rename({"betweenness_centrality": "value"})
        results["betweenness"] = bc
    except Exception as e:
        results["betweenness_error"] = str(e)

    try:
        ev = cugraph.eigenvector_centrality(G, max_iter=max_iter, tol=tol)
        ev = ev.rename({"eigenvector_centrality": "value"})
        results["eigenvector"] = ev
    except Exception as e:
        results["eigenvector_error"] = str(e)

    try:
        katz = cugraph.katz_centrality(G, alpha=alpha_katz, max_iter=max_iter, tol=tol, normalized=True)
        katz = katz.rename({"katz_centrality": "value"})
        results["katz"] = katz
    except Exception as e:
        results["katz_error"] = str(e)

    try:
        pr = cugraph.pagerank(G, max_iter=max_iter, tol=tol)
        pr = pr.rename({"pagerank": "value"})
        results["pagerank"] = pr
    except Exception as e:
        results["pagerank_error"] = str(e)

    return results

# -----------------------------
# Triangles & Clustering
# -----------------------------
def clustering_coefficients(G):
    """
    Computes global and local clustering coefficients using triangle counts.
    - Global C = 3*T / (# of connected triplets)
    - Local C_i = (2*T_i)/(k_i*(k_i-1))
    Returns: dict with {'global': float, 'local_df': DataFrame(vertex, clustering)}
    """
    # Triangle counts
    # Some RAPIDS versions expose 'triangle_count' (global) and 'triangles' (per-vertex).
    T_global = cugraph.triangle_count(G)

    deg = cugraph.degree(G).rename({"degree": "k"})
    deg["k_choose_2"] = (deg["k"] * (deg["k"] - 1)) / 2.0
    total_triplets = float(deg["k_choose_2"].sum())

    global_C = float( (3.0 * T_global) / total_triplets ) if total_triplets > 0 else 0.0

    # Per-vertex triangles if available; if not, approximate via k-core/triad sampling (optional)
    local_df = None
    try:
        tri_v = cugraph.triangles(G)  # returns per-vertex triangle counts in recent releases
        # Local clustering: 2*T_i / (k_i*(k_i-1))
        tri_v = tri_v.merge(deg, on="vertex", how="left")
        tri_v["clustering"] = cp.where(tri_v["k"] > 1, (2.0 * tri_v["triangles"]) / (tri_v["k"] * (tri_v["k"] - 1)), 0.0)
        local_df = tri_v[["vertex", "clustering"]]
    except Exception as e:
        # If per-vertex triangles not available, return None but keep global.
        local_df = cudf.DataFrame({"vertex": deg["vertex"], "clustering": cp.nan})
        local_df["note"] = "per-vertex triangle counts not available in this cuGraph build"

    return {"global": global_C, "local_df": local_df}

# -----------------------------
# Approximate diameter
# -----------------------------
def approximate_diameter(G, num_sources=64, use_double_sweep=True):
    """
    Approximates graph diameter (max shortest-path distance) using:
    - multi-source BFS sampling
    - optional double-sweep heuristic
    Returns: dict with {'approx_diameter': int, 'eccentricities': DataFrame}
    """
    verts = cugraph.utilities.utils.get_two_hop_neighbors(G)[0]  # quick way to touch renumbered verts
    # If above feels brittle, fallback:
    if verts is None or len(verts) == 0:
        verts = cugraph.degree(G)[["vertex"]]
    verts = verts["vertex"]

    # sample sources
    n = len(verts)
    idx = cp.random.permutation(n)[:min(num_sources, n)]
    sources = verts.take(idx)

    max_dist = 0
    ecc = []

    for s in sources.to_pandas().values:  # small loop over sources
        bfs_df = cugraph.bfs(G, start=s, return_predecessors=False)
        ecc_s = int(bfs_df["distance"].max())
        ecc.append((s, ecc_s))
        if ecc_s > max_dist:
            max_dist = ecc_s
            far = int(bfs_df.sort_values("distance", ascending=False)["vertex"].iloc[0])

    if use_double_sweep and n > 0:
        # BFS from farthest discovered node; often sharpens the bound
        bfs_df2 = cugraph.bfs(G, start=far, return_predecessors=False)
        max_dist = max(max_dist, int(bfs_df2["distance"].max()))
        ecc.append((far, int(bfs_df2["distance"].max())))

    ecc_df = cudf.DataFrame(ecc, columns=["vertex", "eccentricity"])
    return {"approx_diameter": int(max_dist), "eccentricities": ecc_df}

# -----------------------------
# Community detection & conductance
# -----------------------------
def louvain_partition(G, resolution=1.0, max_iter=100):
    parts, _ = cugraph.louvain(G, resolution=resolution, max_iter=max_iter)
    parts = parts.rename({"partition": "community"})
    return parts  # columns: vertex, community

def leiden_partition(G, resolution=1.0, max_iter=100):
    parts = cugraph.leiden(G, resolution=resolution, max_iter=max_iter)
    parts = parts.rename({"partition": "community"})
    return parts

def conductance_from_partition(G, parts):
    """
    Computes conductance phi(S) = cut(S,~S) / min(vol(S), vol(~S)) for each community S.
    Returns a DF with community-level conductance and a scalar 'best' (min) conductance.
    Notes:
      - For weighted graphs, replace degree by weighted degree (strength).
    """
    # Build edge list (renumbered ids)
    el = cugraph.to_cudf_edgelist(G)
    el = el.rename({"src": "u", "dst": "v"})

    # attach community labels
    parts = parts[["vertex", "community"]]
    el = el.merge(parts, left_on="u", right_on="vertex", how="left").drop(columns=["vertex"])
    el = el.merge(parts, left_on="v", right_on="vertex", how="left", suffixes=("_u", "_v")).drop(columns=["vertex"])

    # cut edges: community differs
    cut_flag = (el["community_u"] != el["community_v"]).astype("int8")
    # volume: use degree as volume proxy
    deg = cugraph.degree(G).rename({"degree": "deg"})
    vol = deg.merge(parts, on="vertex", how="left").groupby("community")["deg"].sum()

    # cut size per community: count edges incident to community crossing the cut
    # Each cut edge contributes 1 to each side's cut volume.
    cut_u = el[cut_flag == 1].groupby("community_u").size().rename("cut_incident")
    cut_v = el[cut_flag == 1].groupby("community_v").size().rename("cut_incident")
    cut_by_comm = cudf.concat([cut_u, cut_v], axis=0).groupby(level=0).sum()

    # align
    df = cudf.DataFrame({"community": vol.index})
    df["vol"] = vol.values
    df = df.merge(cut_by_comm.reset_index().rename(columns={"index": "community"}), on="community", how="left")
    df["cut_incident"] = df["cut_incident"].fillna(0)

    # total volume (sum of degrees)
    total_vol = float(vol.sum())
    df["vol_comp"] = total_vol - df["vol"]
    df["phi"] = df["cut_incident"] / df[["vol", "vol_comp"]].min(axis=1)
    df = df.sort_values("phi")

    best_phi = float(df["phi"].min()) if len(df) else math.nan
    return {"by_community": df, "best_conductance": best_phi}

# -----------------------------
# Robustness / resilience sims
# -----------------------------
def induced_subgraph_edges(edge_df, keep_vertices_set, src="src", dst="dst"):
    """
    Filter edges to keep only those with both endpoints in keep_vertices_set (cuDF Series).
    Returns filtered cuDF edge list.
    """
    tmp = edge_df.merge(keep_vertices_set.rename("keep"), left_on=src, right_index=True, how="left")
    tmp = tmp[tmp["keep"].notnull()].drop(columns=["keep"])
    tmp = tmp.merge(keep_vertices_set.rename("keep"), left_on=dst, right_index=True, how="left")
    tmp = tmp[tmp["keep"].notnull()].drop(columns=["keep"])
    return tmp

def simulate_removals(G, edge_df=None, mode="random", by="degree", steps=10, directed=False):
    """
    Simulates node removal and tracks:
      - giant component size
      - approx diameter
      - global clustering coefficient
    mode:
      - "random": remove random fraction each step
      - "targeted": remove highest-by 'by' (e.g., 'degree' or 'betweenness')
    """
    if edge_df is None:
        edge_df = cugraph.to_cudf_edgelist(G).rename(columns={"src":"src","dst":"dst"})

    # ranking for targeted removal
    base_rank = None
    if mode == "targeted":
        if by == "degree":
            base_rank = cugraph.degree(G).rename({"degree":"score"})
        elif by == "betweenness":
            base_rank = cugraph.betweenness_centrality(G, k=64).rename({"betweenness_centrality":"score"})
        else:
            raise ValueError("Unsupported 'by' for targeted mode. Use 'degree' or 'betweenness'.")

        base_rank = base_rank.sort_values("score", ascending=False)["vertex"].reset_index(drop=True)

    # all vertices
    V_all = cugraph.degree(G)["vertex"].sort_values().reset_index(drop=True)
    n = int(len(V_all))
    results = []

    for i in range(1, steps + 1):
        frac = i / steps
        remove_k = int(frac * n)

        if mode == "random":
            rm_idx = cp.random.permutation(n)[:remove_k]
            removed = V_all.take(rm_idx)
        else:
            removed = base_rank.iloc[:remove_k]

        keep = V_all.to_frame(name="vertex")
        keep = keep.merge(cudf.DataFrame({"vertex": removed}), on="vertex", how="left", indicator=True)
        keep = keep[keep["_merge"] == "left_only"][["vertex"]].set_index("vertex")

        sub_edges = induced_subgraph_edges(edge_df, keep.index, src="src", dst="dst")
        subG = cugraph.Graph(directed=directed)
        if len(sub_edges) == 0:
            results.append({"step": i, "frac_removed": frac, "n_left": int(n - remove_k),
                            "giant_comp": 0, "approx_diam": math.nan, "C_global": math.nan})
            continue
        subG.from_cudf_edgelist(sub_edges, source="src", destination="dst", renumber=True)

        # giant component size
        comps = cugraph.connected_components(subG) if not directed else cugraph.weakly_connected_components(subG)
        gc_size = int(comps["component"].value_counts().max())

        # approx diameter & clustering
        diam = approximate_diameter(subG, num_sources=16, use_double_sweep=True)["approx_diameter"]
        Cg = clustering_coefficients(subG)["global"]

        results.append({"step": i, "frac_removed": frac, "n_left": int(n - remove_k),
                        "giant_comp": gc_size, "approx_diam": int(diam), "C_global": float(Cg)})

    return cudf.DataFrame(results)

# -----------------------------
# Optional: DGL handoff
# -----------------------------
def to_dgl_graph(G):
    """
    Converts cuGraph to a DGLGraph on GPU.
    (Moves edge list -> CuPy -> Torch CUDA tensors -> DGLGraph)
    """
    import torch
    import dgl

    el = cugraph.to_cudf_edgelist(G).rename(columns={"src":"src","dst":"dst"})
    src = torch.utils.dlpack.from_dlpack(ensure_cupy_array(el["src"]).toDlpack()).cuda()
    dst = torch.utils.dlpack.from_dlpack(ensure_cupy_array(el["dst"]).toDlpack()).cuda()
    g = dgl.graph((src, dst), num_nodes=int(cugraph.number_of_vertices(G)), idtype=torch.int64, device="cuda")
    return g

# -----------------------------
# Minimal driver (example)
# -----------------------------
if __name__ == "__main__":
    # Example: replace with your path
    PATH = "edges.csv"   # columns: src,dst,(weight)
    G, edf = load_edgelist_to_graph(PATH, directed=False, weighted=False)

    # 1) Centralities
    cents = compute_centralities(G, k_betw_approx=64)
    print({k: (v.shape if isinstance(v, cudf.DataFrame) else v) for k, v in cents.items()})

    # 2) Clustering
    clust = clustering_coefficients(G)
    print("Global clustering:", clust["global"])

    # 3) Approx diameter
    diam = approximate_diameter(G, num_sources=64, use_double_sweep=True)
    print("Approx diameter:", diam["approx_diameter"])

    # 4) Conductance (Louvain)
    parts = louvain_partition(G)
    cond = conductance_from_partition(G, parts)
    print("Best conductance:", cond["best_conductance"])

    # 5) Robustness (random vs targeted-by-degree)
    rob_rand = simulate_removals(G, edge_df=edf, mode="random", steps=8)
    rob_deg  = simulate_removals(G, edge_df=edf, mode="targeted", by="degree", steps=8)
    print("Robustness (random):", rob_rand.head().to_pandas())
    print("Robustness (targeted-degree):", rob_deg.head().to_pandas())

    # 6) DGL handoff (optional)
    # dgl_g = to_dgl_graph(G)
    # print(dgl_g)
