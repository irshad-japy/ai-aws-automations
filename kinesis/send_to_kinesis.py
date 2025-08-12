"""
python -m kinesis.send_to_kinesis
"""

import boto3
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def send_data_to_kinesis(data, stream_name, region_name='ap-southeast-2'):
    try:
        # Initialize a session using Amazon Glue
        session = boto3.Session()
        kinesis_client = session.client('kinesis', region_name=region_name)
        
        # Send the data to the Kinesis stream
        response = kinesis_client.put_record(
            StreamName=stream_name,
            Data=data,
            PartitionKey="partition_key"
        )
        
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
# data = '<?xml version=\"1.0\" encoding = \"UTF-8\" ?>  <eventMsg xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" consignmentNumber = \"TGEB600841\" consignmentId = \"TGEB600841_PRIO\" > <srcSystem>PRIO</srcSystem> <event action = \"UN\" >  <type>item</type><itemId>00093275103945581826</itemId><eventCode>10</eventCode><eventDescription>Pickup at 10</eventDescription><itemCount>1</itemCount><eventLocation><addressLine1>Nsw Fire Brigade City of Sydne</addressLine1><addressLine2>211-217 Castlereagh St</addressLine2><suburb>SYDNEY</suburb><state>NSW</state><country>AU</country><postCode>2000</postCode></eventLocation><businessUnit>PRIO</businessUnit><eventDateTime>2025-04-30T15:46:15Z</eventDateTime><eventTimezone>+10:00</eventTimezone><containerId/><routeId>MEL__10</routeId><scanType>Physical</scanType><additionalAttributes><attribName>vehicleType</attribName><attribValue>VAN</attribValue></additionalAttributes></event>  </eventMsg>'
# data = '{"IsB2cService": true, "busUnit": "FAST", "consignmentId": "397ce6412ad7a66a20ec25891d4aea4120228b50", "consignmentNumber": "2361", "eventDateTime": "2025/06/10 00:00:00", "senderName": "TOLL PRIORITY", "receiverName": "TOLL PRIORITY", "milestone": "SHPCRE", "isException": "false", "publicDescription": "Shipment Created", "trackedEntityType": "shipment", "stopDetails": [{"stopNumber": "1", "companyName": "TOLL PRIORITY", "stopAddress": {"suburb": "CARDIFF", "state": "NSW", "country": "Australia", "postCode": "2285", "latitude": "-32.911035", "longitude": "151.618744", "addrLine1": "ARUMA PL", "addrLine2": null}, "sequence": 1, "references": "{}"}], "InvolvedParty.billTo.Account": "SYMPER", "InvolvedParty.billTo.Location.state": "NSW", "senderAccount": "SYMPER", "receiverAccount": null}'
# data = '{"IsB2cService": true, "busUnit": "PRIO", "consignmentId": "347cad5015c569a2473fae3e54da8236aeb02cda", "consignmentNumber": "BABT814144", "eventDateTime": "2025/06/17 19:41:48", "senderName": "TOLL PRIORITY", "receiverName": "CHILDRENS HEALTH QLD HOSPITAL", "milestone": "AWTCOL", "isException": "false", "publicDescription": "DELIVERED TO SERVICE HUB", "trackedEntityType": "SHIPMENT", "stopDetails": [{"stopNumber": "1", "companyName": "TOLL PRIORITY", "stopAddress": {"suburb": "CARDIFF", "state": "NSW", "country": "Australia", "postCode": "2285", "latitude": "-32.911035", "longitude": "151.618744", "addrLine1": "ARUMA PL", "addrLine2": null}, "sequence": 1, "references": "{}"}], "InvolvedParty.billTo.Account": "SYMPER", "InvolvedParty.billTo.Location.state": "NSW", "senderAccount": "SYMPER", "receiverAccount": null}'
data = '{     "eventDateTime": "2025/06/17 19:41:48",     "senderAccount": "200bhy",     "busUnit": "PRIO",     "PortalName": "",     "receiverName": "CHILDRENS HEALTH QLD HOSPITAL",     # "consignmentId": "347cad5015c569a2473fae3e54da8236aeb02cda",     "consignmentId": "72bc28e001acd077912c2677d61b9a4d56a9ad6d",     "publicDescription": "DELIVERED TO SERVICE HUB",     "adpName": "LYGON EVERYDAY CHEMIST",     "consignmentNumber": "BABT814144",     "IsB2cService": True,     "InvolvedParty.billTo.Account": "2005PL",     "eventCode": "1$$DA",     "adpLocation": {         "country": "AU",         "addressLine1": "475 LYGON ST",         "suburb": "BRUNSWICK EAST",         "postCode": "3057",         "state": "VIC"     },     "routeId": "3424   ",     "eta": "2025/06/17 00:00:00",     "milestone": "AWTCOL",     # "milestone": "COLLCTD",     "MerchantName": "",     "trackedEntityType": "SHIPMENT",     "adpOpeningHours": "M-F:09:00-20:00;SA:09:00-17:00;SU:10:00-16:00",     "IsBignBulkyService": False,     "vehicleType": "VEHICLE <4.5 T",     "notifications": {},     "adpDisplayHint": "true" }'

def main():
    # stream_name = "k-mytoll.syd.dem.stg.notification"
    stream_name = "k-tge-nihau-stream"

    response = send_data_to_kinesis(data, stream_name)
    print(f"sent data to kinesis stream {stream_name}")
    print(response)

if __name__ == "__main__":
    main()

