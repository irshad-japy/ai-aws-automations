"""
set PYSPARK_PYTHON=python
set PYSPARK_DRIVER_PYTHON=python
spark-submit --packages graphframes:graphframes:0.8.2-spark3.1-s_2.12 pyspark/graphframe_poc/graphframe_algorithms.py
"""

from pyspark.sql import SparkSession
from graphframes import GraphFrame

# Start Spark Session with GraphFrames
spark = SparkSession.builder \
    .appName("GraphFrames POC Expanded") \
    .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.1-s_2.12") \
    .getOrCreate()

# Create expanded vertices and edges
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

# Build GraphFrame
g = GraphFrame(vertices, edges)

# 📌 PageRank
print("==== PageRank ====")
pagerank_results = g.pageRank(resetProbability=0.15, maxIter=5)
pagerank_results.vertices.select("id", "name", "pagerank").show()

# 📌 Connected Components
print("==== Connected Components ====")
# Set checkpoint directory for connectedComponents
spark.sparkContext.setCheckpointDir("file:///C:/tmp/spark-checkpoint")

# Connected Components
components = g.connectedComponents()
components.show()


# 📌 BFS from Alice (a) to Ivan (i)
print("==== BFS from Alice to Ivan ====")
bfs_results = g.bfs(fromExpr="id='a'", toExpr="id='i'")
bfs_results.show()
