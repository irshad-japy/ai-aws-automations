"""
python clone_lambda.py  
"""

import boto3
import sys
import json

def clone_lambda_function(source_function_name, new_function_name):
    lambda_client = boto3.client("lambda")

    # Get the source function configuration
    try:
        response = lambda_client.get_function(FunctionName=source_function_name)
    except Exception as e:
        print(f"Error fetching source Lambda: {e}")
        return

    config = response["Configuration"]
    code = response["Code"]

    # Get the deployment package (S3 bucket + key if stored in S3)
    if "RepositoryType" in code and code["RepositoryType"] == "S3":
        code_params = {
            "S3Bucket": code["Location"].split("/")[2],
            "S3Key": "/".join(code["Location"].split("/")[3:])
        }
    else:
        # If not S3-backed, fetch zip file directly
        print("Fetching deployment package from Lambda...")
        code_bytes = lambda_client.get_function_code_signing_config(
            FunctionName=source_function_name
        )
        code_params = {
            "ZipFile": code_bytes
        }

    # Create the new Lambda function
    try:
        new_function = lambda_client.create_function(
            FunctionName=new_function_name,
            Runtime="python3.12",  # Force Python 3.12
            Role=config["Role"],
            Handler=config["Handler"],
            Code={"S3Bucket": response["Code"]["RepositoryType"], "S3Key": response["CodeSha256"]} if "S3Bucket" in code else {"ZipFile": lambda_client.get_function(FunctionName=source_function_name)["Code"]["Location"]},
            Description=config.get("Description", ""),
            Timeout=config["Timeout"],
            MemorySize=config["MemorySize"],
            Environment=config.get("Environment", {}),
            Publish=True,
            VpcConfig=config.get("VpcConfig", {}),
            Layers=config.get("Layers", []),
            PackageType=config.get("PackageType", "Zip"),
            Architectures=config.get("Architectures", ["x86_64"])
        )
        print(f"✅ Lambda function '{new_function_name}' created successfully.")
    except Exception as e:
        print(f"Error creating new Lambda: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clone_lambda.py <source_lambda_name> <new_lambda_name>")
        sys.exit(1)

    source_lambda = "tge-pdf-express-statement-consolidate-staging"
    new_lambda = "my-duplicate-lambda"

    clone_lambda_function(source_lambda, new_lambda)
