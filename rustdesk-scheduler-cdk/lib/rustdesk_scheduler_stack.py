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
from .scheduler_config import (
    SchedulerConfig, 
    get_rustdesk_config, 
    get_basic_work_hours_config, 
    get_development_config,
    get_custom_config
)

class GenericEC2SchedulerStack(Stack):
    """
    Generic EC2 Scheduler Stack
    
    Creates a configurable scheduler system with:
      - Lambda function for EC2 management (start/stop/restart)
      - EventBridge rules based on configuration
      - Support for multiple scheduling patterns
      - Easy configuration switching
    """

    def __init__(self, scope: Construct, construct_id: str, scheduler_config: SchedulerConfig = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -------- Configuration Setup --------
        if scheduler_config is None:
            # Try to get config type from context, default to RustDesk
            config_type = self.node.try_get_context("configType") or "rustdesk"
            scheduler_config = self._get_config_by_type(config_type)
        
        self.config = scheduler_config
        
        # -------- Context / config --------
        instance_id: str = self.node.try_get_context("instanceId")
        if not instance_id:
            raise ValueError("Set context: instanceId in cdk.json or pass instance_ids in config")

        # Override tags from context if provided
        project_tag = self.node.try_get_context("projectTag") or self.config.project_tag
        owner_tag = self.node.try_get_context("ownerTag") or self.config.owner_tag
        
        # Store for later use
        self.instance_id = instance_id
        self.project_tag = project_tag  
        self.owner_tag = owner_tag
        
        # -------- Create Lambda Function --------
        self._create_lambda_function()
        
        # -------- Create Schedule Rules --------
        self._create_schedule_rules()

        # -------- Apply Tags --------
        Tags.of(self).add("Project", self.project_tag)
        Tags.of(self).add("Owner", self.owner_tag)
    
    def _get_config_by_type(self, config_type: str) -> SchedulerConfig:
        """Get configuration based on type string"""
        config_map = {
            "rustdesk": get_rustdesk_config,
            "work_hours": get_basic_work_hours_config,
            "development": get_development_config,
            "custom": lambda: get_custom_config()
        }
        
        if config_type not in config_map:
            raise ValueError(f"Unknown config type: {config_type}. Available: {list(config_map.keys())}")
        
        return config_map[config_type]()
        
    def _create_lambda_function(self):
        """Create the Lambda function for EC2 management"""
        # IAM Role for Lambda
        self.lambda_role = iam.Role(
            self,
            "Ec2SchedulerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )
        self.lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ec2:StartInstances",
                    "ec2:StopInstances", 
                    "ec2:DescribeInstances",
                    "ec2:RebootInstances"  # For restart functionality
                ],
                resources=["*"],
            )
        )

        # Prepare environment variables
        env_vars = {
            "INSTANCE_ID": self.instance_id,
            "TIMEZONE": self.config.timezone.name,
            **self.config.additional_env_vars
        }

        # Map log retention days to proper enum values
        retention_mapping = {
            1: logs.RetentionDays.ONE_DAY,
            3: logs.RetentionDays.THREE_DAYS,
            5: logs.RetentionDays.FIVE_DAYS,
            7: logs.RetentionDays.ONE_WEEK,
            14: logs.RetentionDays.TWO_WEEKS,
            30: logs.RetentionDays.ONE_MONTH,
            60: logs.RetentionDays.TWO_MONTHS,
            90: logs.RetentionDays.THREE_MONTHS,
            120: logs.RetentionDays.FOUR_MONTHS,
            150: logs.RetentionDays.FIVE_MONTHS,
            180: logs.RetentionDays.SIX_MONTHS,
            365: logs.RetentionDays.ONE_YEAR,
            400: logs.RetentionDays.THIRTEEN_MONTHS,
            545: logs.RetentionDays.EIGHTEEN_MONTHS,
            731: logs.RetentionDays.TWO_YEARS,
            1827: logs.RetentionDays.FIVE_YEARS,
            3653: logs.RetentionDays.TEN_YEARS
        }
        
        log_retention = retention_mapping.get(
            self.config.lambda_log_retention_days, 
            logs.RetentionDays.ONE_MONTH
        )

        # Create Lambda function
        self.lambda_function = _lambda.Function(
            self,
            "Ec2SchedulerFn",
            function_name=self.config.lambda_function_name,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            role=self.lambda_role,
            timeout=Duration.seconds(self.config.lambda_timeout_seconds),
            memory_size=self.config.lambda_memory_mb,
            environment=env_vars,
            log_retention=log_retention,
        )

    def _create_schedule_rules(self):
        """Create EventBridge rules based on configuration"""
        enabled_schedules = self.config.get_enabled_schedules()
        
        for i, schedule in enumerate(enabled_schedules):
            # Generate cron expression
            cron_expr = schedule.get_cron_expression(self.config.timezone)
            
            # Create EventBridge rule
            rule = events.Rule(
                self,
                f"ScheduleRule{i}_{schedule.name}",
                schedule=events.Schedule.cron(
                    minute=cron_expr["minute"],
                    hour=cron_expr["hour"],
                    week_day=cron_expr["week_day"]
                ),
                description=schedule.description or f"{schedule.action.value} EC2 at {schedule.hour:02d}:{schedule.minute:02d} {self.config.timezone.name}",
            )
            
            # Add Lambda target with action parameters
            event_input = {
                "action": schedule.action.value,
                "instance_id": self.instance_id,
                "schedule_name": schedule.name,
                "timezone": self.config.timezone.name
            }
            
            rule.add_target(
                targets.LambdaFunction(
                    self.lambda_function,
                    event=events.RuleTargetInput.from_object(event_input)
                )
            )


# Keep backward compatibility with old class name
class RustDeskSchedulerStack(GenericEC2SchedulerStack):
    """Backward compatibility wrapper for RustDesk scheduler"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        # Force RustDesk configuration
        super().__init__(scope, construct_id, scheduler_config=get_rustdesk_config(), **kwargs)
