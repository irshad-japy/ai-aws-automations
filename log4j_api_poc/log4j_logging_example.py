from pyspark.sql import SparkSession

# Step 1: Start SparkSession with log4j config
spark = SparkSession.builder \
    .appName("Log4jLoggingExample") \
    .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:log4j2.properties") \
    .config("spark.executor.extraJavaOptions", "-Dlog4j.configuration=file:log4j2.properties") \
    .getOrCreate()

# Step 2: Access Log4j logger from JVM
log4j_logger = spark._jvm.org.apache.log4j.LogManager.getLogger("my.custom.logger")

# Step 3: Log some messages
log4j_logger.info("✅ This is an INFO message from Log4j logger.")
log4j_logger.warn("⚠️ This is a WARNING message from Log4j logger.")
log4j_logger.error("❌ This is an ERROR message from Log4j logger.")

# Step 4: Run a basic Spark action
df = spark.createDataFrame([(1, "a"), (2, "b")], ["id", "value"])
df.show()

log4j_logger.debug("✅ DataFrame shown successfully.")

spark.stop()
