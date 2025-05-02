# utils/helper.py
from my_glue_job.log_utils.jvm_logger import get_jvm_logger

def do_transformation(spark):
    logger = get_jvm_logger(spark, "helper-logger")
    logger.info("ird_1214: Log from helper function - this may appear in executor or driver depending on where it's called.")
