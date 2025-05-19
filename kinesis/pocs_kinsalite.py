"""
python -m kinesis.pocs_kinsalite
"""

import boto3
import json
import time

# Kinesalite endpoint
kinesis = boto3.client(
    "kinesis",
    region_name="us-east-1",
    endpoint_url="http://localhost:4567",  # Kinesalite default
    aws_access_key_id="fakeMyKeyId",        # Dummy values for local
    aws_secret_access_key="fakeSecretAccessKey"
)

# Constants
STREAM_NAME = "demo-stream"

def create_stream():
    print("Creating stream...")
    kinesis.create_stream(StreamName=STREAM_NAME, ShardCount=1)
    # Wait until stream becomes ACTIVE
    while True:
        response = kinesis.describe_stream(StreamName=STREAM_NAME)
        status = response["StreamDescription"]["StreamStatus"]
        print(f"Stream status: {status}")
        if status == "ACTIVE":
            break
        time.sleep(1)
    print("Stream is active.")

def put_record():
    print("Putting record...")
    response = kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps({"event": "test_event", "value": 123}),
        PartitionKey="partition-1"
    )
    print("Put record response:", response)

def get_records():
    print("Getting shard iterator...")
    shard_id = kinesis.describe_stream(StreamName=STREAM_NAME)['StreamDescription']['Shards'][0]['ShardId']
    shard_iter = kinesis.get_shard_iterator(
        StreamName=STREAM_NAME,
        ShardId=shard_id,
        ShardIteratorType='TRIM_HORIZON'
    )['ShardIterator']

    print("Reading records from stream...")
    records = kinesis.get_records(ShardIterator=shard_iter, Limit=10)
    for record in records['Records']:
        print("Record:", record['Data'].decode())

if __name__ == "__main__":
    create_stream()
    put_record()
    time.sleep(1)
    get_records()
