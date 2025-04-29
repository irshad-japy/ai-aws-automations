# Auto-generated EC2 instance properties

# Auto-generated EC2 instance properties

ec2_instance_data = {
    "AmiLaunchIndex": 0,
    "ImageId": "ami-xxxxxxxxxxxxxxxxx",  # Redacted
    "InstanceId": "i-xxxxxxxxxxxxxxxxx",  # Redacted
    "InstanceType": "t2.large",
    "KeyName": "REDACTED",  # Redacted
    "LaunchTime": "2025-04-25 11:00:00+00:00",
    "Monitoring": {
        "State": "disabled"
    },
    "Placement": {
        "AvailabilityZone": "ap-southeast-2b",
        "GroupName": "",
        "Tenancy": "default"
    },
    "PrivateDnsName": "ip-10-xx-xx-xx.ap-southeast-2.compute.internal",  # Redacted
    "PrivateIpAddress": "10.xx.xx.xx",  # Redacted
    "ProductCodes": [],
    "PublicDnsName": "",
    "State": {
        "Code": 16,
        "Name": "running"
    },
    "StateTransitionReason": "",
    "SubnetId": "subnet-xxxxxxxxxxxxxxxxx",  # Redacted
    "VpcId": "vpc-xxxxxxxxxxxxxxxxx",  # Redacted
    "Architecture": "x86_64",
    "BlockDeviceMappings": [
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "AttachTime": "2023-08-25 12:22:41+00:00",
                "DeleteOnTermination": False,
                "Status": "attached",
                "VolumeId": "vol-xxxxxxxxxxxxxxxxx"  # Redacted
            }
        }
    ],
    "ClientToken": "REDACTED",  # Redacted
    "EbsOptimized": False,
    "EnaSupport": False,
    "Hypervisor": "xen",
    "IamInstanceProfile": {
        "Arn": "arn:aws:iam::xxxxxxxxxxxx:instance-profile/REDACTED",  # Redacted
        "Id": "AIPAxxxxxxxxxxxxxxxxx"  # Redacted
    },
    "NetworkInterfaces": [
        {
            "Attachment": {
                "AttachTime": "2023-03-16 10:48:39+00:00",
                "AttachmentId": "eni-attach-xxxxxxxxxxxxxxxxx",  # Redacted
                "DeleteOnTermination": True,
                "DeviceIndex": 0,
                "Status": "attached",
                "NetworkCardIndex": 0
            },
            "Description": "Primary network interface",
            "Groups": [
                {"GroupName": "REDACTED", "GroupId": "sg-xxxxxxxxxxxxxxxxx"},  # Redacted
                {"GroupName": "REDACTED", "GroupId": "sg-xxxxxxxxxxxxxxxxx"},  # Redacted
                {"GroupName": "REDACTED", "GroupId": "sg-xxxxxxxxxxxxxxxxx"}   # Redacted
            ],
            "Ipv6Addresses": [],
            "MacAddress": "02:xx:xx:xx:xx:xx",  # Redacted
            "NetworkInterfaceId": "eni-xxxxxxxxxxxxxxxxx",  # Redacted
            "OwnerId": "xxxxxxxxxxxx",  # Redacted
            "PrivateDnsName": "ip-10-xx-xx-xx.ap-southeast-2.compute.internal",  # Redacted
            "PrivateIpAddress": "10.xx.xx.xx",  # Redacted
            "PrivateIpAddresses": [
                {
                    "Primary": True,
                    "PrivateDnsName": "ip-10-xx-xx-xx.ap-southeast-2.compute.internal",  # Redacted
                    "PrivateIpAddress": "10.xx.xx.xx"  # Redacted
                }
            ],
            "SourceDestCheck": True,
            "Status": "in-use",
            "SubnetId": "subnet-xxxxxxxxxxxxxxxxx",  # Redacted
            "VpcId": "vpc-xxxxxxxxxxxxxxxxx",  # Redacted
            "InterfaceType": "interface"
        }
    ],
    "RootDeviceName": "/dev/sda1",
    "RootDeviceType": "ebs",
    "SecurityGroups": [
        {"GroupName": "REDACTED", "GroupId": "sg-xxxxxxxxxxxxxxxxx"},  # Redacted
        {"GroupName": "REDACTED", "GroupId": "sg-xxxxxxxxxxxxxxxxx"},  # Redacted
        {"GroupName": "REDACTED", "GroupId": "sg-xxxxxxxxxxxxxxxxx"}   # Redacted
    ],
    "SourceDestCheck": True,
    "Tags": [
        {"Key": "Used For", "Value": "REDACTED"},  # Redacted
        {"Key": "Name", "Value": "REDACTED"},  # Redacted
        {"Key": "Application Name", "Value": "REDACTED"},  # Redacted
        {"Key": "Schedule", "Value": "REDACTED"},  # Redacted
        {"Key": "Environment", "Value": "REDACTED"},  # Redacted
        {"Key": "Application", "Value": "REDACTED"},  # Redacted
        {"Key": "OS", "Value": "Amazon Linux 2"},
        {"Key": "Platform", "Value": "Linux"}
    ],
    "VirtualizationType": "hvm",
    "CpuOptions": {
        "CoreCount": 2,
        "ThreadsPerCore": 1
    },
    "CapacityReservationSpecification": {
        "CapacityReservationPreference": "open"
    },
    "HibernationOptions": {
        "Configured": False
    },
    "MetadataOptions": {
        "State": "applied",
        "HttpTokens": "required",
        "HttpPutResponseHopLimit": 1,
        "HttpEndpoint": "enabled",
        "HttpProtocolIpv6": "disabled",
        "InstanceMetadataTags": "disabled"
    },
    "EnclaveOptions": {
        "Enabled": False
    },
    "PlatformDetails": "Linux/UNIX",
    "UsageOperation": "RunInstances",
    "UsageOperationUpdateTime": "2023-03-16 10:48:39+00:00",
    "PrivateDnsNameOptions": {
        "HostnameType": "ip-name",
        "EnableResourceNameDnsARecord": True,
        "EnableResourceNameDnsAAAARecord": False
    },
    "MaintenanceOptions": {
        "AutoRecovery": "default"
    },
    "CurrentInstanceBootMode": "legacy-bios"
}