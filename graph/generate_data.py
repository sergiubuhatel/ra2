# Example Usage:
#
# python your_script.py \
#   --nodes ./frontend/public/data/2017/Top50_tickers.csv \
#   --edges ./frontend/public/data/2017/edgesBtwTop50_2017.csv \
#   --output ./frontend/public/data/2017/graph_with_centrality.json


import pandas as pd
import json
import networkx as nx
import argparse


def prepare_graph_data(nodes_file, edges_file):
    """
    Reads CSVs and builds a NetworkX Graph directly in memory.

    Returns:
        G (networkx.Graph): The constructed graph with node attributes.
    """
    # Load data
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)

    # Clean and filter edges: keep only those between top 50 nodes
    top50_ids = set(nodes_df['ID'])
    filtered_edges = edges_df[
        edges_df['Source'].isin(top50_ids) & edges_df['Target'].isin(top50_ids)
    ]

    # Handle missing industry data
    nodes_df['Industry'] = nodes_df['Industry'].fillna(-1)

    # Initialize graph
    G = nx.Graph()

    # Add nodes with attributes
    for _, row in nodes_df.iterrows():
        G.add_node(row["ID"], label=row["Label"], industry=row["Industry"])

    # Add edges with weight
    for _, row in filtered_edges.iterrows():
        G.add_edge(row["Source"], row["Target"], weight=row["Weight"])

    print(f"Step 1: Graph built in memory with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G


def compute_centralities(G, output_file):
    """
    Computes various centrality metrics and exports the result as JSON.

    Args:
        G (networkx.Graph): Graph with node and edge data.
        output_file (str): Path to output JSON file.
    """
    print("Step 2: Calculating centrality metrics...")

    # Centrality computations
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G, weight="weight")
    closeness_centrality = nx.closeness_centrality(G)
    eigenvector_centrality = nx.eigenvector_centrality_numpy(G, weight="weight")
    harmonic_centrality = nx.harmonic_centrality(G, distance="weight")
    eccentricity = nx.eccentricity(G)

    # Degree stats
    unweighted_degree = dict(G.degree())
    weighted_degree = dict(G.degree(weight="weight"))

    # Compile node data
    nodes_out = []
    for node_id in G.nodes():
        attr = G.nodes[node_id]
        nodes_out.append({
            "id": node_id,
            "label": attr.get("label"),
            "industry": attr.get("industry"),
            "degree_centrality": degree_centrality[node_id],
            "betweenness_centrality": betweenness_centrality[node_id],
            "closeness_centrality": closeness_centrality[node_id],
            "eigenvector_centrality": eigenvector_centrality[node_id],
            "harmonic_centrality": harmonic_centrality[node_id],
            "eccentricity": eccentricity[node_id],
            "degree": unweighted_degree[node_id],
            "weighted_degree": weighted_degree[node_id]
        })

    # Compile edge data
    edges_out = [
        {
            "source": u,
            "target": v,
            "weight": d["weight"]
        }
        for u, v, d in G.edges(data=True)
    ]

    # Export as JSON
    with open(output_file, "w") as f:
        json.dump({"nodes": nodes_out, "edges": edges_out}, f, indent=2)

    print(f"Step 3: Graph with centrality metrics saved to {output_file}")


# === CLI Entry Point ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build graph and compute centrality metrics.")
    parser.add_argument('--nodes', required=True, help="Path to nodes CSV (e.g., Top50_tickers.csv)")
    parser.add_argument('--edges', required=True, help="Path to edges CSV (e.g., edgesBtwTop50_2017.csv)")
    parser.add_argument('--output', required=True, help="Path to output JSON file")

    args = parser.parse_args()

    G = prepare_graph_data(args.nodes, args.edges)
    compute_centralities(G, args.output)
