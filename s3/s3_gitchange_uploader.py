"""
python -m s3.s3_gitchange_uploader
"""

import os
import time
import subprocess
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

# ------------------------------------------------------
# CONFIG
# ------------------------------------------------------
POD_FINANCE_PROJECTS = ['oracle-ebs', 'pdf_express', 'pdf_express_nz', 'rapid_apply']

LOCAL_REPO = r"C:\Users\erirs\projects\tge-projects\pod-finance"
S3_BUCKET = "tge-nihau-bucket"
S3_PREFIX = "irshad/code/pod-finance"
INTERVAL_SECONDS = 300  # 5 min

EXCLUDE_PATTERNS = [".git", ".venv", "__pycache__", ".idea", ".vscode"]

s3 = boto3.client("s3")

config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,
    multipart_chunksize=16 * 1024 * 1024,
    max_concurrency=10,
    use_threads=True
)

# ------------------------------------------------------
# HELPERS
# ------------------------------------------------------
def excluded(path):
    return any(pattern in path for pattern in EXCLUDE_PATTERNS)

def get_project_path(project):
    return os.path.join(LOCAL_REPO, project)

def get_git_changes(project):
    project_path = get_project_path(project)

    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    changed_paths = []

    for line in result.stdout.splitlines():
        parts = line.strip().split(" ", 1)
        if len(parts) != 2:
            continue

        relative = parts[1]
        full = os.path.join(project_path, relative)

        if excluded(full):
            continue

        changed_paths.append((relative, full))

    return changed_paths

def upload_to_s3(project, relative_path, full_path):
    """
    Upload a file OR a whole folder recursively.
    Maintains folder structure in S3.
    """

    # --------------------------
    # CASE 1: FULL_PATH IS FILE
    # --------------------------
    if os.path.isfile(full_path):
        s3_key = f"{S3_PREFIX}/{project}/{relative_path}".replace("\\", "/")
        print(f"⬆️ Uploading file → s3://{S3_BUCKET}/{s3_key}")

        s3.upload_file(
            Filename=full_path,
            Bucket=S3_BUCKET,
            Key=s3_key,
            Config=config
        )
        return

    # --------------------------
    # CASE 2: FULL_PATH IS FOLDER
    # --------------------------
    if os.path.isdir(full_path):
        print(f"📂 Uploading folder recursively → {full_path}")

        for root, dirs, files in os.walk(full_path):
            for file in files:
                file_full_path = os.path.join(root, file)

                # relative inside the project folder
                relative_inside = os.path.relpath(file_full_path, get_project_path(project))

                # final S3 key
                s3_key = f"{S3_PREFIX}/{project}/{relative_inside}".replace("\\", "/")

                print(f"⬆️ Uploading → s3://{S3_BUCKET}/{s3_key}")

                s3.upload_file(
                    Filename=file_full_path,
                    Bucket=S3_BUCKET,
                    Key=s3_key,
                    Config=config
                )
        return

    # --------------------------
    # Invalid paths
    # --------------------------
    print(f"⚠️ Skipping unknown path type: {full_path}")


# ------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------
def main():
    print("🚀 Multi-Project Git → S3 Sync Started (FAST MODE)\n")

    while True:
        print("🔍 Checking Git changes...\n")

        for project in POD_FINANCE_PROJECTS:
            print(f"📁 Project: {project}")
            changes = get_git_changes(project)

            if changes:
                print(f"📌 {len(changes)} changed files found")
                for relative, full in changes:
                    upload_to_s3(project, relative, full)
            else:
                print("✔️ No changes detected.")

            print("-" * 60)

        print(f"⏳ Sleeping {INTERVAL_SECONDS} seconds...\n")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
