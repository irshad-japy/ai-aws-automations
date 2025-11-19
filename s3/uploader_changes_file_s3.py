"""
python -m s3.uploader_changes_file_s3
"""


import os
import time
import subprocess
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

# ---------------- CONFIG ----------------
LOCAL_REPO = r"C:\Users\erirs\projects\finance-project\pdf_express"
S3_BUCKET = "tge-nihau-bucket"
S3_PREFIX = "irshad/code/"
INTERVAL_SECONDS = 300  # 5 min

EXCLUDE_PATTERNS = [".git", ".venv", "__pycache__", ".idea", ".vscode"]

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


def get_git_changes():
    """Return all changed/untracked files."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=LOCAL_REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    changes = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(" ", 1)
        if len(parts) == 2:
            relative = parts[1]
            full = os.path.join(LOCAL_REPO, relative)
            if not excluded(full):
                changes.append((relative, full))

    return changes


def upload_to_s3(local_path, full_path):
    bucket = S3_BUCKET
    base_prefix = "irshad/code"  # change if needed

    # If path is a directory → recursively upload contents
    if os.path.isdir(full_path):
        print(f"📂 Folder detected → Uploading recursively: {full_path}")

        for root, dirs, files in os.walk(full_path):
            for file in files:
                file_full_path = os.path.join(root, file)

                # Build s3 key relative to the project folder
                relative_inside_folder = os.path.relpath(file_full_path, LOCAL_REPO)
                s3_key = f"{base_prefix}/{relative_inside_folder}".replace("\\", "/")

                print(f"⬆️ Uploading file → s3://{bucket}/{s3_key}")
                s3.upload_file(file_full_path, bucket, s3_key)

        return  # folder handled completely

    # If path is a file → upload normally
    s3_key = f"{base_prefix}/{local_path}".replace("\\", "/")

    print(f"⬆️ Uploading file → s3://{bucket}/{s3_key}")
    s3.upload_file(full_path, bucket, s3_key)

# --------------- MAIN LOOP ----------------
def main():
    print("🚀 Laptop-A Git → S3 Sync Started (FAST MODE)...\n")

    while True:
        print("🔍 Checking Git changes...")
        changed_files = get_git_changes()

        if changed_files:
            print(f"📌 {len(changed_files)} files changed — uploading...")
            for relative, full in changed_files:
                upload_to_s3(relative, full)

        else:
            print("✔️ No local changes detected.")

        print(f"⏳ Waiting {INTERVAL_SECONDS} sec...\n")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
