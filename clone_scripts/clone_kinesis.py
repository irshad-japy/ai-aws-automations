def clone_kinesis_streams(STREAMS_TO_CLONE, action_if_exists='recreate'):
    import boto3
    import time
    from botocore.exceptions import ClientError

    kinesis = boto3.client('kinesis')

    def stream_exists(stream_name):
        try:
            resp = kinesis.describe_stream(StreamName=stream_name)
            return resp['StreamDescription']['StreamStatus'] in ['ACTIVE', 'CREATING', 'UPDATING']
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            else:
                raise

    def wait_for_stream_active(stream_name):
        while True:
            status = kinesis.describe_stream(StreamName=stream_name)['StreamDescription']['StreamStatus']
            if status == 'ACTIVE':
                break
            time.sleep(2)

    def delete_stream_if_exists(stream_name):
        if stream_exists(stream_name):
            kinesis.delete_stream(StreamName=stream_name, EnforceConsumerDeletion=True)
            while stream_exists(stream_name):
                time.sleep(2)

    def clone_stream(source, target):
        print(f"🔁 Cloning Kinesis stream: {source} → {target}")

        # Get source details
        source_desc = kinesis.describe_stream(StreamName=source)['StreamDescription']
        shard_count = len(source_desc['Shards'])
        retention_hours = source_desc.get('RetentionPeriodHours', 24)

        if stream_exists(target):
            if action_if_exists == 'skip':
                print(f"⏭️ Skipped existing stream: {target}")
                return
            elif action_if_exists == 'update_retention':
                existing = kinesis.describe_stream(StreamName=target)['StreamDescription']
                current_retention = existing.get('RetentionPeriodHours', 24)
                if retention_hours > current_retention:
                    kinesis.increase_stream_retention_period(
                        StreamName=target,
                        RetentionPeriodHours=retention_hours
                    )
                elif retention_hours < current_retention:
                    kinesis.decrease_stream_retention_period(
                        StreamName=target,
                        RetentionPeriodHours=retention_hours
                    )
                print(f"✅ Retention updated for stream: {target}")
                return
            elif action_if_exists == 'recreate':
                delete_stream_if_exists(target)

        # Create new stream
        kinesis.create_stream(StreamName=target, ShardCount=shard_count)
        wait_for_stream_active(target)

        if retention_hours > 24:
            kinesis.increase_stream_retention_period(
                StreamName=target,
                RetentionPeriodHours=retention_hours
            )

        print(f"✅ Stream cloned: {target}")

    for source, target in STREAMS_TO_CLONE:
        try:
            clone_stream(source, target)
        except Exception as e:
            print(f"❌ Failed to clone {source} → {target}: {str(e)}")
