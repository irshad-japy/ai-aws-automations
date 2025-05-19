"""
python clone_scripts/clone_pipeline_ec_collector_tdf.py
"""

from clone_dynamodb import clone_dynamodb_tables
from clone_kinesis import clone_kinesis_streams
from clone_glue import clone_glue_job

def main():
    print("🚀 Starting AWS resource cloning...\n")
    env = "stg"

    # Glue
    print("\n🧪 Cloning Glue jobs...")
    glue_jobs = [
        (
            f"myteamge-dem-{env}-event-collector-tdf",  # existing job
            f"nihau-ex-glue-{env}-tdf-event",            # cloned job name
            f"s3://b-myteamge-syd-{env}-glue-dem/ird-glue-scripts/nihau-ex-glue-{env}-tdf-event.py"  # script path
        )
    ]

    # for existing_name, new_name, script_path in glue_jobs:
    #     clone_glue_job(existing_name, new_name, script_path)

    # DynamoDB
    print("📦 Cloning DynamoDB tables...")
    dynamodb_tables = [
        (f"myteamge-dem-{env}-consignment", f"nihau-ex-table-{env}-consignment"),
        (f"myteamge-dem-{env}-dirtyconsignment", f"nihau-ex-table-{env}-dirtyconsignment"),
        (f"myteamge-dem-{env}-eventstate", f"nihau-ex-table-{env}-eventstate"),
        (f"myteamge-dem-{env}-rawevent", f"nihau-ex-table-{env}-rawevent"),
        (f"myteamge-dem-{env}-references", f"nihau-ex-table-{env}-references"),
    ]
    if env =="devge":
        env = "dev"
        dynamodb_tables.append((f"mytoll_{env}_consignment_status_info", f"nihau-ex-table-{env}_consignment_status_info"))
        
    # clone_dynamodb_tables(dynamodb_tables)

    # Kinesis
    print("\n📡 Cloning Kinesis streams...")
    kinesis_streams = [
        (f"k-mytoll.syd.dem.{env}.tdf.consignment", f"k-nihau-ex.dem.{env}.tdf.consignment"),
        (f"k-mytoll.syd.dem.{env}.notification", f"k-nihau-ex.dem.{env}.notification")
    ]
    clone_kinesis_streams(kinesis_streams, action_if_exists='skip')  # Options: 'recreate', 'skip', 'update_retention'

    print("\n✅ All cloning operations completed.")

if __name__ == "__main__":
    main()
