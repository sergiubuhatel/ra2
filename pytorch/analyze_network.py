import pandas as pd
import torch
from torch_geometric.data import Data
from torch_geometric.nn import Node2Vec
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import networkx as nx

# --- Device setup ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# --- Load CSVs ---
industries = pd.read_csv("2017_industries.csv")
network = pd.read_csv("2017_Network.csv")

# --- Clean data ---
industries["ticker"] = industries["ticker"].str.upper()
network["firma"] = network["firma"].str.upper()
network["firmb"] = network["firmb"].str.upper()
network["numconnections"] = pd.to_numeric(network["numconnections"], errors="coerce")
network = network.dropna(subset=["firma", "firmb", "numconnections"])

# --- Encode nodes ---
nodes = pd.unique(network[["firma", "firmb"]].values.ravel())
node_to_idx = {node: i for i, node in enumerate(nodes)}

edge_index = torch.tensor([
    [node_to_idx[src] for src in network["firma"]],
    [node_to_idx[dst] for dst in network["firmb"]]
], dtype=torch.long).to(device)

edge_weight = torch.tensor(network["numconnections"].values, dtype=torch.float).to(device)

data = Data(edge_index=edge_index, edge_attr=edge_weight, num_nodes=len(nodes))

# --- Node2Vec embeddings ---
embedding_dim = 16
model = Node2Vec(
    edge_index=edge_index,
    embedding_dim=embedding_dim,
    walk_length=20,
    context_size=10,
    walks_per_node=10,
    num_negative_samples=1,
    sparse=True
).to(device)

loader = model.loader(batch_size=32, shuffle=True)
optimizer = torch.optim.SparseAdam(list(model.parameters()), lr=0.01)

# --- Train Node2Vec ---
epochs = 50
for epoch in range(epochs):
    total_loss = 0
    for pos_rw, neg_rw in loader:
        pos_rw = pos_rw.to(device)
        neg_rw = neg_rw.to(device)
        optimizer.zero_grad()
        loss = model.loss(pos_rw, neg_rw)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")

# --- Get embeddings ---
embeddings = model.embedding.weight.detach().cpu().numpy()

# --- Cluster nodes ---
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
clusters = kmeans.fit_predict(embeddings)
firm_clusters = {node: cluster for node, cluster in zip(nodes, clusters)}

# --- Print clusters ---
print("\n--- Stock Clusters ---")
for firm, cluster in firm_clusters.items():
    print(f"{firm}: Cluster {cluster}")

# --- Build NetworkX graph ---
G = nx.from_pandas_edgelist(network, 'firma', 'firmb', edge_attr='numconnections')

# --- Layout for visualization ---
pos = nx.spring_layout(G, seed=42)

# --- Node colors and sizes ---
colors = [firm_clusters.get(node, -1) for node in G.nodes()]
centrality = nx.degree_centrality(G)
node_sizes = [500 * (centrality[node] + 0.1) for node in G.nodes()]  # scaled

# --- Draw network ---
plt.figure(figsize=(14, 10))
nx.draw(
    G,
    pos,
    node_color=colors,
    cmap=plt.cm.tab10,
    node_size=node_sizes,
    with_labels=True,
    font_size=8,
    edge_color='lightgray'
)
plt.title("Financial Stock Network Clusters (Node2Vec + KMeans)", fontsize=16)
plt.show()
