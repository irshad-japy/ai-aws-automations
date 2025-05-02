"""
spark-submit --verbose ^
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:log4j.properties" ^
  --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:log4j.properties" ^
  --master local[*] ^
  --name GlueLoggerDemo ^
  driver_executor_demo.py
"""

from pyspark.sql import SparkSession

# ----------------------------
# 1. DRIVER FUNCTION
# ----------------------------
def driver_function(logger):
    # Log a message from the driver
    logger.info("ird_1214: Running driver_function on the driver")

# ----------------------------
# 2. WORKER (EXECUTOR) FUNCTION
# ----------------------------
def worker_function(x, add_broadcast, spark):
    logger = spark._jvm.org.apache.log4j.LogManager.getLogger("GlueLoggerDemo")
    # Log a message from the executor
    logger.info(f"ird_1214: Executor processing value: {x}")
    return x * x + add_broadcast.value

def initialize_spark(log4j_path="/tmp/log4j.properties"):
    try:
        spark = SparkSession.builder \
            .appName("GlueLoggerDemo") \
            .config("spark.driver.extraJavaOptions", f"-Dlog4j.configurationFile={log4j_path}") \
            .config("spark.executor.extraJavaOptions", f"-Dlog4j.configurationFile={log4j_path}") \
            .getOrCreate()

        return spark
    except Exception as e:
        print(f"Error initializing Spark: {e}")
        raise

if __name__ == "__main__":
    # Initialize Spark
    spark = initialize_spark()

    # Get the log4j logger
    logger = spark._jvm.org.apache.log4j.LogManager.getLogger("GlueLoggerDemo")

    # Access the SparkContext
    sc = spark.sparkContext

    # Log a message from the driver
    driver_function(logger)

    # Create a broadcast variable
    broadcast_var = sc.broadcast(10)

    # Prepare an RDD
    data = [1, 2, 3, 4, 5]
    rdd = sc.parallelize(data, numSlices=2)

    # Use the logger in the worker function
    squared_plus_bcast = rdd.map(lambda x: worker_function(x, broadcast_var, spark))

    # Collect results
    results = squared_plus_bcast.collect()

    # Log results on the driver
    logger.info(f"ird_1214: Results collected on driver: {results}")

    # Stop Spark
    spark.stop()