
PS D:\Users\IrshadAl\tge\ird-project\aws_projects> & 'D:\spark_setup\spark_3_3_1\spark\spark-3.3.1-bin-hadoop3\bin\spark-submit.cmd' `
>>   --master local[*] `
>>   --verbose `
>>   --conf spark.log4jHotPatch.enabled=false `
>>   --conf spark.pyspark.python=python `
>>   --conf spark.pyspark.driver.python=python `
>>   glue\my_glue_job.py --JOB_NAME LocalSample
