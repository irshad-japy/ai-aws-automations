from aws_cdk import (
    Duration,
    Stack,
    Tags,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_logs as logs,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct

class RustDeskSchedulerStack(Stack):
    """
    Creates:
      - Lambda (start/stop EC2) named 'lambda-rustdesk-auto-start-stop-ec2'
      - EventBridge rules:
          * Start 09:00 IST (03:30 UTC)  [Fri ON, Sat OFF]
          * Stop  21:00 IST (15:30 UTC)  daily
          * Stop  13:30 IST daily except Saturday (08:00 UTC)
          * Start 14:30 IST daily except Saturday (09:00 UTC)
      - (Idle-shutdown alarms REMOVED)
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -------- Context / config --------
        instance_id: str = self.node.try_get_context("instanceId")
        if not instance_id:
            raise ValueError("Set context: instanceId in cdk.json")

        # kept for backwards compatibility but no longer used for logic
        friday_off = bool(self.node.try_get_context("fridayOff") or True)

        project_tag = self.node.try_get_context("projectTag") or "RustDesk-Auto"
        owner_tag = self.node.try_get_context("ownerTag") or "owner"

        # -------- Lambda: EC2 start/stop --------
        lambda_role = iam.Role(
            self,
            "Ec2StartStopRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ec2:StartInstances",
                    "ec2:StopInstances",
                    "ec2:DescribeInstances",
                ],
                resources=["*"],
            )
        )

        fn = _lambda.Function(
            self,
            "Ec2StartStopFn",
            function_name="lambda-rustdesk-auto-start-stop-ec2",
            # If your aws-cdk-lib is older, switch to PYTHON_3_10
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            environment={"INSTANCE_ID": instance_id},
            log_retention=logs.RetentionDays.ONE_MONTH,
        )

        # -------- EventBridge schedules (UTC) --------
        # IST = UTC + 5:30
        # 09:00 IST  → 03:30 UTC
        # 21:00 IST  → 15:30 UTC
        # 13:30 IST  → 08:00 UTC
        # 14:30 IST  → 09:00 UTC

        # ✅ Daily 09:00 IST start → Mon–Fri + Sun (Saturday OFF)
        start_0900_weekdays = "MON-FRI,SUN"  # Friday ON, Saturday OFF
        start_0900 = events.Rule(
            self,
            "Start09IST",
            schedule=events.Schedule.cron(
                minute="30", hour="3", week_day=start_0900_weekdays
            ),
            description="Start EC2 at 09:00 IST (03:30 UTC) except Saturday",
        )
        start_0900.add_target(
            targets.LambdaFunction(
                fn,
                event=events.RuleTargetInput.from_object(
                    {"action": "start", "instance_id": instance_id}
                ),
            )
        )

        # ✅ Daily 21:00 IST stop → ALL days
        stop_2100 = events.Rule(
            self,
            "Stop21IST",
            schedule=events.Schedule.cron(
                minute="30", hour="15", week_day="MON-SUN"
            ),
            description="Stop EC2 at 21:00 IST (15:30 UTC) daily",
        )
        stop_2100.add_target(
            targets.LambdaFunction(
                fn,
                event=events.RuleTargetInput.from_object(
                    {"action": "stop", "instance_id": instance_id}
                ),
            )
        )

        # ❌ Old Friday 09:00 stop rule REMOVED

        # ✅ NEW: Daily 13:30 IST stop except Saturday → 08:00 UTC
        maint_weekdays_utc = "MON-FRI,SUN"  # Friday ON, Saturday OFF
        stop_1330 = events.Rule(
            self,
            "Stop1330ISTExceptSaturday",
            schedule=events.Schedule.cron(
                minute="0", hour="8", week_day=maint_weekdays_utc
            ),
            description="Stop EC2 at 13:30 IST daily except Saturday (08:00 UTC)",
        )
        stop_1330.add_target(
            targets.LambdaFunction(
                fn,
                event=events.RuleTargetInput.from_object(
                    {"action": "stop", "instance_id": instance_id}
                ),
            )
        )

        # ✅ NEW: Daily 14:30 IST start except Saturday → 09:00 UTC
        start_1430 = events.Rule(
            self,
            "Start1430ISTExceptSaturday",
            schedule=events.Schedule.cron(
                minute="0", hour="9", week_day=maint_weekdays_utc
            ),
            description="Start EC2 at 14:30 IST daily except Saturday (09:00 UTC)",
        )
        start_1430.add_target(
            targets.LambdaFunction(
                fn,
                event=events.RuleTargetInput.from_object(
                    {"action": "start", "instance_id": instance_id}
                ),
            )
        )

        # -------- Tags --------
        Tags.of(self).add("Project", project_tag)
        Tags.of(self).add("Owner", owner_tag)
