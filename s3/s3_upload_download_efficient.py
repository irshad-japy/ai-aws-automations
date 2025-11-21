"""
python -m s3.s3_upload_download_efficient
"""

# s3_transfer_module_final.py

import boto3
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create S3 client
s3_client = boto3.client('s3')

# Lock for thread-safe progress bars
lock = threading.Lock()

# Retry decorator for robustness
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def upload_file(file_path, bucket_name, s3_key):
    """Upload a single file to S3 with retry and progress bar."""
    try:
        config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=8 * 1024 * 1024,  # 8MB
            multipart_chunksize=16 * 1024 * 1024, # 16MB
            max_concurrency=10,
            use_threads=True
        )

        filesize = os.path.getsize(file_path)

        with tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Uploading {os.path.basename(file_path)}") as pbar:
            def progress_callback(bytes_amount):
                with lock:
                    pbar.update(bytes_amount)

            s3_client.upload_file(
                Filename=file_path,
                Bucket=bucket_name,
                Key=s3_key,
                Callback=progress_callback,
                Config=config
            )

        logger.info(f"Uploaded {file_path} to s3://{bucket_name}/{s3_key}")
    except ClientError as e:
        logger.error(f"Failed to upload {file_path}: {e}")
        raise e

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def download_file(bucket_name, s3_key, download_path):
    """Download a single file from S3 with retry and progress bar."""
    try:
        os.makedirs(os.path.dirname(download_path), exist_ok=True)

        response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        filesize = response['ContentLength']

        with tqdm(total=filesize, unit='B', unit_scale=True, desc=f"Downloading {os.path.basename(download_path)}") as pbar:
            def progress_callback(bytes_amount):
                with lock:
                    pbar.update(bytes_amount)

            s3_client.download_file(
                Bucket=bucket_name,
                Key=s3_key,
                Filename=download_path,
                Callback=progress_callback
            )

        logger.info(f"Downloaded s3://{bucket_name}/{s3_key} to {download_path}")
    except ClientError as e:
        logger.error(f"Failed to download {s3_key}: {e}")
        raise e

def upload_folder(local_folder, bucket_name, s3_prefix="", max_workers=10):
    """Upload a local folder to S3."""
    all_files = []
    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")
            all_files.append((local_path, bucket_name, s3_key))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(upload_file, *file_args) for file_args in all_files]
        for future in as_completed(futures):
            future.result()

def download_folder(bucket_name, s3_prefix, local_folder, max_workers=10):
    """Download an S3 folder to local."""
    paginator = s3_client.get_paginator('list_objects_v2')
    all_objects = []
    for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                s3_key = obj['Key']
                relative_path = os.path.relpath(s3_key, s3_prefix)
                local_path = os.path.join(local_folder, relative_path)
                all_objects.append((bucket_name, s3_key, local_path))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_file, *obj_args) for obj_args in all_objects]
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    # import pdb; pdb.set_trace()
    # ✨ Define project root
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    # ✨ Define upload and download folders
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "data", "upload_folder")
    DOWNLOAD_FOLDER = os.path.join(PROJECT_ROOT, "data", "download_folder")

    # ✨ Create folders if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    # 📦 Config dict
    config = {
        "operation": "download",  # "upload" or "download"
        "upload_local_folder": UPLOAD_FOLDER,
        "download_local_folder": DOWNLOAD_FOLDER,
        "bucket": "tge-nihau-bucket",
        "s3_prefix": "irshad/noncode/",  # S3 folder path
        "max_workers": 10
    }

    if config["operation"] == "upload":
        upload_folder(
            local_folder=config["upload_local_folder"],
            bucket_name=config["bucket"],
            s3_prefix=config["s3_prefix"],
            max_workers=config["max_workers"]
        )
    elif config["operation"] == "download":
        download_folder(
            bucket_name=config["bucket"],
            s3_prefix=config["s3_prefix"],
            local_folder=config["download_local_folder"],
            max_workers=config["max_workers"]
        )
    else:
        raise ValueError(f"Unknown operation: {config['operation']}")
