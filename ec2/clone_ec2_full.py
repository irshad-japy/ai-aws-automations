"""
python -m ec2.clone_ec2_full
"""

import boto3
import time

def launch_clone_instance():
    REGION = "ap-southeast-2"
    AMI_ID = "ami-0def9aa861c825c8e"
    INSTANCE_TYPE = "t3.2xlarge"
    KEY_NAME = "mytoll_stg"
    SUBNET_ID = "subnet-0f8f2980c321ca6dc"
    SECURITY_GROUP_IDS = [
        "sg-0ef006c8584b63f8b",
        "sg-09059b1ac96cb204b",
        "sg-052a18ca285e92665",
        "sg-06309376c5fe3bda1",
        "sg-0ee8c89988316771a",
        "sg-0e0b7d180c0ddf661",
        "sg-0443821144e3d16c3",
        "sg-0725ffa143829ade0",
        "sg-0ee0410a4b04cd326",
        "sg-009a7fed3c1843584"
    ]
    IAM_INSTANCE_PROFILE_ARN = "arn:aws:iam::927721130786:instance-profile/Toll-DefaultEC2-Role"

    NAME_TAG = "DEMAPAUD017-clone"
    HOSTNAME_TAG = "DEMAPAUD022-clone"

    TAGS = [
        {"Key": "Business Unit", "Value": "TGE"},
        {"Key": "Application", "Value": "DEM-GLUE"},
        {"Key": "Backup", "Value": "NA"},
        {"Key": "Schedule", "Value": "24x5_Mon-Fro"},
        {"Key": "Server Role", "Value": "APP"},
        {"Key": "Application Name", "Value": "MyToll"},
        {"Key": "ManagedBy", "Value": "HCL"},
        {"Key": "Application Team", "Value": "MyToll"},
        {"Key": "CreatedBy", "Value": "HCL"},
        {"Key": "Name", "Value": NAME_TAG},
        {"Key": "Platform", "Value": "Linux"},
        {"Key": "Costcenter", "Value": "F00123"},
        {"Key": "Hostname", "Value": HOSTNAME_TAG},
        {"Key": "OS", "Value": "Amazon Linux 2 centos rhel fedora"},
        {"Key": "Division", "Value": "Corporate"},
        {"Key": "Availability", "Value": "24x7_Mon-Fri"},
        {"Key": "Owner", "Value": "Toll GBD"},
        {"Key": "Availability_New", "Value": "24*7"},
        {"Key": "Environment", "Value": "PREPROD"},
        {"Key": "Project", "Value": "dem-uplift"}
    ]

    BLOCK_DEVICES = [
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "DeleteOnTermination": True,
                "VolumeSize": 20,
                "VolumeType": "gp3"
            }
        },
        {
            "DeviceName": "/dev/xvda",
            "Ebs": {
                "DeleteOnTermination": True,
                "VolumeSize": 20,
                "VolumeType": "gp3"
            }
        }
    ]

    ec2 = boto3.resource("ec2", region_name=REGION)

    instance = ec2.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SubnetId=SUBNET_ID,
        SecurityGroupIds=SECURITY_GROUP_IDS,
        IamInstanceProfile={"Arn": IAM_INSTANCE_PROFILE_ARN},
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": TAGS
        }],
        BlockDeviceMappings=BLOCK_DEVICES,
        MinCount=1,
        MaxCount=1,
        Monitoring={"Enabled": False},
        EbsOptimized=True,
        MetadataOptions={
            'HttpTokens': 'required',
            'HttpEndpoint': 'enabled',
            'HttpPutResponseHopLimit': 1,
            'HttpProtocolIpv6': 'disabled',
            'InstanceMetadataTags': 'disabled'
        }
    )[0]

    print("🚀 Launching the safe EC2 clone...")
    instance.wait_until_running()
    instance.reload()
    print(f"✅ Instance ID: {instance.id}")
    print(f"🔗 Public IP: {instance.public_ip_address or 'N/A'}")

if __name__ == "__main__":
    launch_clone_instance()
