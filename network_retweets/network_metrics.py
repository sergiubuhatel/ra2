import pandas as pd
import networkx as nx

# -------------------------------------------------
# 1. Load data (NO HEADER in CSV)
# -------------------------------------------------
file_path = "retweet_network2017.csv"

df = pd.read_csv(
    file_path,
    header=None,
    names=[
        "screen_name4",
        "user_screen_name",
        "edgeB",
        "tweetyear",
        "tweetmonth",
        "EST"
    ],
    engine="python",     # <-- critical fix
    sep=",",
    quotechar='"',
    on_bad_lines="skip"  # <-- skip malformed rows
)

# -------------------------------------------------
# 2. Build directed retweet network
# -------------------------------------------------
G = nx.DiGraph()

# Add edges: user_screen_name -> edgeB
for _, row in df.iterrows():
    if pd.notna(row["user_screen_name"]) and pd.notna(row["edgeB"]):
        G.add_edge(row["user_screen_name"], row["edgeB"])

# -------------------------------------------------
# 3. Centrality metrics
# -------------------------------------------------
centrality_df = pd.DataFrame({
    "in_degree_centrality": nx.in_degree_centrality(G),
    "out_degree_centrality": nx.out_degree_centrality(G),
    "betweenness_centrality": nx.betweenness_centrality(G, normalized=True),
    "eigenvector_centrality": nx.eigenvector_centrality(G, max_iter=1000)
})
centrality_df.index.name = "user"

# -------------------------------------------------
# 4. Clustering coefficient
#    (computed on undirected projection)
# -------------------------------------------------
clustering = nx.clustering(G.to_undirected())
clustering_df = pd.DataFrame.from_dict(
    clustering,
    orient="index",
    columns=["clustering_coefficient"]
)
clustering_df.index.name = "user"

# -------------------------------------------------
# 5. Network density
# -------------------------------------------------
density_df = pd.DataFrame(
    {"network_density": [nx.density(G)]}
)

# -------------------------------------------------
# 6. Save outputs
# -------------------------------------------------
centrality_df.to_csv("centrality_metrics_2017.csv")
clustering_df.to_csv("clustering_coefficients_2017.csv")
density_df.to_csv("network_density_2017.csv")

print("Finished. Output files created:")
print("- centrality_metrics_2017.csv")
print("- clustering_coefficients_2017.csv")
print("- network_density_2017.csv")
