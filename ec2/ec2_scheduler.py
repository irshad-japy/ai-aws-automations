# -*- coding: utf-8 -*-
"""
ec2_scheduler.py

python ec2_scheduler.py status
python ec2_scheduler.py start
python ec2_scheduler.py idle-guard
you want stop
python ec2_scheduler.py idle-guard --window-min 60 --slice-min 5

Subcommands:
  - start        : Start the instance.
  - stop         : Stop the instance.
  - status       : Print current state.
  - idle-guard   : Check last 30 min metrics every run; stop if idle window.

Env vars (override defaults):
  INSTANCE_ID         (required) e.g. i-0abc123...
  REGION              default ap-south-1
  AWS_PROFILE         default None (use default chain)
  WINDOW_MINUTES      default 30
  SLICE_MINUTES       default 5
  IDLE_CPU_PCT        default 2.0
  IDLE_NET_BYTES      default 50000  (~50 KB per slice)
  LOG_DIR             default ./logs

CLI flags override envs.
"""

import os
import sys
import argparse
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, timezone

try:
    from dotenv import load_dotenv  # optional
    load_dotenv()
except Exception:
    pass

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# ---------- Config helpers ----------

def env(key, default=None, cast=str):
    val = os.environ.get(key, None)
    if val is None:
        return default
    try:
        return cast(val)
    except Exception:
        return val if default is None else cast(default)

DEFAULTS = {
    "INSTANCE_ID": None,
    "REGION": "ap-south-1",
    "AWS_PROFILE": None,
    "WINDOW_MINUTES": 30,
    "SLICE_MINUTES": 5,
    "IDLE_CPU_PCT": 2.0,
    "IDLE_NET_BYTES": 50000,
    "LOG_DIR": "./logs",
}

# ---------- Logging ----------

def get_logger(name="ec2_scheduler", log_dir=None):
    log_dir = log_dir or env("LOG_DIR", DEFAULTS["LOG_DIR"])
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # avoid duplicate handlers if script is called repeatedly
    if not logger.handlers:
        fh = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        ))
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(fh)
        logger.addHandler(sh)
    return logger

# ---------- AWS clients ----------

def make_session(profile):
    if profile:
        return boto3.Session(profile_name=profile)
    return boto3.Session()

def clients(region, profile=None):
    sess = make_session(profile)
    return (
        sess.client("ec2", region_name=region),
        sess.client("cloudwatch", region_name=region),
    )

# ---------- Core ops ----------

def get_instance_state(ec2, instance_id):
    d = ec2.describe_instances(InstanceIds=[instance_id])
    return d["Reservations"][0]["Instances"][0]["State"]["Name"]

def start_instance(ec2, instance_id, logger):
    try:
        state = get_instance_state(ec2, instance_id)
        logger.info(f"Current state: {state}")
        if state == "running":
            logger.info("Instance already running; nothing to do.")
            return
        resp = ec2.start_instances(InstanceIds=[instance_id])
        logger.info(f"Start response: {resp}")
    except (ClientError, BotoCoreError) as e:
        logger.exception(f"Failed to start instance: {e}")
        sys.exit(2)

def stop_instance(ec2, instance_id, logger):
    try:
        state = get_instance_state(ec2, instance_id)
        logger.info(f"Current state: {state}")
        if state in ("stopped", "stopping"):
            logger.info("Instance already stopped/stopping; nothing to do.")
            return
        resp = ec2.stop_instances(InstanceIds=[instance_id])
        logger.info(f"Stop response: {resp}")
    except (ClientError, BotoCoreError) as e:
        logger.exception(f"Failed to stop instance: {e}")
        sys.exit(2)

def get_metric_series(cw, instance_id, metric, start, end, period, stat="Average", unit=None):
    params = {
        "Namespace": "AWS/EC2",
        "MetricName": metric,
        "Dimensions": [{"Name": "InstanceId", "Value": instance_id}],
        "StartTime": start,
        "EndTime": end,
        "Period": period,
        "Statistics": [stat],
    }
    if unit:
        params["Unit"] = unit
    r = cw.get_metric_statistics(**params)
    dps = sorted(r.get("Datapoints", []), key=lambda d: d["Timestamp"])
    return [dp.get(stat, 0.0) for dp in dps]

