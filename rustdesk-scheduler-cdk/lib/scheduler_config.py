"""
Generic Scheduler Configuration

This module defines the configuration structure for EC2 scheduling.
Easily modify schedules, actions, and settings without touching the main CDK code.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class Action(Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"


class WeekDay(Enum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"
    
    # Convenience groups
    WEEKDAYS = "MON-FRI"
    WEEKENDS = "SAT-SUN"
    ALL_DAYS = "MON-SUN"
    ALL_EXCEPT_SAT = "MON-FRI,SUN"


@dataclass
class TimeZoneConfig:
    """Timezone configuration with UTC offset"""
    name: str
    utc_offset_hours: float
    
    def to_utc_hour(self, local_hour: int, local_minute: int = 0) -> tuple[int, int]:
        """Convert local time to UTC time"""
        total_local_minutes = local_hour * 60 + local_minute
        total_utc_minutes = total_local_minutes - (self.utc_offset_hours * 60)
        
        # Handle day rollover
        if total_utc_minutes < 0:
            total_utc_minutes += 24 * 60
        elif total_utc_minutes >= 24 * 60:
            total_utc_minutes -= 24 * 60
            
        utc_hour = int(total_utc_minutes // 60)
        utc_minute = int(total_utc_minutes % 60)
        
        return utc_hour, utc_minute


@dataclass
class ScheduleRule:
    """Individual schedule rule configuration"""
    name: str
    action: Action
    hour: int  # Local time hour (24-hour format)
    minute: int = 0  # Local time minute
    week_days: str = WeekDay.ALL_DAYS.value  # AWS cron format: MON-FRI,SUN
    enabled: bool = True
    description: str = ""
    
    def get_cron_expression(self, timezone_config: TimeZoneConfig) -> Dict[str, str]:
        """Generate AWS EventBridge cron expression in UTC"""
        utc_hour, utc_minute = timezone_config.to_utc_hour(self.hour, self.minute)
        
        return {
            "minute": str(utc_minute),
            "hour": str(utc_hour),
            "week_day": self.week_days
        }


@dataclass
class SchedulerConfig:
    """Main scheduler configuration"""
    # Instance and Lambda settings
    lambda_function_name: str = "generic-ec2-scheduler"
    lambda_timeout_seconds: int = 60
    lambda_memory_mb: int = 128
    lambda_log_retention_days: int = 30
    
    # Timezone
    timezone: TimeZoneConfig = field(default_factory=lambda: TimeZoneConfig(
        name="IST", 
        utc_offset_hours=5.5  # IST = UTC+5:30
    ))
    
    # Schedule rules
    schedules: Optional[List[ScheduleRule]] = None
    
    # Tags
    project_tag: str = "Generic-EC2-Scheduler"
    owner_tag: str = "DevOps"
    
    # Additional environment variables for Lambda
    additional_env_vars: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.schedules is None:
            # Default RustDesk schedule (backward compatible)
            self.schedules = self.get_default_rustdesk_schedules()
        
        if self.additional_env_vars is None:
            self.additional_env_vars = {}
    
    def get_default_rustdesk_schedules(self) -> List[ScheduleRule]:
        """Default RustDesk scheduling rules"""
        return [
            ScheduleRule(
                name="DailyStart0900",
                action=Action.START,
                hour=9,
                minute=0,
                week_days=WeekDay.ALL_EXCEPT_SAT.value,
                description="Start EC2 at 09:00 IST daily except Saturday"
            ),
            ScheduleRule(
                name="DailyStop2100", 
                action=Action.STOP,
                hour=21,
                minute=0,
                week_days=WeekDay.ALL_DAYS.value,
                description="Stop EC2 at 21:00 IST daily"
            ),
            ScheduleRule(
                name="MaintenanceStop1730",
                action=Action.STOP,
                hour=17,
                minute=30,
                week_days=WeekDay.ALL_EXCEPT_SAT.value,
                description="Stop EC2 at 17:30 IST for maintenance except Saturday"
            ),
            ScheduleRule(
                name="MaintenanceStart1830",
                action=Action.START,
                hour=18,
                minute=30,
                week_days=WeekDay.ALL_EXCEPT_SAT.value,
                description="Restart EC2 at 18:30 IST after maintenance except Saturday"
            )
        ]
    
    def get_enabled_schedules(self) -> List[ScheduleRule]:
        """Get only enabled schedule rules"""
        return [schedule for schedule in self.schedules if schedule.enabled]


# Predefined configurations for different environments/use cases

def get_basic_work_hours_config() -> SchedulerConfig:
    """Simple work hours: start 9 AM, stop 6 PM, weekdays only"""
    return SchedulerConfig(
        lambda_function_name="work-hours-ec2-scheduler",
        schedules=[
            ScheduleRule(
                name="WorkStart",
                action=Action.START,
                hour=9,
                minute=0,
                week_days=WeekDay.WEEKDAYS.value,
                description="Start EC2 for work hours"
            ),
            ScheduleRule(
                name="WorkStop",
                action=Action.STOP,
                hour=18,
                minute=0,
                week_days=WeekDay.WEEKDAYS.value,
                description="Stop EC2 after work hours"
            )
        ]
    )


def get_development_config() -> SchedulerConfig:
    """Development environment: flexible hours with restart capability"""
    return SchedulerConfig(
        lambda_function_name="dev-ec2-scheduler",
        timezone=TimeZoneConfig("EST", -5.0),  # Eastern Time
        schedules=[
            ScheduleRule(
                name="DevStart",
                action=Action.START,
                hour=8,
                minute=0,
                week_days=WeekDay.WEEKDAYS.value,
                description="Start development environment"
            ),
            ScheduleRule(
                name="DevRestart",
                action=Action.RESTART,
                hour=12,
                minute=0,
                week_days=WeekDay.WEEKDAYS.value,
                description="Daily restart for dev environment"
            ),
            ScheduleRule(
                name="DevStop",
                action=Action.STOP,
                hour=20,
                minute=0,
                week_days=WeekDay.ALL_DAYS.value,
                description="Stop development environment"
            )
        ]
    )


def get_rustdesk_config() -> SchedulerConfig:
    """Original RustDesk configuration"""
    return SchedulerConfig()


def get_custom_config(
    timezone_name: str = "UTC",
    timezone_offset: float = 0.0,
    custom_schedules: List[ScheduleRule] = None
) -> SchedulerConfig:
    """Create a custom configuration"""
    return SchedulerConfig(
        timezone=TimeZoneConfig(timezone_name, timezone_offset),
        schedules=custom_schedules or [],
        lambda_function_name=f"custom-{timezone_name.lower()}-scheduler"
    )