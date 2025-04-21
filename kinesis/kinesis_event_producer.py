"""
python -m aws.aws_kinesis.kinesis_event_producer
"""

import boto3
import random
import string
from datetime import datetime
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.time_calc_decorator import timeit

# 🔧 Configuration
STREAM_NAME = "k-mytoll.syd.dem.stg.tdf.event"
REGION_NAME = "ap-southeast-2"
THREADS = 10           # Number of threads
RECORD_COUNT = 10   # Total records to send

kinesis_client = boto3.client("kinesis", region_name=REGION_NAME)

# Sample options
event_codes = [
    ("CREATED$$CREATE", "CREATED"),
    ("ARRIVED$$DEL", "DEL"),
    ("DISPTCHD$$DEL", "DEL"),
]
business_units = ["TNQX", "SYDQ", "MELB"]

def generate_random_track_id():
    return ''.join(random.choices(string.digits, k=20))

def generate_event_xml():
    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    consignment_number = str(random.randint(24691161240000, 24691161249999))
    consignment_id = f"{consignment_number}_TDF"
    track_id = generate_random_track_id()
    event_code, parent_event = random.choice(event_codes)
    business_unit = random.choice(business_units)

    eventMsg = ET.Element("eventMsg", {
        "consignmentId": consignment_id,
        "consignmentNumber": consignment_number
    })

    srcSystem = ET.SubElement(eventMsg, "srcSystem")
    srcSystem.text = "TW"

    event = ET.SubElement(eventMsg, "event")
    ET.SubElement(event, "type").text = "item"
    ET.SubElement(event, "itemId").text = track_id
    ET.SubElement(event, "trackId").text = track_id
    ET.SubElement(event, "eventCode").text = event_code
    ET.SubElement(event, "parentEventCode").text = parent_event
    ET.SubElement(event, "businessUnit").text = business_unit
    ET.SubElement(event, "eventDateTime").text = now
    ET.SubElement(event, "eventTimezone").text = "Australia/Melbourne"
    ET.SubElement(event, "aestEventDateTime").text = now

    return ET.tostring(eventMsg, encoding="unicode"), consignment_id

def send_record(i):
    try:
        xml_data, partition_key = generate_event_xml()
        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=xml_data,
            PartitionKey=partition_key
        )
        return f"✔ Event {i} sent | SequenceNumber: {response['SequenceNumber']}"
    except Exception as e:
        return f"❌ Event {i} failed | Error: {str(e)}"

@timeit
def send_to_kinesis_parallel():
    print(f"🚀 Sending {RECORD_COUNT} records using {THREADS} threads...")
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(send_record, i+1) for i in range(RECORD_COUNT)]
        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    send_to_kinesis_parallel()
