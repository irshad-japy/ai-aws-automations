def clone_dynamodb_tables(TABLES_TO_CLONE):
    import boto3
    import time
    from botocore.exceptions import ClientError

    dynamodb = boto3.client('dynamodb')
    resource = boto3.resource('dynamodb')

    def delete_table_if_exists(table_name):
        try:
            print(f"🔍 Checking if table '{table_name}' exists...")
            dynamodb.describe_table(TableName=table_name)
            print(f"⚠️ Table '{table_name}' exists. Deleting...")
            dynamodb.delete_table(TableName=table_name)
            resource.Table(table_name).wait_until_not_exists()
            print(f"✅ Deleted table '{table_name}'.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"ℹ️ Table '{table_name}' does not exist. Skipping deletion.")
            else:
                raise

    def clone_table(source_table, target_table):
        print(f"\n🔁 Cloning DynamoDB table from '{source_table}' to '{target_table}'")

        print("📥 Fetching source table schema...")
        desc = dynamodb.describe_table(TableName=source_table)['Table']
        schema = {
            'TableName': target_table,
            'KeySchema': desc['KeySchema'],
            'AttributeDefinitions': desc['AttributeDefinitions'],
        }

        billing_mode = desc.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
        if billing_mode == 'PAY_PER_REQUEST':
            schema['BillingMode'] = 'PAY_PER_REQUEST'
            print("⚙️ Billing mode: PAY_PER_REQUEST")
        else:
            schema['ProvisionedThroughput'] = {
                'ReadCapacityUnits': max(1, desc['ProvisionedThroughput']['ReadCapacityUnits']),
                'WriteCapacityUnits': max(1, desc['ProvisionedThroughput']['WriteCapacityUnits']),
            }
            print(f"⚙️ Billing mode: PROVISIONED with RCU: {schema['ProvisionedThroughput']['ReadCapacityUnits']}, WCU: {schema['ProvisionedThroughput']['WriteCapacityUnits']}")

        delete_table_if_exists(target_table)

        print(f"🚀 Creating table '{target_table}'...")
        dynamodb.create_table(**schema)
        resource.Table(target_table).wait_until_exists()
        print(f"✅ Table '{target_table}' is created and ACTIVE.")

        print(f"📦 Copying data from '{source_table}' to '{target_table}'...")
        src = resource.Table(source_table)
        dst = resource.Table(target_table)
        response = src.scan()
        items = response['Items']
        print(f"📊 Total items to copy: {len(items)}")

        with dst.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"✅ Data copy completed for table '{target_table}'.")

    for source, target in TABLES_TO_CLONE:
        clone_table(source, target)

    print("\n🎉 All DynamoDB tables cloned successfully.")