def idle_guard(ec2, cw, instance_id, window_min, slice_min, cpu_thresh, net_thresh, logger):
    state = get_instance_state(ec2, instance_id)
    logger.info(f"Instance state: {state}")
    if state != "running":
        logger.info("Instance not running; skip idle check.")
        return

    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=window_min)
    period = slice_min * 60

    cpu = get_metric_series(cw, instance_id, "CPUUtilization", start, now, period, stat="Average", unit="Percent")
    net_in = get_metric_series(cw, instance_id, "NetworkIn", start, now, period, stat="Sum", unit="Bytes")
    net_out = get_metric_series(cw, instance_id, "NetworkOut", start, now, period, stat="Sum", unit="Bytes")
    n = min(len(cpu), len(net_in), len(net_out))

    if n == 0:
        logger.info("No datapoints in the window; being conservative (do not stop).")
        return

    all_idle = True
    for i in range(n):
        c = cpu[i]
        net = net_in[i] + net_out[i]
        c_ok = c < cpu_thresh
        n_ok = net < net_thresh
        logger.info(f"slice {i+1}/{n}: cpu={c:.2f}% (<{cpu_thresh}? {c_ok}), net={net}B (<{net_thresh}? {n_ok})")
        if not (c_ok and n_ok):
            all_idle = False

    if all_idle:
        logger.info(f"Idle for ~{window_min} min across {n} slices → stopping instance.")
        stop_instance(ec2, instance_id, logger)
    else:
        logger.info("Activity detected → keep running.")

# ---------- CLI ----------

def build_parser():
    p = argparse.ArgumentParser(description="Local EC2 scheduler utilities")
    p.add_argument("--instance-id", default=env("INSTANCE_ID", DEFAULTS["INSTANCE_ID"]),
                   help="EC2 instance ID (env INSTANCE_ID)")
    p.add_argument("--region", default=env("REGION", DEFAULTS["REGION"]),
                   help="AWS region (env REGION)")
    p.add_argument("--profile", default=env("AWS_PROFILE", DEFAULTS["AWS_PROFILE"]),
                   help="AWS named profile (env AWS_PROFILE)")

    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("start", help="Start the instance")

    sub.add_parser("stop", help="Stop the instance")

    sub.add_parser("status", help="Show instance state")

    g = sub.add_parser("idle-guard", help="Stop if idle across whole window")
    g.add_argument("--window-min", type=int, default=env("WINDOW_MINUTES", DEFAULTS["WINDOW_MINUTES"], int))
    g.add_argument("--slice-min", type=int, default=env("SLICE_MINUTES", DEFAULTS["SLICE_MINUTES"], int))
    g.add_argument("--idle-cpu-pct", type=float, default=env("IDLE_CPU_PCT", DEFAULTS["IDLE_CPU_PCT"], float))
    g.add_argument("--idle-net-bytes", type=int, default=env("IDLE_NET_BYTES", DEFAULTS["IDLE_NET_BYTES"], int))

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.instance_id:
        print("ERROR: INSTANCE_ID not provided. Use --instance-id or set env INSTANCE_ID.")
        sys.exit(1)

    logger = get_logger()

    try:
        ec2, cw = clients(args.region, args.profile)

        if args.cmd == "start":
            start_instance(ec2, args.instance_id, logger)

        elif args.cmd == "stop":
            stop_instance(ec2, args.instance_id, logger)

        elif args.cmd == "status":
            state = get_instance_state(ec2, args.instance_id)
            logger.info({"instance_id": args.instance_id, "state": state})
            print(state)

        elif args.cmd == "idle-guard":
            idle_guard(
                ec2, cw, args.instance_id,
                args.window_min, args.slice_min,
                args.idle_cpu_pct, args.idle_net_bytes,
                logger
            )

    except Exception as e:
        # Full traceback goes to the log file and console
        logger.exception(f"Unhandled error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
