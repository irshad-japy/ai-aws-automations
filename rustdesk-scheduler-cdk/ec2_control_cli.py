
"""
# On-demand local CLI (optional)

python ec2_control_cli.py --region ap-south-1 --instance i-09c40c2e332da8c67 --start
python ec2_control_cli.py --region ap-south-1 --instance i-09c40c2e332da8c67 --status
python ec2_control_cli.py --region ap-south-1 --instance i-09c40c2e332da8c67 --stop

"""

import argparse, boto3

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--region", default="ap-south-1")
    p.add_argument("--instance", required=True)
    p.add_argument("--profile")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--start", action="store_true")
    g.add_argument("--stop", action="store_true")
    args = p.parse_args()

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    ec2 = session.client("ec2", region_name=args.region)

    if args.start:
        ec2.start_instances(InstanceIds=[args.instance])
        print(f"Start requested for {args.instance}")
    else:
        ec2.stop_instances(InstanceIds=[args.instance])
        print(f"Stop requested for {args.instance}")

if __name__ == "__main__":
    main()
