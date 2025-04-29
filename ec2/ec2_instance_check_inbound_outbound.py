"""
python -m ec2.ec2_instance_check_inbound_outbound
"""

import boto3

def check_ssh_access(instance_id):
    ec2 = boto3.client('ec2')

    # Get instance details
    instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    security_group_ids = [sg['GroupId'] for sg in instance['SecurityGroups']]

    print(f"Checking SSH access for instance: {instance_id}")
    print(f"Security Groups: {security_group_ids}")

    # Check security group rules
    for sg_id in security_group_ids:
        sg = ec2.describe_security_groups(GroupIds=[sg_id])['SecurityGroups'][0]
        print(f"\nSecurity Group: {sg['GroupName']} ({sg['GroupId']})")

        # Check inbound rules
        inbound_ssh_allowed = False
        for rule in sg['IpPermissions']:
            if rule.get('FromPort') == 22 and rule.get('ToPort') == 22:
                for ip_range in rule.get('IpRanges', []):
                    print(f"Inbound SSH allowed from: {ip_range['CidrIp']}")
                    inbound_ssh_allowed = True
                for ipv6_range in rule.get('Ipv6Ranges', []):
                    print(f"Inbound SSH allowed from (IPv6): {ipv6_range['CidrIpv6']}")
                    inbound_ssh_allowed = True

        if not inbound_ssh_allowed:
            print("No inbound SSH rule found.")

        # Check outbound rules
        outbound_ssh_allowed = False
        for rule in sg['IpPermissionsEgress']:
            if rule.get('FromPort') == 22 and rule.get('ToPort') == 22:
                for ip_range in rule.get('IpRanges', []):
                    print(f"Outbound SSH allowed to: {ip_range['CidrIp']}")
                    outbound_ssh_allowed = True
                for ipv6_range in rule.get('Ipv6Ranges', []):
                    print(f"Outbound SSH allowed to (IPv6): {ipv6_range['CidrIpv6']}")
                    outbound_ssh_allowed = True

        if not outbound_ssh_allowed:
            print("No outbound SSH rule found.")

if __name__ == "__main__":
    # Replace with your EC2 instance ID
    # instance_id = "i-0b89496664935e18c"  # Example instance ID
    instance_id = "i-01bff7ad7bb3e0efa"  # Example instance ID
    check_ssh_access(instance_id)