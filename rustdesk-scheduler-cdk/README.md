# Generic EC2 Scheduler — CDK (Python)

A highly configurable EC2 scheduler that supports:
- **Multiple scheduling patterns** (work hours, 24/7 with maintenance, custom timezones)
- **Flexible actions** (start/stop/restart)
- **Easy configuration** without touching CDK code
- **Backward compatibility** with original RustDesk setup
- **Timezone support** with automatic UTC conversion
- **Multiple instances** support via Lambda
- **Enable/disable schedules** without redeployment

## Quick Start

### 1. For Existing RustDesk Users (Backward Compatible)
```bash
# Your existing deployment continues to work unchanged
cdk deploy RustDeskSchedulerStack -c instanceId=i-09c40c2e332da8c67
```

### 2. For New Generic Configurations
```python
# app.py
import aws_cdk as cdk
from lib.rustdesk_scheduler_stack import GenericEC2SchedulerStack
from lib.scheduler_config import get_basic_work_hours_config

app = cdk.App()
GenericEC2SchedulerStack(
    app, "WorkHoursScheduler",
    scheduler_config=get_basic_work_hours_config(),
    env=cdk.Environment(account="your-account", region="your-region"),
)
app.synth()
```

## Available Configurations

### 1. RustDesk (Original)
- **Start**: 09:00 IST daily except Saturday
- **Stop**: 21:00 IST daily  
- **Maintenance**: Stop 17:30 IST, Start 18:30 IST (except Saturday)

```python
from lib.scheduler_config import get_rustdesk_config
config = get_rustdesk_config()
```

### 2. Basic Work Hours
- **Start**: 09:00 IST weekdays
- **Stop**: 18:00 IST weekdays

```python
from lib.scheduler_config import get_basic_work_hours_config
config = get_basic_work_hours_config()
```

### 3. Development Environment
- **Timezone**: Eastern Time (EST)
- **Start**: 08:00 EST weekdays
- **Restart**: 12:00 EST weekdays (daily restart)
- **Stop**: 20:00 EST daily

```python
from lib.scheduler_config import get_development_config
config = get_development_config()
```

### 4. Custom Configuration
```python
from lib.scheduler_config import (
    SchedulerConfig, ScheduleRule, Action, WeekDay, TimeZoneConfig
)

custom_config = SchedulerConfig(
    lambda_function_name="my-custom-scheduler",
    timezone=TimeZoneConfig("PST", -8.0),  # Pacific Time
    schedules=[
        ScheduleRule(
            name="MorningStart",
            action=Action.START,
            hour=8,      # 8 AM PST
            minute=30,   # 8:30 AM PST
            week_days=WeekDay.WEEKDAYS.value,
            description="Start work day"
        ),
        ScheduleRule(
            name="EveningStop",
            action=Action.STOP,
            hour=17,     # 5 PM PST
            minute=0,
            week_days=WeekDay.ALL_DAYS.value,
            description="Stop after work"
        )
    ],
    project_tag="My-Project",
    additional_env_vars={
        "ENVIRONMENT": "production",
        "NOTIFICATION_ENABLED": "true"
    }
)
```

## Usage Examples

### Context-Based Configuration (Simple)
```bash
# Set configuration type in CDK context
cdk deploy -c configType=work_hours -c instanceId=i-1234567890abcdef0
```

Available `configType` values:
- `rustdesk` (default)
- `work_hours`
- `development` 
- `custom`

### Configuration in Code (Advanced)
```python
# app.py
import aws_cdk as cdk
from lib.rustdesk_scheduler_stack import GenericEC2SchedulerStack
from lib.scheduler_config import *

# Different timezone example
pacific_config = SchedulerConfig(
    timezone=TimeZoneConfig("PST", -8.0),
    schedules=[
        ScheduleRule("Start", Action.START, 9, 0, WeekDay.WEEKDAYS.value),
        ScheduleRule("Stop", Action.STOP, 17, 0, WeekDay.ALL_DAYS.value),
    ]
)

app = cdk.App()
GenericEC2SchedulerStack(
    app, "PacificScheduler",
    scheduler_config=pacific_config,
    env=cdk.Environment(account="123456789012", region="us-west-2"),
)
app.synth()
```

## Advanced Features

### Restart Capability
```python
ScheduleRule(
    name="DailyRestart",
    action=Action.RESTART,  # Stop then start
    hour=3,                 # 3 AM maintenance window
    minute=0,
    week_days=WeekDay.ALL_DAYS.value,
    description="Daily maintenance restart"
)
```

### Multiple Instances
The Lambda handler supports multiple instances:
```json
{
  "action": "start",
  "instance_ids": ["i-1234567890abcdef0", "i-0987654321fedcba0"]
}
```

### Enable/Disable Schedules
```python
ScheduleRule(
    name="OptionalSchedule",
    action=Action.STOP,
    hour=12,
    minute=0,
    week_days=WeekDay.WEEKDAYS.value,
    enabled=False,  # Disabled without redeployment
    description="Lunch break (currently disabled)"
)
```

