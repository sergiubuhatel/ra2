import cudf
import cugraph

# -------------------------------------------------
# 1. Load CSV on GPU (NO HEADER)
# -------------------------------------------------
file_path = "retweet_network2017.csv"
columns = ["screen_name4", "user_screen_name", "edgeB", "tweetyear", "tweetmonth", "EST"]

df = cudf.read_csv(
    file_path,
    names=columns,
    dtype={"screen_name4": "str",
           "user_screen_name": "str",
           "edgeB": "str",
           "tweetyear": "int32",
           "tweetmonth": "int32",
           "EST": "str"},
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
# 4. CLUSTERING COEFFICIENT (GPU)
# -------------------------------------------------
G_undirected = G.to_undirected()

# Compute triangle counts per vertex (GPU)
# Note: triangles() requires recent cuGraph >=23.04
try:
    triangles_df = cugraph.triangles(G_undirected)  # columns: ["vertex", "count"]
except AttributeError:
    # If triangles() is not available, approximate using Python (slower, fallback)
    import pandas as pd
    from collections import defaultdict
    edges_gpu = G_undirected.view_edge_list()
    adj_dict = defaultdict(set)
    for s, d in zip(edges_gpu["src"].to_pandas(), edges_gpu["dst"].to_pandas()):
        adj_dict[s].add(d)
        adj_dict[d].add(s)
    def local_clustering(v):
        neighbors = adj_dict[v]
        if len(neighbors) < 2:
            return 0.0
        links = sum(1 for u in neighbors for w in neighbors if u != w and w in adj_dict[u]) / 2
        return links / (len(neighbors) * (len(neighbors) - 1) / 2)
    vertices = list(adj_dict.keys())
    clustering_values = [local_clustering(v) for v in vertices]
    clustering_df = pd.DataFrame({"vertex": vertices, "clustering_coefficient": clustering_values})
else:
    # Get degrees per vertex
    degrees_df = G_undirected.degree()  # columns: ["vertex", "degree"]

    # Merge triangle counts and degrees
    clustering_df = triangles_df.merge(degrees_df, on="vertex")

    # Compute clustering coefficient on GPU
    clustering_df["clustering_coefficient"] = (
        2 * clustering_df["count"] / (clustering_df["degree"] * (clustering_df["degree"] - 1))
    )
    clustering_df = clustering_df.fillna(0)

# -------------------------------------------------
# 5. NETWORK DENSITY
# -------------------------------------------------
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
network_density = num_edges / (num_nodes * (num_nodes - 1))

# -------------------------------------------------
# 6. SAVE RESULTS
# -------------------------------------------------
in_degree.to_csv("in_degree_centrality_2017.csv", index=False)
out_degree.to_csv("out_degree_centrality_2017.csv", index=False)
betweenness.to_csv("betweenness_centrality_2017.csv", index=False)
pagerank.to_csv("pagerank_2017.csv", index=False)
clustering_df.to_csv("clustering_coefficients_2017.csv", index=False)

with open("network_density_2017.txt", "w") as f:
    f.write(f"Network density: {network_density}\n")

print("GPU network analysis completed successfully.")
