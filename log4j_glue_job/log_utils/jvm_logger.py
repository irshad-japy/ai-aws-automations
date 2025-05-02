# log_utils/log4j_logger.py
def get_jvm_logger(spark, logger_name="glue-job-logger"):
    """
    Returns a log4j logger usable across main and helper scripts.
    """
    jvm_logger = spark._jvm.org.apache.log4j.LogManager.getLogger(logger_name)
    return jvm_logger