### Custom Environment Variables
```python
SchedulerConfig(
    additional_env_vars={
        "SLACK_WEBHOOK": "https://hooks.slack.com/...",
        "ENVIRONMENT": "production",
        "AUTO_RETRY": "true"
    }
)
```

## Deployment

### Prerequisites
```bash
# Bootstrap (first time per account/region)
cdk bootstrap aws://YOUR_ACCOUNT/YOUR_REGION
```

### Environment Setup
```bash
# PowerShell
$env:AWS_PROFILE = "your-profile"
$env:CDK_DEFAULT_REGION = "ap-south-1"
$env:CDK_DEFAULT_ACCOUNT = (aws sts get-caller-identity --query Account --output text)

# Verify
aws sts get-caller-identity
```

### Deploy
```bash
# Backward compatible (existing RustDesk users)
cdk deploy RustDeskSchedulerStack -c instanceId=i-1234567890abcdef0

# Generic scheduler with work hours
cdk deploy WorkHoursScheduler -c configType=work_hours -c instanceId=i-1234567890abcdef0

# Custom configuration (modify app.py)
cdk deploy MyCustomScheduler
```

### Destroy
```bash
cdk destroy RustDeskSchedulerStack --force
```

## Configuration Reference

### SchedulerConfig Parameters
- `lambda_function_name`: Lambda function name
- `lambda_timeout_seconds`: Execution timeout (default: 60)
- `lambda_memory_mb`: Memory allocation (default: 128)
- `lambda_log_retention_days`: Log retention (default: 30)
- `timezone`: TimeZoneConfig object
- `schedules`: List of ScheduleRule objects
- `project_tag`: Project tag value
- `owner_tag`: Owner tag value
- `additional_env_vars`: Extra environment variables

### ScheduleRule Parameters  
- `name`: Unique rule name
- `action`: Action.START, Action.STOP, or Action.RESTART
- `hour`: Hour in local timezone (0-23)
- `minute`: Minute (0-59)
- `week_days`: AWS cron format ("MON-FRI", "SAT,SUN", etc.)
- `enabled`: Boolean to enable/disable
- `description`: Human-readable description

### WeekDay Convenience Values
- `WeekDay.WEEKDAYS.value` → "MON-FRI"
- `WeekDay.WEEKENDS.value` → "SAT-SUN"  
- `WeekDay.ALL_DAYS.value` → "MON-SUN"
- `WeekDay.ALL_EXCEPT_SAT.value` → "MON-FRI,SUN"

## Examples and Testing

See `example_configurations.py` for comprehensive examples including:
- Multiple timezone configurations
- 24/7 servers with maintenance windows
- Development environments with restart
- Disabled schedule management

### Test Lambda Manually
```bash
# Using the CLI tool
python invoke_lambda_function.py

# Or AWS CLI
aws lambda invoke \
  --function-name generic-ec2-scheduler \
  --payload '{"action":"start","instance_id":"i-1234567890abcdef0"}' \
  response.json
```

## Troubleshooting

### Common Issues
1. **Instance ID not found**: Verify `instanceId` in cdk.json or context
2. **Timezone conversion**: Check `TimeZoneConfig` offset value
3. **Schedule not running**: Verify `enabled=True` and cron expression
4. **Lambda timeout**: Increase `lambda_timeout_seconds` for restart operations

### View Logs
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/generic-ec2-scheduler"
aws logs tail /aws/lambda/generic-ec2-scheduler --follow
```

### Debug Schedule Rules
EventBridge rules are created with descriptive names:
- `ScheduleRule0_DailyStart0900`
- `ScheduleRule1_DailyStop2100`

Check EventBridge console for rule status and next scheduled executions.

## Migration Guide

### From Original RustDesk
✅ **No changes needed** - `RustDeskSchedulerStack` maintains full compatibility

### To Generic Configuration
1. Replace `RustDeskSchedulerStack` with `GenericEC2SchedulerStack`
2. Add desired `scheduler_config` parameter
3. Deploy with same instance ID

### Custom Requirements
For unique scheduling needs not covered by predefined configs:
1. Copy patterns from `example_configurations.py`
2. Create your own `SchedulerConfig`
3. Use `GenericEC2SchedulerStack` with your config

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  EventBridge    │───▶│  Lambda         │───▶│  EC2 Instance   │
│  Rules (Cron)   │    │  (Enhanced)     │    │  (Start/Stop/   │
│                 │    │                 │    │   Restart)      │  
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       │
         │              ┌─────────────────┐
    ┌─────────────────┐ │   CloudWatch    │
    │ Configuration   │ │   Logs          │
    │ (scheduler_     │ │                 │
    │  config.py)     │ └─────────────────┘
    └─────────────────┘
```

The system automatically:
- Converts local times to UTC for EventBridge
- Creates descriptive rule names and descriptions  
- Handles timezone calculations
- Provides enhanced error handling and logging
- Supports multiple instances per Lambda invocation
