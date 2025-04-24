from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("POC_History_Server") \
    .config("spark.eventLog.enabled", "true") \
    .config("spark.eventLog.dir", "file:///tmp/spark-events") \
    .getOrCreate()

# Sample job
print("\nRunning sample Spark job...")
df = spark.range(1, 100000)
df = df.withColumn("square", df["id"] * df["id"])
df.write.mode("overwrite").parquet("/tmp/output-data")

spark.stop()
print("\nSpark job completed.")