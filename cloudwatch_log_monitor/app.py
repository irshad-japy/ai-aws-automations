# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List

# Import your existing working script WITHOUT modification
import lambda_log_monitor as lm

app = FastAPI(
    title="CloudWatch Multi Log Group Monitor (Wrapper)",
    version="1.0.0",
)

# ------------------------------
# Request model
# ------------------------------
class MonitorRequest(BaseModel):
    log_groups: Optional[List[str]] = None
    send_if_no_logs: bool = False   # Only supported feature

# ------------------------------
# Health check
# ------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "aws_region": lm.AWS_REGION,
        "log_groups": lm.LOG_GROUPS,
        "send_all_logs": lm.SEND_ALL_LOGS,
        "error_keywords": lm.ERROR_KEYWORDS,
        "timestamp_map": lm.last_timestamp_map,
    }

# ------------------------------
# Main endpoint
# ------------------------------
@app.post("/check-logs")
def check_logs(req: MonitorRequest):

    # Use override if provided, else use .env
    groups_to_process = req.log_groups or lm.LOG_GROUPS

    result = {}

    for log_group in groups_to_process:

        # Use your existing validation
        lm.ensure_log_group_exists(log_group)

        # IMPORTANT:
        # Call EXACT function signature from original script
        logs = lm.fetch_logs_for_group(log_group)

        result[log_group] = len(logs)

        if logs:
            lm.send_to_teams(log_group, logs)
        elif req.send_if_no_logs:
            heartbeat = [
                {
                    "timestamp": lm.datetime.now(lm.utc).isoformat(),
                    "message": "No logs found during this check.",
                    "log_stream": "N/A"
                }
            ]
            lm.send_to_teams(log_group, heartbeat)

    return {
        "status": "completed",
        "log_groups": groups_to_process,
        "counts": result
    }
