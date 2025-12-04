import json
import os
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EC2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION"))
INSTANCE_ID = os.getenv("INSTANCE_ID")


def _state(iid: str) -> str:
    r = EC2.describe_instances(InstanceIds=[iid])
    return r["Reservations"][0]["Instances"][0]["State"]["Name"]


def _start(iid: str):
    s = _state(iid)
    if s in ("running", "pending"):
        logger.info("%s already %s", iid, s)
        return {"ok": True, "state": s}
    EC2.start_instances(InstanceIds=[iid])
    logger.info("Start called on %s", iid)
    return {"ok": True, "state": "starting"}


def _stop(iid: str):
    s = _state(iid)
    if s in ("stopping", "stopped", "shutting-down", "terminated"):
        logger.info("%s already %s", iid, s)
        return {"ok": True, "state": s}
    EC2.stop_instances(InstanceIds=[iid])
    logger.info("Stop called on %s", iid)
    return {"ok": True, "state": "stopping"}


def handler(event, _ctx):
    """
    Accepts:
      {"action":"start|stop","instance_id":"i-..."}
    Alarm path is wired via EventBridge and still passes {action: "stop"}.
    """
    logger.info("event=%s", json.dumps(event))
    action = (event.get("action") or "").lower()
    iid = event.get("instance_id") or INSTANCE_ID
    if not action or not iid:
        raise ValueError("Need action and instance_id (or env INSTANCE_ID)")

    try:
        if action == "start":
            return _start(iid)
        if action == "stop":
            return _stop(iid)
        raise ValueError(f"Unknown action: {action}")
    except ClientError as e:
        logger.exception("AWS error")
        raise
    except Exception as e:
        logger.exception("Unhandled error")
        raise
