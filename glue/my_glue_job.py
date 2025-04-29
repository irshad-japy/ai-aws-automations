# my_glue_local_demo.py

import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions

# 1) Grab JOB_NAME so GlueContext initializes cleanly
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

# 2) Create Spark + Glue contexts
sc    = SparkContext()
glue  = GlueContext(sc)
spark = glue.spark_session

print(f"Running Glue demo with Spark {spark.version}")

# 3) Build an in-memory DataFrame with sample data
sample_data = [
    ("Alice",  29, "Finance"),
    ("Bob",    42, "Engineering"),
    ("Carol",  35, "Marketing"),
    ("Dave",   23, "Sales")
]
columns = ["name", "age", "dept"]

df = spark.createDataFrame(sample_data, schema=columns)

# 4) Show the data
print("=== Sample DataFrame ===")
df.show()

# 5) Run a simple transformation (e.g. people over 30)
print("=== Filter: age > 30 ===")
df.filter(df.age > 30).show()

# 6) Write out to console (or change to write.parquet / write.csv as needed)
#    Here we’ll just collect and print
results = df.collect()
print("Collected rows:", results)

# 7) Stop contexts when done
sc.stop()
