# main.py
from my_glue_job.log_utils.jvm_logger import get_log4j_logger
from utils.helper import do_transformation
from pyspark.sql import SparkSession
from pyspark import SparkContext
import logging

def log_in_executor(x):
    # This runs entirely on the worker.
    # Use Python's built-in logging instead of log4j in executors
    
    # Configure logging for the executor
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("executor-logger")
    
    logger.info(f"Log from executor: value={x}")
    return x

def initialize_spark(log4j_path="/tmp/log4j2.properties"):
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

def main():
    spark = initialize_spark()

    # Driver logger
    driver_log = get_log4j_logger(spark, "main-logger")
    driver_log.info("ird_1214: Job started from main.py")

    do_transformation(spark)

    data = spark.sparkContext.parallelize([1, 2, 3])
    data.foreach(log_in_executor)

    driver_log.info("ird_1214: Job completed")

if __name__ == "__main__":
    main()
