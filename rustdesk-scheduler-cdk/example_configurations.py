#!/usr/bin/env python3
"""
Example Configurations for Generic EC2 Scheduler

This file demonstrates how to use different scheduler configurations.
Copy the patterns you need or create your own custom configurations.
"""

import aws_cdk as cdk
from lib.rustdesk_scheduler_stack import GenericEC2SchedulerStack
from lib.scheduler_config import (
    SchedulerConfig,
    ScheduleRule,
    Action,
    WeekDay,
    TimeZoneConfig,
    get_rustdesk_config,
    get_basic_work_hours_config,
    get_development_config,
    get_custom_config
)


def create_rustdesk_example():
    """Original RustDesk configuration - maintains existing behavior"""
    app = cdk.App()
    
    # Option 1: Use the backward compatibility class (recommended for existing setups)
    from lib.rustdesk_scheduler_stack import RustDeskSchedulerStack
    RustDeskSchedulerStack(
        app, "RustDeskSchedulerStack",
        env=cdk.Environment(account="747230718574", region="ap-south-1"),
    )
    
    # Option 2: Use generic stack with RustDesk config
    GenericEC2SchedulerStack(
        app, "GenericRustDeskStack",
        scheduler_config=get_rustdesk_config(),
        env=cdk.Environment(account="747230718574", region="ap-south-1"),
    )
    
    return app


def create_work_hours_example():
    """Simple work hours: 9 AM - 6 PM, weekdays only"""
    app = cdk.App()
    
    GenericEC2SchedulerStack(
        app, "WorkHoursSchedulerStack", 
        scheduler_config=get_basic_work_hours_config(),
        env=cdk.Environment(account="747230718574", region="ap-south-1"),
    )
    
    return app


def create_development_example():
    """Development environment with Eastern Time and restart capability"""
    app = cdk.App()
    
    GenericEC2SchedulerStack(
        app, "DevSchedulerStack",
        scheduler_config=get_development_config(),
        env=cdk.Environment(account="747230718574", region="ap-south-1"),
    )
    
    return app


def create_custom_timezone_example():
    """Custom configuration with different timezone"""
    
    # Create custom schedules for Pacific Time
    pacific_schedules = [
        ScheduleRule(
            name="MorningStart",
            action=Action.START,
            hour=8,  # 8 AM PST
            minute=30,
            week_days=WeekDay.WEEKDAYS.value,
            description="Start EC2 for work day in PST"
        ),
        ScheduleRule(
            name="EveningStop", 
            action=Action.STOP,
            hour=17,  # 5 PM PST
            minute=0,
            week_days=WeekDay.WEEKDAYS.value,
            description="Stop EC2 after work in PST"
        ),
        ScheduleRule(
            name="WeekendStop",
            action=Action.STOP,
            hour=22,  # 10 PM PST
            minute=0, 
            week_days=WeekDay.WEEKENDS.value,
            description="Stop EC2 late on weekends"
        )
    ]
    
    custom_config = SchedulerConfig(
        lambda_function_name="pacific-ec2-scheduler",
        timezone=TimeZoneConfig("PST", -8.0),  # Pacific Standard Time
        schedules=pacific_schedules,
        project_tag="Pacific-Scheduler",
        owner_tag="West-Coast-Team",
        lambda_timeout_seconds=45,
        additional_env_vars={
            "ENVIRONMENT": "production",
            "NOTIFICATION_ENABLED": "true"
        }
    )
    
    app = cdk.App()
    GenericEC2SchedulerStack(
        app, "PacificSchedulerStack",
        scheduler_config=custom_config,
        env=cdk.Environment(account="747230718574", region="us-west-2"),
    )
    
    return app


