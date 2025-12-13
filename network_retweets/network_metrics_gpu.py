import argparse
import cudf
import cugraph
import cupy as cp
from collections import defaultdict

# -------------------------------------------------
# Argument parsing
# -------------------------------------------------
parser = argparse.ArgumentParser(description="GPU network metrics by year")
parser.add_argument("--year", type=int, required=True, help="Year of the retweet network CSV")
args = parser.parse_args()

year = args.year

# -------------------------------------------------
# 1. Load CSV on GPU (NO HEADER)
# -------------------------------------------------
file_path = f"retweet_network{year}.csv"
columns = ["screen_name4", "user_screen_name", "edgeB", "tweetyear", "tweetmonth", "EST"]

df = cudf.read_csv(
    file_path,
    names=columns,
    dtype={
        "screen_name4": "str",
        "user_screen_name": "str",
        "edgeB": "str",
        "tweetyear": "int32",
        "tweetmonth": "int32",
        "EST": "str"
    },
    parse_dates=["EST"]
)

# Drop rows with missing users
df = df.dropna(subset=["user_screen_name", "edgeB"])
edges_df = df.rename(columns={"user_screen_name": "src", "edgeB": "dst"})

# -------------------------------------------------
# 2. Build GPU directed graph
# -------------------------------------------------
G = cugraph.Graph(directed=True)
G.from_cudf_edgelist(
    edges_df,
    source="src",
    destination="dst",
    renumber=True,
    store_transposed=True  # optimal for PageRank
)

# -------------------------------------------------
# 3. CENTRALITY METRICS (GPU)
# -------------------------------------------------
# In-degree centrality
in_degree = G.in_degree()
in_degree["in_degree_centrality"] = in_degree["degree"] / (G.number_of_nodes() - 1)
in_degree = in_degree.drop(columns="degree")

# Out-degree centrality
out_degree = G.out_degree()
out_degree["out_degree_centrality"] = out_degree["degree"] / (G.number_of_nodes() - 1)
out_degree = out_degree.drop(columns="degree")

# Approximate betweenness centrality (GPU)
k = 1000  # number of sampled vertices
betweenness = cugraph.betweenness_centrality(G, k=k, normalized=True)

# PageRank
pagerank = cugraph.pagerank(G)

# -------------------------------------------------
# 4. CLUSTERING COEFFICIENT (GPU-safe approximation)
# -------------------------------------------------
G_undirected = G.to_undirected()

try:
    # Attempt GPU triangle counts (requires cuGraph >= 23.04)
    triangles_df = cugraph.triangles(G_undirected)  # columns: ["vertex", "count"]
    degrees_df = G_undirected.degree()  # columns: ["vertex", "degree"]
    clustering_df = triangles_df.merge(degrees_df, on="vertex")
    clustering_df["clustering_coefficient"] = (
        2 * clustering_df["count"] / (clustering_df["degree"] * (clustering_df["degree"] - 1))
    )
    clustering_df = clustering_df.fillna(0)
except AttributeError:
    # Fallback: GPU-friendly approximate clustering
    edges = G_undirected.view_edge_list()[["src", "dst"]]
    # Build adjacency dictionary (on CPU but lightweight)
    adj = defaultdict(set)
    srcs = edges["src"].to_pandas()
    dsts = edges["dst"].to_pandas()
    for s, d in zip(srcs, dsts):
        adj[s].add(d)
        adj[d].add(s)

    # Compute approximate clustering (sampling all nodes sequentially)
    vertices = list(adj.keys())
    clustering_values = []
    for v in vertices:
        neighbors = adj[v]
        if len(neighbors) < 2:
            clustering_values.append(0.0)
            continue
        links = sum(1 for u in neighbors for w in neighbors if u != w and w in adj[u]) / 2
        clustering_values.append(links / (len(neighbors) * (len(neighbors) - 1) / 2))
    import cudf
    clustering_df = cudf.DataFrame({"vertex": vertices, "clustering_coefficient": clustering_values})

# -------------------------------------------------
# 5. NETWORK DENSITY
# -------------------------------------------------
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
network_density = num_edges / (num_nodes * (num_nodes - 1))

# -------------------------------------------------
# 6. SAVE RESULTS
# -------------------------------------------------
in_degree.to_csv(f"./output/{year}/in_degree_centrality_{year}.csv", index=False)
out_degree.to_csv(f"./output/{year}/out_degree_centrality_{year}.csv", index=False)
betweenness.to_csv(f"./output/{year}/betweenness_centrality_{year}.csv", index=False)
pagerank.to_csv(f"./output/{year}/pagerank_{year}.csv", index=False)
clustering_df.to_csv(f"./output/{year}/clustering_coefficients_{year}.csv", index=False)

with open(f"./output/{year}/network_density_{year}.txt", "w") as f:
    f.write(f"Network density: {network_density}\n")

print("GPU network analysis completed successfully.")
