#!/usr/bin/env python3
"""
Domain Warmup Scheduler

Implements progressive volume ramping for new domains based on predefined
schedules and real-time deliverability feedback.

TODO for production:
- Add Redis caching for rate limiting
- Implement distributed locking for multi-instance deployments
- Add webhook integration for ESP feedback loops
- Enhance error handling and retry logic
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class WarmupSchedule:
    """Represents a domain warmup schedule with daily/hourly limits."""
    name: str
    daily_limits: List[int]  # Daily email limits by week
    hourly_limits: List[int]  # Hourly email limits by week
    bounce_threshold: float = 0.03  # 3% bounce rate threshold
    complaint_threshold: float = 0.001  # 0.1% complaint rate threshold


class WarmupScheduler:
    """Manages domain warmup scheduling and volume enforcement."""
    
    def __init__(self, config_path: str = "config/warmup_schedules.json"):
        self.logger = logging.getLogger(__name__)
        self.schedules = self._load_schedules(config_path)
        
    def _load_schedules(self, config_path: str) -> Dict[str, WarmupSchedule]:
        """Load predefined warmup schedules from configuration."""
        # Default schedules if config file doesn't exist
        default_schedules = {
            "conservative": WarmupSchedule(
                name="conservative",
                daily_limits=[10, 25, 50, 100, 200, 300, 500],
                hourly_limits=[2, 5, 8, 15, 25, 35, 50]
            ),
            "moderate": WarmupSchedule(
                name="moderate",
                daily_limits=[50, 150, 300, 500, 750, 1000],
                hourly_limits=[10, 20, 35, 50, 75, 100]
            ),
            "aggressive": WarmupSchedule(
                name="aggressive",
                daily_limits=[200, 500, 1000, 2000],
                hourly_limits=[30, 50, 75, 100]
            )
        }
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return {name: WarmupSchedule(**schedule) 
                       for name, schedule in config.items()}
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return default_schedules
    
    def start_warmup(self, domain: str, schedule_name: str = "conservative") -> bool:
        """Initialize warmup process for a new domain."""
        if schedule_name not in self.schedules:
            raise ValueError(f"Unknown schedule: {schedule_name}")
            
        schedule = self.schedules[schedule_name]
        warmup_record = {
            "domain": domain,
            "schedule_name": schedule_name,
            "start_date": datetime.utcnow().isoformat(),
            "current_week": 1,
            "status": "active",
            "daily_sent": 0,
            "hourly_sent": 0,
            "last_reset": datetime.utcnow().isoformat()
        }
        
        # TODO: Store in database instead of logging
        self.logger.info(f"Started {schedule_name} warmup for domain {domain}")
        self.logger.info(f"Week 1 limits: {schedule.daily_limits[0]} daily, {schedule.hourly_limits[0]} hourly")
        
        return True
    
    def check_send_limit(self, domain: str, email_count: int = 1) -> Dict[str, any]:
        """Check if sending is allowed based on current warmup limits."""
        # TODO: Fetch from database
        # Mock warmup record for demonstration
        warmup_record = {
            "domain": domain,
            "schedule_name": "conservative",
            "current_week": 2,
            "daily_sent": 15,
            "hourly_sent": 3,
            "last_reset": (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        }
        
        schedule = self.schedules[warmup_record["schedule_name"]]
        week_index = min(warmup_record["current_week"] - 1, len(schedule.daily_limits) - 1)
        
        daily_limit = schedule.daily_limits[week_index]
        hourly_limit = schedule.hourly_limits[week_index]
        
        # Check if we need to reset counters
        last_reset = datetime.fromisoformat(warmup_record["last_reset"])
        now = datetime.utcnow()
        
        if (now - last_reset).total_seconds() >= 3600:  # Reset hourly counter
            warmup_record["hourly_sent"] = 0
            
        if now.date() > last_reset.date():  # Reset daily counter
            warmup_record["daily_sent"] = 0
        
        # Check limits
        can_send_daily = warmup_record["daily_sent"] + email_count <= daily_limit
        can_send_hourly = warmup_record["hourly_sent"] + email_count <= hourly_limit
        
        return {
            "allowed": can_send_daily and can_send_hourly,
            "daily_remaining": daily_limit - warmup_record["daily_sent"],
            "hourly_remaining": hourly_limit - warmup_record["hourly_sent"],
            "current_week": warmup_record["current_week"],
            "next_reset": {
                "hourly": (last_reset + timedelta(hours=1)).isoformat(),
                "daily": (datetime.combine(now.date() + timedelta(days=1), datetime.min.time())).isoformat()
            }
        }
    
    def record_delivery_stats(self, domain: str, delivered: int, bounced: int, complaints: int) -> None:
        """Record delivery statistics and adjust warmup if thresholds exceeded."""
        total_sent = delivered + bounced
        bounce_rate = bounced / total_sent if total_sent > 0 else 0
        complaint_rate = complaints / delivered if delivered > 0 else 0
        
        # TODO: Fetch actual schedule from database
        schedule = self.schedules["conservative"]
        
        if bounce_rate > schedule.bounce_threshold:
            self.logger.warning(f"Domain {domain} bounce rate {bounce_rate:.3f} exceeds threshold {schedule.bounce_threshold}")
            # TODO: Pause sending and reduce volume
            
        if complaint_rate > schedule.complaint_threshold:
            self.logger.warning(f"Domain {domain} complaint rate {complaint_rate:.3f} exceeds threshold {schedule.complaint_threshold}")
            # TODO: Pause sending and investigate
        
        self.logger.info(f"Domain {domain} stats: {bounce_rate:.3f} bounce rate, {complaint_rate:.3f} complaint rate")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Domain warmup scheduler")
    parser.add_argument("--domain", required=True, help="Domain to warm up")
    parser.add_argument("--schedule", default="conservative", 
                       choices=["conservative", "moderate", "aggressive"],
                       help="Warmup schedule to use")
    
    args = parser.parse_args()
    
    scheduler = WarmupScheduler()
    scheduler.start_warmup(args.domain, args.schedule)
    
    # Check current limits
    limits = scheduler.check_send_limit(args.domain)
    print(f"Send limits for {args.domain}: {limits}")