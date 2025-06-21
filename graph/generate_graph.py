import pandas as pd
import json

# Load data
nodes_df = pd.read_csv('Top50_tickers.csv')
edges_df = pd.read_csv('edgesBtwTop50_2017.csv')

# Clean and filter edges: keep only those between top 50
top50_ids = set(nodes_df['ID'])
filtered_edges = edges_df[
    edges_df['Source'].isin(top50_ids) &
    edges_df['Target'].isin(top50_ids)
]

# Handle missing industry data (e.g., fill with -1 or "Unknown")
nodes_df['Industry'] = nodes_df['Industry'].fillna(-1)

# Convert nodes to list of dicts
nodes = [
    {
        "id": row["ID"],
        "label": row["Label"],
        "industry": row["Industry"]
    }
    for _, row in nodes_df.iterrows()
]

# Convert edges to list of dicts
edges = [
    {
        "source": row["Source"],
        "target": row["Target"],
        "weight": row["Weight"]
    }
    for _, row in filtered_edges.iterrows()
]

# Build final JSON
graph_data = {
    "nodes": nodes,
    "edges": edges
}

# Export to file
with open("graph_top50.json", "w") as f:
    json.dump(graph_data, f, indent=2)
