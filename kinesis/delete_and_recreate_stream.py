"""
python -m kinesis.delete_and_recreate_stream
"""

import boto3
import time

# Replace with your Kinesis stream name and region
stream_name = "k-tge-nihau-stream"
region_name = "ap-southeast-2"

# Create a Kinesis client
kinesis_client = boto3.client("kinesis", region_name=region_name)

# Function to delete the stream
def delete_stream():
    try:
        response = kinesis_client.delete_stream(
            StreamName=stream_name,
        )
        print(f"Stream '{stream_name}' deletion initiated. Waiting for completion...")
        time.sleep(10)  # Wait a bit before checking the status
    except kinesis_client.exceptions.ResourceInUseException as e:
        print(f"Error: Stream '{stream_name}' is in use. Please shut down applications and try again.")
        return
    except kinesis_client.exceptions.ResourceNotFoundException as e:
        print(f"Error: Stream '{stream_name}' not found.")
        return
    except Exception as e:
        print(f"Error during stream deletion: {e}")
        return

    # Wait for the stream to be deleted (DELETED state)
    while True:
        try:
            describe_stream_response = kinesis_client.describe_stream_summary(
                StreamName=stream_name
            )
            stream_status = describe_stream_response["StreamDescriptionSummary"]["StreamStatus"]
            if stream_status == "DELETED":
                print(f"Stream '{stream_name}' has been deleted.")
                break
            elif stream_status == "DELETING":
                print(f"Stream '{stream_name}' is still deleting...")
                time.sleep(5)
            else:
                print(f"Unexpected stream status: {stream_status}")
                break
        except kinesis_client.exceptions.ResourceNotFoundException:
            print(f"Stream '{stream_name}' has been deleted.")
            break  # Stream is already gone, so we can stop waiting
        except Exception as e:
            print(f"Error describing stream: {e}")
            break

# Function to create the stream
def create_stream(shard_count=3):
    try:
        response = kinesis_client.create_stream(
            StreamName=stream_name, ShardCount=shard_count
        )
        print(f"Stream '{stream_name}' created.")
    except kinesis_client.exceptions.ResourceInUseException as e:
        print(f"Error: Stream '{stream_name}' already exists.")
    except kinesis_client.exceptions.LimitExceededException as e:
        print(f"Error: Stream creation limit exceeded.")
    except Exception as e:
        print(f"Error creating stream: {e}")

# Main execution
if __name__ == "__main__":
    # Delete the stream
    delete_stream()

    # Wait a bit for deletion to complete
    time.sleep(10)  # Give some time for deletion to complete

    # Recreate the stream
    create_stream(shard_count=1)  # Adjust shard count as needed

    print("Script completed.")