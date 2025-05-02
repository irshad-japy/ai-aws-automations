Compress-Archive -Path utils,log_utils -DestinationPath log4j.zip

------------------------------------
set PYSPARK_PYTHON=python
set PYSPARK_DRIVER_PYTHON=python
set PYTHONPATH=%CD%

spark-submit ^
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:log4j.properties" ^
  --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:log4j.properties" ^
  --master local[*] ^
  --name GlueLoggerDemo ^
  --py-files log4j.zip ^
  main.py