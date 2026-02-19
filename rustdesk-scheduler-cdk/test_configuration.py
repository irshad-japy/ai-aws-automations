#!/usr/bin/env python3
"""
Test Configuration Validation

Quick test to validate the refactored configuration system works correctly.
"""

import sys
import traceback
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

def test_timezone_conversion():
    """Test timezone to UTC conversion"""
    print("Testing timezone conversions...")
    
    # Test IST (UTC+5:30)
    ist_tz = TimeZoneConfig("IST", 5.5)
    
    # Test 9:00 IST -> should be 3:30 UTC
    utc_hour, utc_minute = ist_tz.to_utc_hour(9, 0)
    assert utc_hour == 3 and utc_minute == 30, f"Expected 3:30 UTC, got {utc_hour}:{utc_minute}"
    print(f"[PASS] 9:00 IST -> {utc_hour}:{utc_minute:02d} UTC")
    
    # Test PST (UTC-8)
    pst_tz = TimeZoneConfig("PST", -8.0)
    utc_hour, utc_minute = pst_tz.to_utc_hour(8, 30)
    assert utc_hour == 16 and utc_minute == 30, f"Expected 16:30 UTC, got {utc_hour}:{utc_minute}"
    print(f"[PASS] 8:30 PST -> {utc_hour}:{utc_minute:02d} UTC")
    
    print("[PASS] Timezone conversion tests passed!")


def test_schedule_rules():
    """Test schedule rule generation"""
    print("\nTesting schedule rules...")
    
    config = get_basic_work_hours_config()
    schedules = config.get_enabled_schedules()
    
    assert len(schedules) == 2, f"Expected 2 schedules, got {len(schedules)}"
    
    for schedule in schedules:
        cron_expr = schedule.get_cron_expression(config.timezone)
        print(f"[PASS] {schedule.name}: {schedule.action.value} at {schedule.hour:02d}:{schedule.minute:02d} {config.timezone.name}")
        print(f"       Cron: minute={cron_expr['minute']}, hour={cron_expr['hour']}, weekday={cron_expr['week_day']}")
    
    print("[PASS] Schedule rule tests passed!")


def test_predefined_configs():
    """Test all predefined configurations"""
    print("\nTesting predefined configurations...")
    
    configs = {
        "rustdesk": get_rustdesk_config(),
        "work_hours": get_basic_work_hours_config(), 
        "development": get_development_config(),
        "custom": get_custom_config()
    }
    
    for name, config in configs.items():
        schedules = config.get_enabled_schedules()
        print(f"[PASS] {name}: {len(schedules)} schedules, timezone={config.timezone.name}, lambda={config.lambda_function_name}")
        
        for schedule in schedules:
            assert schedule.action in [Action.START, Action.STOP, Action.RESTART], f"Invalid action: {schedule.action}"
            assert 0 <= schedule.hour <= 23, f"Invalid hour: {schedule.hour}"
            assert 0 <= schedule.minute <= 59, f"Invalid minute: {schedule.minute}"
    
    print("[PASS] Predefined configuration tests passed!")


def test_custom_configuration():
    """Test custom configuration creation"""
    print("\nTesting custom configuration...")
    
    # Create a custom config
    custom_schedules = [
        ScheduleRule(
            name="CustomStart",
            action=Action.START,
            hour=10,
            minute=15,
            week_days="MON,WED,FRI",
            description="Custom start schedule"
        ),
        ScheduleRule(
            name="CustomRestart",
            action=Action.RESTART,
            hour=12,
            minute=0,
            week_days=WeekDay.ALL_DAYS.value,
            enabled=False,  # Test disabled schedule
            description="Daily restart (disabled)"
        )
    ]
    
    custom_config = SchedulerConfig(
        lambda_function_name="test-custom-scheduler",
        timezone=TimeZoneConfig("EST", -5.0),
        schedules=custom_schedules,
        lambda_timeout_seconds=90,
        lambda_memory_mb=256,
        additional_env_vars={
            "TEST_MODE": "true",
            "DEBUG": "1"
        }
    )
    
    # Test enabled schedules (should only return the enabled one)
    enabled = custom_config.get_enabled_schedules()
    assert len(enabled) == 1, f"Expected 1 enabled schedule, got {len(enabled)}"
    assert enabled[0].name == "CustomStart", f"Wrong schedule enabled: {enabled[0].name}"
    
    # Test cron generation
    cron_expr = enabled[0].get_cron_expression(custom_config.timezone)
    # 10:15 EST -> 15:15 UTC
    assert cron_expr["hour"] == "15", f"Expected hour 15, got {cron_expr['hour']}"
    assert cron_expr["minute"] == "15", f"Expected minute 15, got {cron_expr['minute']}"
    
    print("[PASS] Custom configuration tests passed!")


def test_weekday_enums():
    """Test WeekDay enum values"""
    print("\nTesting WeekDay enums...")
    
    assert WeekDay.WEEKDAYS.value == "MON-FRI"
    assert WeekDay.WEEKENDS.value == "SAT-SUN"
    assert WeekDay.ALL_DAYS.value == "MON-SUN"
    assert WeekDay.ALL_EXCEPT_SAT.value == "MON-FRI,SUN"
    
    print("[PASS] WeekDay enum tests passed!")


def run_all_tests():
    """Run all validation tests"""
    print("Running configuration validation tests...\n")
    
    try:
        test_timezone_conversion()
        test_schedule_rules()
        test_predefined_configs()
        test_custom_configuration()
        test_weekday_enums()
        
        print("\nAll tests passed! The refactored configuration system is working correctly.")
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)