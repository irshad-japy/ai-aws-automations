from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

spark = SparkSession.builder \
    .appName("KinesisConsumerPOC") \
    .getOrCreate()

# Create streaming DataFrame
df = spark.readStream \
    .format("kinesis") \
    .option("streamName", "k-nihau-ex.dem.stg.tdf.consignment") \
    .option("endpointUrl", "https://kinesis.ap-southeast-2.amazonaws.com") \
    .option("region", "ap-southeast-2") \
    .option("startingposition", "TRIM_HORIZON") \
    .load()

# Convert binary to string
df_parsed = df.selectExpr(
    "CAST(data AS STRING) as message",
    "CAST(partitionKey AS STRING)",
    "CAST(sequenceNumber AS STRING)"
)

# Write to console
query = df_parsed.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