def create_24_7_with_restart_example():
    """24/7 server with daily restart for maintenance"""
    
    maintenance_schedules = [
        ScheduleRule(
            name="DailyRestart",
            action=Action.RESTART,
            hour=3,  # 3 AM IST - low usage time
            minute=0,
            week_days=WeekDay.ALL_DAYS.value,
            description="Daily restart for maintenance"
        ),
        # Emergency stop on Sundays for major maintenance
        ScheduleRule(
            name="WeeklyMaintenance",
            action=Action.STOP,
            hour=2,  # 2 AM Sunday
            minute=0,
            week_days="SUN",
            description="Weekly maintenance window"
        ),
        ScheduleRule(
            name="MaintenanceResume",
            action=Action.START,
            hour=4,  # 4 AM Sunday
            minute=0, 
            week_days="SUN",
            description="Resume after maintenance"
        )
    ]
    
    always_on_config = SchedulerConfig(
        lambda_function_name="always-on-ec2-scheduler",
        schedules=maintenance_schedules,
        project_tag="24x7-Production",
        owner_tag="SRE-Team",
        lambda_timeout_seconds=120,  # Longer timeout for restart operations
        lambda_memory_mb=256,
        additional_env_vars={
            "ENVIRONMENT": "production",
            "HIGH_AVAILABILITY": "true"
        }
    )
    
    app = cdk.App()
    GenericEC2SchedulerStack(
        app, "AlwaysOnSchedulerStack",
        scheduler_config=always_on_config,
        env=cdk.Environment(account="747230718574", region="ap-south-1"),
    )
    
    return app


def create_multi_instance_example():
    """Example showing how to handle multiple instances with configuration context"""
    
    # Note: This still uses single instance per stack
    # For multiple instances, you'd deploy multiple stacks or modify the Lambda
    # to handle multiple instance IDs from environment variables
    
    test_config = SchedulerConfig(
        lambda_function_name="test-env-scheduler",
        schedules=[
            ScheduleRule(
                name="TestStart",
                action=Action.START,
                hour=9,
                minute=0,
                week_days=WeekDay.WEEKDAYS.value,
                description="Start test environment"
            ),
            ScheduleRule(
                name="TestStop",
                action=Action.STOP, 
                hour=18,
                minute=0,
                week_days=WeekDay.ALL_DAYS.value,
                description="Stop test environment"
            )
        ],
        project_tag="Test-Environment",
        additional_env_vars={
            "ENVIRONMENT": "test",
            "AUTO_CLEANUP": "true"
        }
    )
    
    app = cdk.App()
    GenericEC2SchedulerStack(
        app, "TestEnvSchedulerStack",
        scheduler_config=test_config,
        env=cdk.Environment(account="747230718574", region="ap-south-1"),
    )
    
    return app


def create_disabled_schedule_example():
    """Example showing how to disable certain schedules"""
    
    schedules = [
        ScheduleRule(
            name="WorkStart",
            action=Action.START,
            hour=9,
            minute=0,
            week_days=WeekDay.WEEKDAYS.value,
            enabled=True,  # This will run
            description="Start for work"
        ),
        ScheduleRule(
            name="LunchBreak", 
            action=Action.STOP,
            hour=12,
            minute=0,
            week_days=WeekDay.WEEKDAYS.value,
            enabled=False,  # This is disabled
            description="Stop for lunch (disabled)"
        ),
        ScheduleRule(
            name="WorkEnd",
            action=Action.STOP,
            hour=17,
            minute=0, 
            week_days=WeekDay.WEEKDAYS.value,
            enabled=True,  # This will run
            description="Stop after work"
        )
    ]
    
    config = SchedulerConfig(
        lambda_function_name="flexible-scheduler",
        schedules=schedules,
        project_tag="Flexible-Schedule"
    )
    
    app = cdk.App()
    GenericEC2SchedulerStack(
        app, "FlexibleSchedulerStack",
        scheduler_config=config,
        env=cdk.Environment(account="747230718574", region="ap-south-1"),
    )
    
    return app


if __name__ == "__main__":
    """
    To use any of these examples:
    
    1. Copy the configuration you want to your app.py
    2. Set the instanceId in cdk.json: {"context": {"instanceId": "i-1234567890abcdef0"}}
    3. Deploy: cdk deploy YourStackName
    """
    
    print("Example configurations created!")
    print("Available configurations:")
    print("1. RustDesk (original) - create_rustdesk_example()")
    print("2. Work Hours - create_work_hours_example()")
    print("3. Development - create_development_example()")
    print("4. Custom Timezone (PST) - create_custom_timezone_example()")
    print("5. 24/7 with Restart - create_24_7_with_restart_example()")
    print("6. Multi-Instance - create_multi_instance_example()")
    print("7. Disabled Schedules - create_disabled_schedule_example()")
    
    # You can uncomment one of these to test:
    # app = create_work_hours_example()
    # app.synth()