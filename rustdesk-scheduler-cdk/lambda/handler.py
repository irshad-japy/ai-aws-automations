import json
import os
import logging
import time
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EC2 = boto3.client("ec2", region_name=os.getenv("AWS_REGION"))
INSTANCE_ID = os.getenv("INSTANCE_ID")


def _get_instance_state(instance_id: str) -> str:
    """Get the current state of an EC2 instance"""
    try:
        response = EC2.describe_instances(InstanceIds=[instance_id])
        return response["Reservations"][0]["Instances"][0]["State"]["Name"]
    except (IndexError, KeyError) as e:
        logger.error(f"Failed to get instance state for {instance_id}: {e}")
        raise ValueError(f"Instance {instance_id} not found or invalid response")


def _wait_for_state(instance_id: str, target_state: str, max_wait_seconds: int = 30) -> bool:
    """Wait for instance to reach target state"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        current_state = _get_instance_state(instance_id)
        if current_state == target_state:
            return True
        time.sleep(2)
    
    return False

def _start_instance(instance_id: str) -> Dict[str, Any]:
    """Start an EC2 instance"""
    current_state = _get_instance_state(instance_id)
    
    if current_state in ("running", "pending"):
        logger.info(f"Instance {instance_id} already {current_state}")
        return {"ok": True, "state": current_state, "action": "start", "message": f"Already {current_state}"}
    
    if current_state in ("shutting-down", "terminated"):
        logger.warning(f"Cannot start instance {instance_id} in state {current_state}")
        return {"ok": False, "state": current_state, "action": "start", "message": f"Cannot start instance in {current_state} state"}
    
    try:
        EC2.start_instances(InstanceIds=[instance_id])
        logger.info(f"Start command sent to instance {instance_id}")
        return {"ok": True, "state": "starting", "action": "start", "message": "Start command sent successfully"}
    except ClientError as e:
        logger.error(f"Failed to start instance {instance_id}: {e}")
        return {"ok": False, "state": current_state, "action": "start", "message": f"Failed to start: {str(e)}"}


def _stop_instance(instance_id: str) -> Dict[str, Any]:
    """Stop an EC2 instance"""
    current_state = _get_instance_state(instance_id)
    
    if current_state in ("stopping", "stopped", "shutting-down", "terminated"):
        logger.info(f"Instance {instance_id} already {current_state}")
        return {"ok": True, "state": current_state, "action": "stop", "message": f"Already {current_state}"}
    
    if current_state == "pending":
        logger.warning(f"Instance {instance_id} is starting, waiting before stopping...")
        # Wait a bit for instance to finish starting
        time.sleep(10)
        current_state = _get_instance_state(instance_id)
    
    try:
        EC2.stop_instances(InstanceIds=[instance_id])
        logger.info(f"Stop command sent to instance {instance_id}")
        return {"ok": True, "state": "stopping", "action": "stop", "message": "Stop command sent successfully"}
    except ClientError as e:
        logger.error(f"Failed to stop instance {instance_id}: {e}")
        return {"ok": False, "state": current_state, "action": "stop", "message": f"Failed to stop: {str(e)}"}


def _restart_instance(instance_id: str) -> Dict[str, Any]:
    """Restart an EC2 instance (stop then start)"""
    logger.info(f"Restarting instance {instance_id}")
    
    current_state = _get_instance_state(instance_id)
    
    # If already stopped, just start it
    if current_state in ("stopped",):
        logger.info(f"Instance {instance_id} already stopped, starting it")
        return _start_instance(instance_id)
    
    # If not running, can't restart
    if current_state not in ("running", "stopping", "pending"):
        logger.warning(f"Cannot restart instance {instance_id} in state {current_state}")
        return {"ok": False, "state": current_state, "action": "restart", 
                "message": f"Cannot restart instance in {current_state} state"}
    
    try:
        # First stop the instance
        stop_result = _stop_instance(instance_id)
        if not stop_result["ok"]:
            return {"ok": False, "state": current_state, "action": "restart", 
                    "message": f"Failed to stop instance during restart: {stop_result['message']}"}
        
        # Wait for instance to be stopped
        logger.info(f"Waiting for instance {instance_id} to stop...")
        if not _wait_for_state(instance_id, "stopped", max_wait_seconds=60):
            logger.warning(f"Instance {instance_id} did not stop within timeout, trying to start anyway")
        
        # Then start it
        time.sleep(2)  # Brief pause before starting
        start_result = _start_instance(instance_id)
        
        if start_result["ok"]:
            return {"ok": True, "state": "restarting", "action": "restart", 
                    "message": "Restart sequence initiated successfully"}
        else:
            return {"ok": False, "state": _get_instance_state(instance_id), "action": "restart",
                    "message": f"Restart failed during start phase: {start_result['message']}"}
            
    except Exception as e:
        logger.error(f"Error during restart of instance {instance_id}: {e}")
        return {"ok": False, "state": _get_instance_state(instance_id), "action": "restart",
                "message": f"Restart failed: {str(e)}"}


def _handle_multiple_instances(instance_ids: List[str], action: str) -> Dict[str, Any]:
    """Handle actions on multiple instances"""
    results = []
    overall_success = True
    
    for instance_id in instance_ids:
        try:
            if action == "start":
                result = _start_instance(instance_id)
            elif action == "stop":
                result = _stop_instance(instance_id)
            elif action == "restart":
                result = _restart_instance(instance_id)
            else:
                result = {"ok": False, "state": "unknown", "action": action, 
                         "message": f"Unknown action: {action}"}
            
            result["instance_id"] = instance_id
            results.append(result)
            
            if not result["ok"]:
                overall_success = False
                
        except Exception as e:
            logger.error(f"Error processing instance {instance_id}: {e}")
            results.append({
                "ok": False, 
                "state": "error", 
                "action": action,
                "instance_id": instance_id,
                "message": f"Processing error: {str(e)}"
            })
            overall_success = False
    
    return {
        "ok": overall_success,
        "action": action,
        "results": results,
        "total_instances": len(instance_ids),
        "successful": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"])
    }


def handler(event, context):
    """
    Enhanced Lambda handler for EC2 instance management
    
    Accepts:
      Single instance: {"action": "start|stop|restart", "instance_id": "i-..."}
      Multiple instances: {"action": "start|stop|restart", "instance_ids": ["i-...", "i-..."]}
      Environment fallback: {"action": "start|stop|restart"} (uses INSTANCE_ID env var)
    
    Returns:
      {"ok": bool, "state": str, "action": str, "message": str, ...}
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        action = (event.get("action") or "").lower().strip()
        if not action:
            raise ValueError("Missing 'action' parameter")
        
        if action not in ["start", "stop", "restart"]:
            raise ValueError(f"Invalid action '{action}'. Supported actions: start, stop, restart")
        
        # Handle multiple instances
        instance_ids = event.get("instance_ids")
        if instance_ids:
            if not isinstance(instance_ids, list):
                raise ValueError("'instance_ids' must be a list")
            return _handle_multiple_instances(instance_ids, action)
        
        # Handle single instance
        instance_id = event.get("instance_id") or INSTANCE_ID
        if not instance_id:
            raise ValueError("Missing 'instance_id' parameter and no INSTANCE_ID environment variable")
        
        # Execute action
        if action == "start":
            return _start_instance(instance_id)
        elif action == "stop":
            return _stop_instance(instance_id)
        elif action == "restart":
            return _restart_instance(instance_id)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {"ok": False, "action": action if 'action' in locals() else "unknown", 
                "message": str(e), "error_type": "validation_error"}
    
    except ClientError as e:
        logger.error(f"AWS API error: {e}")
        return {"ok": False, "action": action, "message": f"AWS error: {str(e)}", 
                "error_type": "aws_error", "error_code": e.response.get("Error", {}).get("Code")}
    
    except Exception as e:
        logger.exception("Unexpected error")
        return {"ok": False, "action": action if 'action' in locals() else "unknown", 
                "message": f"Unexpected error: {str(e)}", "error_type": "unexpected_error"}
