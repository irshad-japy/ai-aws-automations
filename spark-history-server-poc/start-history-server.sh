#!/bin/bash

export SPARK_HOME=/home/erirs/spark_setup/spark/spark-3.4.0-bin-hadoop3
export PATH=$SPARK_HOME/bin:$PATH

export SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=file:///tmp/spark-events"

$SPARK_HOME/sbin/start-history-server.sh
