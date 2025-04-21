def clone_glue_job(existing_job_name, cloned_job_name, new_script_location):
    import boto3
    import copy
    from urllib.parse import urlparse
    from botocore.exceptions import ClientError

    glue = boto3.client('glue', region_name='ap-southeast-2')
    s3 = boto3.client('s3')

    try:
        job_def = glue.get_job(JobName=existing_job_name)['Job']
        original_script = job_def['Command']['ScriptLocation']
        args = job_def['DefaultArguments'].copy()
        for k in ['--job-bookmark-option', '--job-id', '--TempDir', '--enable-continuous-cloudwatch-log']:
            args.pop(k, None)

        payload = {
            'Role': job_def['Role'],
            'ExecutionProperty': job_def.get('ExecutionProperty', {}),
            'Command': copy.deepcopy(job_def['Command']),
            'DefaultArguments': args,
            'Description': f"Cloned from {existing_job_name}",
            'MaxRetries': job_def.get('MaxRetries', 0),
            'Timeout': job_def.get('Timeout', 2880),
            'GlueVersion': job_def.get('GlueVersion', '4.0'),
            'NumberOfWorkers': job_def.get('NumberOfWorkers', 10),
            'WorkerType': job_def.get('WorkerType', 'G.1X'),
            'Connections': job_def.get('Connections', {}),
            'NotificationProperty': job_def.get('NotificationProperty', {})
        }

        try:
            glue.get_job(JobName=cloned_job_name)
            glue.update_job(JobName=cloned_job_name, JobUpdate=payload)
        except glue.exceptions.EntityNotFoundException:
            glue.create_job(Name=cloned_job_name, Tags=job_def.get('Tags', {}), **payload)

        # Copy script
        src = urlparse(original_script)
        dst = urlparse(new_script_location)
        s3.copy_object(
            Bucket=dst.netloc,
            CopySource={'Bucket': src.netloc, 'Key': src.path.lstrip('/')},
            Key=dst.path.lstrip('/')
        )

        payload['Command']['ScriptLocation'] = new_script_location
        glue.update_job(JobName=cloned_job_name, JobUpdate=payload)

    except ClientError as e:
        print(f"AWS error: {e.response['Error']['Message']}")
    except Exception as ex:
        print(f"General error: {ex}")
