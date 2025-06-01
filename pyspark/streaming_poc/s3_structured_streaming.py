"""
set PYSPARK_PYTHON=python
set PYSPARK_DRIVER_PYTHON=python
spark-submit pyspark/streaming_poc/s3_structured_streaming.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

# ✅ Create SparkSession
spark = SparkSession.builder \
    .appName("S3StructuredStreamingPOC") \
    .getOrCreate()

# ✅ Set log level
spark.sparkContext.setLogLevel("WARN")

# ✅ Read text files from S3 folder
s3_path = "s3a://tge-nihau-bucket/streaming/input/"

# Spark will look for new files appearing here
lines_df = spark.readStream \
    .format("text") \
    .load(s3_path)

# ✅ Split each line into words
words_df = lines_df.select(
    explode(split(lines_df.value, " ")).alias("word")
)

# ✅ Count each word
word_counts = words_df.groupBy("word").count()

# ✅ Output to console (in micro-batches)
query = word_counts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
