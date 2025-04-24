#!/bin/bash

# Set Spark home based on your system
export SPARK_HOME=/home/erirs/spark_setup/spark/spark-3.4.0-bin-hadoop3
export PATH=$SPARK_HOME/bin:$PATH

# Optional: Set where to read Spark event logs from (should match spark-defaults.conf)
export SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=file:///tmp/spark-events"

# Start the history server
$SPARK_HOME/sbin/start-history-server.sh
