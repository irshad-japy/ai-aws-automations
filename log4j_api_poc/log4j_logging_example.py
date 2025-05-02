from pyspark.sql import SparkSession

def driver_function():
    logger.info("ird_1214: Running driver_function on the driver")

def worker_function(x, add_broadcast):
    # Log from the executor
    logger.info(f"ird_1214: Executor processing value: {x}")
    return x * x + add_broadcast.value

# Step 1: Start SparkSession with log4j config
spark = SparkSession.builder \
    .appName("Log4jLoggingExample") \
    .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:log4j2.properties") \
    .config("spark.executor.extraJavaOptions", "-Dlog4j.configuration=file:log4j2.properties") \
    .getOrCreate()

sc = spark.sparkContext
# Step 2: Access Log4j logger from JVM
logger = spark._jvm.org.apache.log4j.LogManager.getLogger("my.custom.logger")

# Step 3: Log some messages
logger.info("✅ This is an INFO message from Log4j logger.")
logger.warn("⚠️ This is a WARNING message from Log4j logger.")
logger.error("❌ This is an ERROR message from Log4j logger.")

# Step 4: Run a basic Spark action
broadcast_var = sc.broadcast(10)
data = [1, 2, 3, 4, 5]
rdd = sc.parallelize(data, numSlices=2)

squared_plus_bcast = rdd.map(lambda x: worker_function(x, broadcast_var))
results = squared_plus_bcast.collect()

logger.info(f"ird_1214: Results collected on driver: {results}")

logger.debug("✅ DataFrame shown successfully.")

spark.stop()
