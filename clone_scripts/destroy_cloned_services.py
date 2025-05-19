"""
python clone_scripts/destroy_cloned_services.py
"""

import boto3
from botocore.exceptions import ClientError

def delete_cloned_glue_jobs(glue_job_names, region="ap-southeast-2"):
    glue = boto3.client("glue", region_name=region)
    for job_name in glue_job_names:
        try:
            glue.delete_job(JobName=job_name)
            print(f"🧹 Deleted Glue job: {job_name}")
        except ClientError as e:
            print(f"⚠️ Could not delete Glue job {job_name}: {e.response['Error']['Message']}")

def delete_cloned_dynamodb_tables(table_names):
    dynamodb = boto3.client("dynamodb")
    for table in table_names:
        try:
            dynamodb.delete_table(TableName=table)
            print(f"🧹 Deleted DynamoDB table: {table}")
        except ClientError as e:
            print(f"⚠️ Could not delete table {table}: {e.response['Error']['Message']}")

def delete_cloned_kinesis_streams(stream_names):
    kinesis = boto3.client("kinesis")
    for stream in stream_names:
        try:
            kinesis.delete_stream(StreamName=stream, EnforceConsumerDeletion=True)
            print(f"🧹 Deleted Kinesis stream: {stream}")
        except ClientError as e:
            print(f"⚠️ Could not delete stream {stream}: {e.response['Error']['Message']}")

def main():
    env = "stg"  # update if needed

    # Glue jobs to delete
    glue_jobs = [
        f"nihau-ex-glue-{env}-tdf-event"
    ]
    
    # DynamoDB tables to delete
    dynamodb_tables = [
        f"nihau-ex-table-{env}-consignment",
        f"nihau-ex-table-{env}-dirtyconsignment",
        f"nihau-ex-table-{env}-eventstate",
        f"nihau-ex-table-{env}-rawevent",
        f"nihau-ex-table-{env}-references"
    ]
    if env == "devge":
        dynamodb_tables.append(f"nihau-ex-table-dev_consignment_status_info")

    # Kinesis streams to delete
    kinesis_streams = [
        f"k-nihau-ex.dem.{env}.tdf.event",
        f"k-nihau-ex.dem.{env}.notification"
    ]

    print("\n🧨 Deleting Cloned AWS Resources...\n")
    delete_cloned_glue_jobs(glue_jobs)
    delete_cloned_dynamodb_tables(dynamodb_tables)
    delete_cloned_kinesis_streams(kinesis_streams)
    print("\n✅ Cleanup complete.")

if __name__ == "__main__":
    main()
