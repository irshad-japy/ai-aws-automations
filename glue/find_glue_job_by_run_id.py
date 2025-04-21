"""
python -m aws.aws_glue.find_glue_job_by_run_id
"""

import boto3
from botocore.exceptions import ClientError

def find_glue_job_name_by_run_id(target_run_id):
    glue_client = boto3.client('glue')
    
    # Step 1: List all Glue jobs
    paginator = glue_client.get_paginator('get_jobs')
    job_names = []
    
    for page in paginator.paginate():
        for job in page['Jobs']:
            job_names.append(job['Name'])

    print(f"Checking {len(job_names)} jobs...")

    # Step 2: Iterate over job names and check job run ID
    for job_name in job_names:
        try:
            response = glue_client.get_job_run(JobName=job_name, RunId=target_run_id)
            # If no exception, match found
            print(f"✅ Found! Job Name: {job_name} matches Run ID: {target_run_id}")
            return job_name
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityNotFoundException':
                continue  # RunId not found for this job
            else:
                print(f"❌ Unexpected error for job {job_name}: {e}")
                continue

    print("❌ No job found with the given JobRunId.")
    return None

# Example usage
# job_run_id = 'jr_c43b5e6891832530ec9e3a586fce618f83c926a434d7a60508095c1d208aaa77'
job_run_id = 'jr_16e57c171467e6596eb07de96c35ab9b76d1dd4a2aa6578b3f036cfe1e935161'
find_glue_job_name_by_run_id(job_run_id)
