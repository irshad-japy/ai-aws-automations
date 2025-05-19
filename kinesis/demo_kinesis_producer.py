"""
python -m kinesis.demo_kinesis_producer
"""

import boto3
import json
import time
import random

STREAM_NAME = "k-nihau-ex.dem.stg.tdf.consignment"
kinesis_client = boto3.client("kinesis", region_name="ap-southeast-2")

def generate_event():
    return {
        "user_id": random.randint(1, 100),
        "action": random.choice(["login", "logout", "purchase"]),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

while True:
    event = generate_event()
    kinesis_client.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(event),
        PartitionKey=str(event['user_id'])
    )
    print("Sent:", event)
    time.sleep(1)
