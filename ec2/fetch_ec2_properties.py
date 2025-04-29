"""
python -m ec2.fetch_ec2_properties i-01bff7ad7bb3e0efa
"""

import boto3
import json
import sys

def get_instance_details(instance_id: str, region_name='ap-southeast-2'):
    ec2 = boto3.client('ec2', region_name=region_name)
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
    except Exception as e:
        print(f"❌ Error fetching details: {e}")
        return None

    reservations = response.get("Reservations", [])
    if not reservations or not reservations[0].get("Instances"):
        print("❌ No such instance found.")
        return None

    return reservations[0]["Instances"][0]  # Return the first matching instance

def save_to_python_file(instance_data, output_file='ec2_instance_properties.py'):
    with open(output_file, 'w') as f:
        f.write("# Auto-generated EC2 instance properties\n\n")
        f.write("ec2_instance_data = ")
        # Use default=str to convert datetime and other non-serializable types
        json.dump(instance_data, f, indent=4, default=str)
    print(f"✅ Saved EC2 instance data to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_ec2_properties.py <instance-id>")
        sys.exit(1)

    instance_id = sys.argv[1]
    region = "ap-southeast-2"  # Change this if needed
    data = get_instance_details(instance_id, region)

    if data:
        save_to_python_file(data)
