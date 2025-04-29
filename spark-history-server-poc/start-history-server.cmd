@echo off
:: Setup Spark Home
@REM set SPARK_HOME=D:\spark_setup\spark_3_3_1\spark\spark-3.3.1-bin-hadoop3
@REM set PATH=%SPARK_HOME%\bin;%PATH%

:: Setup History Server Log Directory
set SPARK_HISTORY_OPTS=-Dspark.history.fs.logDirectory=file:///D:/tmp/spark-events

:: Start the History Server manually
spark-class org.apache.spark.deploy.history.HistoryServer
