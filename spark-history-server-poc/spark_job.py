import os
from pyspark.sql import SparkSession

# Dynamically choose event log dir based on OS
if os.name == 'nt':  # nt means Windows
    event_log_dir = "file:///D:/tmp/spark-events"
    output_dir = "D:/tmp/output-data"
else:
    event_log_dir = "file:///tmp/spark-events"
    output_dir = "/tmp/output-data"

spark = SparkSession.builder \
    .appName("POC_History_Server") \
    .config("spark.eventLog.enabled", "true") \
    .config("spark.eventLog.dir", event_log_dir) \
    .getOrCreate()

print("\nRunning sample Spark job...")
df = spark.range(1, 100000)
df = df.withColumn("square", df["id"] * df["id"])
df.write.mode("overwrite").parquet(output_dir)

spark.stop()
print("\nSpark job completed.")
