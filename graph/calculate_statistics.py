import networkx as nx
import json

# Load the JSON file
with open("graph_top50.json", "r") as f:
    data = json.load(f)

# Create a NetworkX graph from the JSON
G = nx.Graph()

# Add nodes
for node in data["nodes"]:
    G.add_node(node["id"], label=node["label"], industry=node["industry"])

# Add edges
for edge in data["edges"]:
    G.add_edge(edge["source"], edge["target"], weight=edge["weight"])

# Calculate centrality metrics
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G, weight="weight")
closeness_centrality = nx.closeness_centrality(G)
eigenvector_centrality = nx.eigenvector_centrality_numpy(G, weight="weight")

# Add metrics to nodes
for node_id in G.nodes():
    G.nodes[node_id]["degree_centrality"] = degree_centrality[node_id]
    G.nodes[node_id]["betweenness_centrality"] = betweenness_centrality[node_id]
    G.nodes[node_id]["closeness_centrality"] = closeness_centrality[node_id]
    G.nodes[node_id]["eigenvector_centrality"] = eigenvector_centrality[node_id]

# Convert nodes and edges to exportable format
nodes = []
for node_id, attrs in G.nodes(data=True):
    nodes.append({
        "id": node_id,
        "label": attrs["label"],
        "industry": attrs["industry"],
        "degree_centrality": attrs["degree_centrality"],
        "betweenness_centrality": attrs["betweenness_centrality"],
        "closeness_centrality": attrs["closeness_centrality"],
        "eigenvector_centrality": attrs["eigenvector_centrality"]
    })

edges = []
for source, target, attrs in G.edges(data=True):
    edges.append({
        "source": source,
        "target": target,
        "weight": attrs["weight"]
    })

# Save new JSON
with open("graph_with_centrality.json", "w") as f:
    json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

print("Saved as graph_with_centrality.json")
