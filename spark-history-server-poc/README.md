# Approach 1: Everything locally
# Run Instructions  
1. Create the spark event log directory: 
   sudo mkdir -p /tmp/spark-events 
   sudo chmod -R 777 /tmp/spark-events 
 
2. Run the Spark job: 
   cd ~/projects/tge-projects/spark-history-server-poc
   spark-submit --properties-file spark-defaults.conf spark_job.py 
 
3. Start the history server: 
   chmod +x start-history-server.sh 
   ./start-history-server.sh 
 
4. Open the browser and visit: 
   http://localhost:18080 

# Windows Commands
# D:\Users\IrshadAl\tge\ird-project\aws_projects\.venv\Scripts\activate.bat
set PYSPARK_PYTHON=python
set PYSPARK_DRIVER_PYTHON=python

1. Open new Command Prompt, create event logs folder
   mkdir C:\tmp\spark-events

2. Move into project folder
   cd C:\Users\YourName\Documents\spark-history-server-poc

3. Run Spark job
# powershell
spark-submit `
  --properties-file spark-defaults.conf `
  --conf spark.log4jHotPatch.enabled=false `
  --conf spark.driver.memory=2g `
  --conf spark.executor.memory=2g `
  spark_job.py

  # cmd prompt
  spark-submit ^
  --properties-file spark-defaults.conf ^
  --conf spark.log4jHotPatch.enabled=false ^
  --conf spark.driver.memory=2g ^
  --conf spark.executor.memory=2g ^
  spark_job.py

4. Start History Server
   start-history-server.cmd

5. Open in Browser
   start http://localhost:18080

mkdir D:\tmp\spark-events


# Approach2: When spark event are in cloud and spark_haddop setup in windows
1. Use below settings in spark-defaults.conf file
# Spark History Server
spark.history.fs.logDirectory=s3a://b-myteamge-syd-perf-glue-dem/sparkeventlogs/myteamge-glue-consignment-collector-tgx/
spark.history.fs.update.interval=10s
spark.history.fs.cleaner.enabled=true
spark.history.fs.cleaner.maxAge=7d
spark.history.provider=org.apache.spark.deploy.history.FsHistoryProvider
spark.hadoop.fs.s3a.aws.credentials.provider=com.amazonaws.auth.DefaultAWSCredentialsProviderChain

# AWS and S3A Configurations
spark.driver.extraJavaOptions=-Divy.cache.dir=/tmp -Divy.home=/tmp -Dcom.amazonaws.services.s3.enableV4=true
spark.executor.extraJavaOptions=-Dcom.amazonaws.services.s3.enableV4=true

spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
spark.hadoop.fs.s3a.endpoint=s3.ap-southeast-2.amazonaws.com
spark.hadoop.fs.s3a.connection.maximum=100
spark.hadoop.fs.s3a.attempts.maximum=3
spark.hadoop.fs.s3a.fast.upload=true
spark.hadoop.fs.s3a.multipart.size=104857600
spark.hadoop.fs.s3a.buffer.dir=/tmp
spark.hadoop.fs.s3a.connection.ssl.enabled=true
spark.hadoop.fs.s3a.connection.timeout=60000

# Optional if your bucket needs path style access (e.g., localhost/minio or custom endpoint)
spark.hadoop.fs.s3a.path.style.access=true


2. Open Admin CMD prompt 
cd D:\Users\IrshadAl\tge\softwares\spark_hadoop\spark-3.3.2-bin-hadoop3\sbin
spark-class org.apache.spark.deploy.history.HistoryServer
