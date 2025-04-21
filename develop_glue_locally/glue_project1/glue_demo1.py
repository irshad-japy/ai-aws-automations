from pyspark.context import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
import pandas as pd
from my_utils import (
    format_name
)

# Start Spark + Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Sample data
data = [("u1", "Alice", "US"), ("u2", "Bob", "IN"), ("u3", "Charlie", "US")]
columns = ["user_id", "name", "country"]
df = spark.createDataFrame(data, columns)

# UDF usage
udf_format_name = udf(format_name, StringType())
df = df.withColumn("formatted_name", udf_format_name(col("name")))

# Convert to DynamicFrame
dyf = DynamicFrame.fromDF(df, glueContext, "dyf")
dyf.toDF().show()

# Write parquet
df.write.mode("overwrite").partitionBy("country").parquet("output/parquet_output")

spark.stop()
