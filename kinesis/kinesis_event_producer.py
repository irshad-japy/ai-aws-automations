"""
python -m kinesis.kinesis_event_producer
"""

import boto3
import random
import string
from datetime import datetime
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from kinesis.kinesis_xml_data import ec_input_records

# 🔧 Configuration
# STREAM_NAME  = "k-mytoll.syd.dem.stg.tdf.consignment"
STREAM_NAME  = "k-tge-nihau-stream"
REGION_NAME  = "ap-southeast-2"
THREADS      = 10           # Number of threads
RECORD_COUNT = 10           # Used only if no input_records

kinesis_client = boto3.client("kinesis", region_name=REGION_NAME)

# Sample options for generated events
event_codes    = [("CREATED$$CREATE", "CREATED"), ("ARRIVED$$DEL", "DEL"), ("DISPTCHD$$DEL", "DEL")]
business_units = ["TNQX", "SYDQ", "MELB"]


def generate_random_track_id():
    return ''.join(random.choices(string.digits, k=20))


def generate_event_xml():
    now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    consignment_number = str(random.randint(24691161240000, 24691161249999))
    consignment_id     = f"{consignment_number}_TDF"
    track_id           = generate_random_track_id()
    event_code, parent = random.choice(event_codes)
    busunit            = random.choice(business_units)

    root = ET.Element("eventMsg", {
        "consignmentId":     consignment_id,
        "consignmentNumber": consignment_number
    })
    ET.SubElement(root, "srcSystem").text = "TW"

    ev = ET.SubElement(root, "event")
    ET.SubElement(ev, "type").text           = "item"
    ET.SubElement(ev, "itemId").text         = track_id
    ET.SubElement(ev, "trackId").text        = track_id
    ET.SubElement(ev, "eventCode").text      = event_code
    ET.SubElement(ev, "parentEventCode").text= parent
    ET.SubElement(ev, "businessUnit").text   = busunit
    ET.SubElement(ev, "eventDateTime").text  = now
    ET.SubElement(ev, "eventTimezone").text  = "Australia/Melbourne"
    ET.SubElement(ev, "aestEventDateTime").text = now

    xml_str = ET.tostring(root, encoding="unicode")
    return xml_str, consignment_id


def send_record(xml_data: str, partition_key: str, idx: int):
    try:
        resp = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=xml_data,
            PartitionKey=partition_key
        )
        return f"✔ Record {idx} sent | SeqNum: {resp['SequenceNumber']}"
    except Exception as e:
        return f"❌ Record {idx} failed | Error: {e}"


def send_to_kinesis_parallel():
    if ec_input_records:
        total = len(ec_input_records)
        print(f"🚀 Sending {total} records from `ec_input_records` using {THREADS} threads...")
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = []
            for i, rec in enumerate(ec_input_records, start=1):
                xml   = rec["input_record"]
                # Try to parse the root 'id' attribute for partition key
                try:
                    root = ET.fromstring(xml)
                    pk   = root.attrib.get("id", str(i))
                except ET.ParseError:
                    pk = str(i)
                futures.append(executor.submit(send_record, xml, pk, i))

            for fut in as_completed(futures):
                print(fut.result())

    else:
        print(f"🚀 No input_records found → generating {RECORD_COUNT} random events using {THREADS} threads...")
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = []
            for i in range(1, RECORD_COUNT + 1):
                xml, pk = generate_event_xml()
                futures.append(executor.submit(send_record, xml, pk, i))

            for fut in as_completed(futures):
                print(fut.result())


if __name__ == "__main__":
    send_to_kinesis_parallel()
