"""
python invoke_lambda_function.py

"""

# invoke_lambda_function.py
import json
import boto3
from botocore.exceptions import ClientError

PROFILE = "personal"
REGION = "ap-south-1"
FUNCTION_NAME = "RustDeskSchedulerStack-Ec2StartStopFn0AB2EDDD-LqMYEvb7CqEQ"  # <- paste from step 2

def debug_where(session):
    sts = session.client("sts")
    ident = sts.get_caller_identity()
    print(f"Invoking as Account={ident['Account']} UserArn={ident['Arn']}")
    print(f"Region={session.region_name}")

def invoke(function_name: str, payload: dict):
    session = boto3.Session(profile_name=PROFILE, region_name=REGION)
    debug_where(session)
    lam = session.client("lambda")

    try:
        resp = lam.invoke(
            FunctionName=function_name,           # name or full ARN
            # Qualifier="prod",                   # use only if you have an alias/version
            InvocationType="RequestResponse",
            Payload=json.dumps(payload).encode("utf-8"),
        )
        print("StatusCode:", resp.get("StatusCode"))
        print("ExecutedVersion:", resp.get("ExecutedVersion"))
        body = resp["Payload"].read().decode("utf-8")
        print("Response:", body)
    except ClientError as e:
        print("Boto3 ClientError:", e.response.get("Error", {}))
        raise

if __name__ == "__main__":
    test_event = {"ping": "hello"}
    invoke(FUNCTION_NAME, test_event)
