"""
set PYSPARK_PYTHON=python
set PYSPARK_DRIVER_PYTHON=python
spark-submit --packages graphframes:graphframes:0.8.2-spark3.1-s_2.12 pyspark/graphframe_poc/graphframes_visualization.py
"""

from pyspark.sql import SparkSession
from graphframes import GraphFrame
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 1️⃣ Start Spark Session with GraphFrames
spark = SparkSession.builder \
    .appName("GraphFrames Visualization") \
    .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12") \
    .getOrCreate()

# 2️⃣ Create vertices and edges
vertices = spark.createDataFrame([
    ("a", "Alice", 34),
    ("b", "Bob", 36),
    ("c", "Charlie", 30),
    ("d", "David", 29),
    ("e", "Esther", 32),
    ("f", "Fay", 25),
    ("g", "George", 28),
    ("h", "Hannah", 40),
    ("i", "Ivan", 31)
], ["id", "name", "age"])

edges = spark.createDataFrame([
    ("a", "b", "friend"),
    ("b", "c", "follow"),
    ("c", "d", "friend"),
    ("d", "e", "follow"),
    ("e", "a", "friend"),
    ("b", "d", "friend"),
    ("a", "c", "follow"),
    ("f", "g", "friend"),
    ("g", "h", "follow"),
    ("h", "i", "friend"),
    ("i", "f", "follow"),
    ("c", "f", "friend"),
    ("b", "g", "follow")
], ["src", "dst", "relationship"])

# 3️⃣ Convert to pandas DataFrames
vertex_df = vertices.toPandas()
edge_df = edges.toPandas()

# 4️⃣ Create NetworkX Graph
G = nx.DiGraph()
for _, row in vertex_df.iterrows():
    G.add_node(row['id'], name=row['name'], age=row['age'])
for _, row in edge_df.iterrows():
    G.add_edge(row['src'], row['dst'], relationship=row['relationship'])

# 📌 Color by Age Group
color_map_age = []
for node in G.nodes:
    age = G.nodes[node]['age']
    if age < 30:
        color_map_age.append('lightgreen')
    elif 30 <= age < 35:
        color_map_age.append('lightblue')
    else:
        color_map_age.append('orange')

plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, labels={n: G.nodes[n]['name'] for n in G.nodes},
        node_color=color_map_age, node_size=1000, edge_color='gray', arrows=True)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(row['src'], row['dst']): row['relationship'] for _, row in edge_df.iterrows()}, font_color='red')
plt.title("Graph Colored by Age Group")
plt.axis('off')
plt.show()

# 📌 Color by Connected Components
undirected_G = G.to_undirected()
components = list(nx.connected_components(undirected_G))
color_map_comp = []
for node in G.nodes:
    for idx, comp in enumerate(components):
        if node in comp:
            color_map_comp.append(f"C{idx}")
            break

plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, labels={n: G.nodes[n]['name'] for n in G.nodes},
        node_color=color_map_comp, node_size=1000, edge_color='gray', arrows=True)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(row['src'], row['dst']): row['relationship'] for _, row in edge_df.iterrows()}, font_color='red')
plt.title("Graph Colored by Connected Components")
plt.axis('off')
plt.show()

# Stop Spark session
spark.stop()
