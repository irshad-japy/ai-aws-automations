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