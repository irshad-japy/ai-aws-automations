"""
python -m s3.s3_downloader
"""

import os
import time
import boto3
from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
from datetime import datetime, timezone

# ---------------- CONFIG ----------------
DOWNLOAD_DIR = r"C:\Users\IrshadAl\projects\tge-projects\pod-finance\pdf_express"
BUCKET = "tge-nihau-bucket"
S3_PREFIX = "irshad/code/"
INTERVAL_SECONDS = 300  # 5 min

EXCLUDE_PATTERNS = [".git", "__pycache__", ".venv", ".idea", ".vscode"]

s3 = boto3.client("s3")

config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    multipart_chunksize=16 * 1024 * 1024,
    max_concurrency=10,
    use_threads=True,
)


# --------------- HELPERS ----------------
def excluded(path):
    return any(x in path for x in EXCLUDE_PATTERNS)


def list_s3_objects():
    paginator = s3.get_paginator("list_objects_v2")
    objs = []

    for page in paginator.paginate(Bucket=BUCKET, Prefix=S3_PREFIX):
        for item in page.get("Contents", []):
            objs.append(item)

    return objs


def download_if_newer(obj):
    key = obj["Key"]

    # ❗ Skip S3 folder placeholders
    if key.endswith("/"):
        return

    relative = key.replace(S3_PREFIX, "")
    local_path = os.path.join(DOWNLOAD_DIR, relative)

    if excluded(local_path):
        return

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    # check if file exists
    if os.path.exists(local_path):
        local_mtime = datetime.fromtimestamp(
            os.path.getmtime(local_path), timezone.utc
        )
        if local_mtime >= obj["LastModified"]:
            return  # skip if up-to-date

    print(f"⬇️ Downloading → {relative}")

    try:
        s3.download_file(
            Bucket=BUCKET,
            Key=key,
            Filename=local_path,
            Config=config
        )
    except ClientError as e:
        print(f"❌ Download failed: {e}")


# --------------- MAIN LOOP ----------------
def main():
    print("🚀 Laptop-B S3 → Local Sync Started (FAST MODE)...\n")

    while True:
        print("🔍 Checking S3 updates...")
        objects = list_s3_objects()

        for obj in objects:
            download_if_newer(obj)

        print(f"⏳ Waiting {INTERVAL_SECONDS} sec...\n")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
