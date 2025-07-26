import pandas as pd
import json
import networkx as nx

# === Step 1: Load and Prepare Graph Data ===

# Load data
nodes_df = pd.read_csv('Top50_tickers.csv')
edges_df = pd.read_csv('edgesBtwTop50_2017.csv')

# Clean and filter edges: keep only those between top 50
top50_ids = set(nodes_df['ID'])
filtered_edges = edges_df[
    edges_df['Source'].isin(top50_ids) &
    edges_df['Target'].isin(top50_ids)
]

# Handle missing industry data
nodes_df['Industry'] = nodes_df['Industry'].fillna(-1)

# Prepare nodes and edges as dicts (in memory)
nodes = [
    {
        "id": row["ID"],
        "label": row["Label"],
        "industry": row["Industry"]
    }
    for _, row in nodes_df.iterrows()
]

edges = [
    {
        "source": row["Source"],
        "target": row["Target"],
        "weight": row["Weight"]
    }
    for _, row in filtered_edges.iterrows()
]

print("Step 1: Graph data prepared in memory.")

# === Step 2: Build Graph and Calculate Centrality Metrics ===

# Create NetworkX graph
G = nx.Graph()

# Add nodes
for node in nodes:
    G.add_node(node["id"], label=node["label"], industry=node["industry"])

# Add edges
for edge in edges:
    G.add_edge(edge["source"], edge["target"], weight=edge["weight"])

# Compute centrality metrics
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G, weight="weight")
closeness_centrality = nx.closeness_centrality(G)
eigenvector_centrality = nx.eigenvector_centrality_numpy(G, weight="weight")
harmonic_centrality = nx.harmonic_centrality(G, distance='weight')
eccentricity = nx.eccentricity(G)
unweighted_degree = dict(G.degree())
weighted_degree = dict(G.degree(weight="weight"))

# Add metrics to nodes
final_nodes = []
for node_id in G.nodes():
    attrs = G.nodes[node_id]
    final_nodes.append({
        "id": node_id,
        "label": attrs["label"],
        "industry": attrs["industry"],
        "degree_centrality": degree_centrality[node_id],
        "betweenness_centrality": betweenness_centrality[node_id],
        "closeness_centrality": closeness_centrality[node_id],
        "eigenvector_centrality": eigenvector_centrality[node_id],
        "harmonic_centrality": harmonic_centrality[node_id],
        "eccentricity": eccentricity[node_id],
        "degree": unweighted_degree[node_id],
        "weighted_degree": weighted_degree[node_id]
    })

# Prepare final edges
final_edges = [
    {
        "source": u,
        "target": v,
        "weight": d["weight"]
    }
    for u, v, d in G.edges(data=True)
]

# Save final graph with centralities
with open("graph_with_centrality.json", "w") as f:
    json.dump({"nodes": final_nodes, "edges": final_edges}, f, indent=2)

print("Step 2: Final graph saved as graph_with_centrality.json")
