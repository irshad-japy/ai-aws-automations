"""
Multi Log Group Monitor → CloudWatch → Teams

Usage:
    python lambda_log_monitor.py
"""

import os
import time
from datetime import datetime, timedelta, timezone

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

# Fixed AWS region (or load from .env)
AWS_REGION = "ap-southeast-2"

# MULTIPLE LOG GROUPS (comma separated in .env OR Python list)
LOG_GROUPS_RAW = os.getenv("LOG_GROUPS", "")
# Example in .env:
# LOG_GROUPS=/aws/lambda/tge-pdf-express-single-dxms-staging,/aws/lambda/tge-pdf-express-dxms-staging
LOG_GROUPS = [lg.strip() for lg in LOG_GROUPS_RAW.split(",") if lg.strip()]

TEAMS_WEBHOOK = os.getenv("TEAMS_WEBHOOK")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))
INIT_LOOKBACK_MINUTES = int(os.getenv("INIT_LOOKBACK_MINUTES", "60"))

SEND_ALL_LOGS = os.getenv("SEND_ALL_LOGS", "true").lower() in ("true", "1", "yes")
ERROR_KEYWORDS = [
    k.strip()
    for k in os.getenv("ERROR_KEYWORDS", "ERROR,Exception,FATAL,Traceback").split(",")
]

if not LOG_GROUPS:
    raise RuntimeError("❌ LOG_GROUPS is not configured in .env")

if not TEAMS_WEBHOOK:
    raise RuntimeError("❌ TEAMS_WEBHOOK missing in .env")

utc = timezone.utc
logs_client = boto3.client("logs", region_name=AWS_REGION)

# Maintain a separate timestamp for each log group
last_timestamp_map = {
    lg: int(
        (datetime.now(utc) - timedelta(minutes=INIT_LOOKBACK_MINUTES)).timestamp() * 1000
    )
    for lg in LOG_GROUPS
}

# ---------------------------------------------------------
# VERIFY LOG GROUP EXISTS
# ---------------------------------------------------------
def ensure_log_group_exists(log_group):
    resp = logs_client.describe_log_groups(
        logGroupNamePrefix=log_group,
        limit=1,
    )
    for lg in resp.get("logGroups", []):
        if lg["logGroupName"] == log_group:
            print(f"✅ Log group found: {log_group}")
            return

    raise RuntimeError(
        f"❌ CloudWatch log group '{log_group}' does NOT exist in region '{AWS_REGION}'."
    )

# ---------------------------------------------------------
# SEND TO MICROSOFT TEAMS
# ---------------------------------------------------------
def send_to_teams(log_group, events):
    if not events:
        return

    # Direct AWS Link for log group
    cloudwatch_url = (
        f"https://{AWS_REGION}.console.aws.amazon.com/cloudwatch/home"
        f"?region={AWS_REGION}#logsV2:log-groups/log-group/{log_group.replace('/', '$252F')}"
    )

    full_message = f"📘 *CloudWatch Logs Update for:* `{log_group}`\n"
    full_message += f"🔗 [Open in CloudWatch]({cloudwatch_url})\n\n"

    for e in events:
        full_message += (
            f"**Timestamp:** {e['timestamp']}\n"
            f"**Log Stream:** {e['log_stream']}\n"
            f"**Message:**\n```\n{e['message']}\n```\n"
            "-------------------------------\n"
        )

    payload = {"text": full_message}

    response = requests.post(TEAMS_WEBHOOK, json=payload)

    if response.status_code in (200, 202):
        print(f"📨 Sent {len(events)} logs → Teams ({log_group})")
    else:
        print(
            f"❌ Teams send failed for {log_group}: {response.status_code}, {response.text}"
        )

# ---------------------------------------------------------
# FETCH NEW LOGS FOR ONE LOG GROUP
# ---------------------------------------------------------
def fetch_logs_for_group(log_group):
    global last_timestamp_map

    start_time_ms = last_timestamp_map[log_group]

    print(
        f"🔎 Fetching logs from {log_group} since "
        f"{datetime.fromtimestamp(start_time_ms/1000, tz=utc).isoformat()}"
    )

    events = []
    next_token = None

    while True:
        params = {
            "logGroupName": log_group,
            "startTime": start_time_ms,
        }
        if next_token:
            params["nextToken"] = next_token

        res = logs_client.filter_log_events(**params)

        for e in res.get("events", []):
            msg = e["message"]
            ts = e["timestamp"]

            match = SEND_ALL_LOGS or any(k in msg for k in ERROR_KEYWORDS)

            if match:
                events.append(
                    {
                        "timestamp": datetime.fromtimestamp(ts/1000, tz=utc).isoformat(),
                        "message": msg.rstrip(),
                        "log_stream": e["logStreamName"],
                    }
                )

            last_timestamp_map[log_group] = max(
                last_timestamp_map[log_group], ts + 1
            )

        next_token = res.get("nextToken")
        if not next_token:
            break

    return events


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
def main():

    print("🟢 Starting MULTI Log Group Monitor")
    print(f"Region: {AWS_REGION}")
    print(f"Check interval: {CHECK_INTERVAL}s")
    print(f"Log groups: {LOG_GROUPS}")

    # Validate all log groups
    for lg in LOG_GROUPS:
        ensure_log_group_exists(lg)

    while True:
        try:
            for lg in LOG_GROUPS:
                logs = fetch_logs_for_group(lg)
                if logs:
                    print(f"📨 Found {len(logs)} logs for {lg}")
                    send_to_teams(lg, logs)
                else:
                    print(f"ℹ No new logs for {lg}")
        except Exception as e:
            print("❌ Error:", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
