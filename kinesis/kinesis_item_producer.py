import boto3
import random
import string
import time
from datetime import datetime
import xml.etree.ElementTree as ET

# 🔧 Config
STREAM_NAME = "k-mytoll.syd.dem.stg.tdf.item"
REGION_NAME = "ap-southeast-2"
kinesis_client = boto3.client("kinesis", region_name=REGION_NAME)

def generate_random_string(length=8):
    """Generate random uppercase alphanumeric string."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_random_item_xml():
    now = datetime.utcnow().isoformat()

    consignment_id_base = str(random.randint(24691161240000, 24691161249999))
    consignment_id = f"{consignment_id_base}_TDF"

    # Create root element
    itemMsg = ET.Element("itemMsg", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "consignmentId": consignment_id
    })

    # srcSystem
    srcSystem = ET.SubElement(itemMsg, "srcSystem")
    srcSystem.text = "TW"

    # item node with attribute
    item = ET.SubElement(itemMsg, "item", {"action": "UN"})

    ET.SubElement(item, "consignmentNumber").text = consignment_id_base
    ET.SubElement(item, "actionDate").text = now
    ET.SubElement(item, "itemId").text = str(random.randint(1, 10))
    ET.SubElement(item, "isTrackable").text = random.choice(["true", "false"])

    # Randomly choose to include full dimension OR extended attributes
    if random.choice([True, False]):
        dimension = ET.SubElement(item, "itemDimension")
        ET.SubElement(dimension, "length", {"UOM": "cm"}).text = str(random.randint(50, 200))
        ET.SubElement(dimension, "height", {"UOM": "cm"}).text = str(random.randint(50, 200))
        ET.SubElement(dimension, "width", {"UOM": "cm"}).text = str(random.randint(50, 200))
        ET.SubElement(dimension, "totalCubic", {"UOM": "m3"}).text = str(round(random.uniform(0.3, 1.0), 3))
        ET.SubElement(dimension, "sequence").text = str(random.randint(1, 3))
        ET.SubElement(dimension, "cubicMultiplier").text = str(random.randint(1, 10))
        ET.SubElement(dimension, "quantity").text = str(random.randint(1, 10))
    else:
        ET.SubElement(item, "commodityType").text = str(random.randint(1, 10))
        ET.SubElement(item, "itemDesc").text = f"T {generate_random_string(8)}"
        ET.SubElement(item, "senderRef").text = str(random.randint(80000000, 89999999))
        ET.SubElement(item, "receiverRef").text = str(random.randint(4000000000, 4999999999))
        ET.SubElement(item, "itemWeight").text = str(random.randint(1000, 15000))
        ET.SubElement(item, "itemCount").text = str(random.randint(0, 10))
        ET.SubElement(item, "palletCount").text = str(random.randint(1, 20))

    return ET.tostring(itemMsg, encoding="unicode"), consignment_id

def send_to_kinesis():
    for i in range(5):  # Send 5 sample records
        xml_data, partition_key = generate_random_item_xml()

        print(f"Sending XML to stream '{STREAM_NAME}':\n{xml_data}\n")

        response = kinesis_client.put_record(
            StreamName=STREAM_NAME,
            Data=xml_data,
            PartitionKey=partition_key
        )
        print(f"✔ SequenceNumber: {response['SequenceNumber']}\n")

        time.sleep(0.5)  # Slight delay to simulate stream

if __name__ == "__main__":
    send_to_kinesis()
