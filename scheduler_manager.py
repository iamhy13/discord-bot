"""
Scheduler Manager for handling multiple spawn notification schedules.
"""

import logging
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import pytz
from config import SPAWN_CONFIGS, BUCHAREST_TZ, START_TIME

logger = logging.getLogger(__name__)

class SpawnSchedulerManager:
    """Manages multiple spawn notification schedules."""
    
    def __init__(self, message_callback):
        """
        Initialize the scheduler manager.
        
        Args:
            message_callback: Async function to call when sending messages
        """
        self.scheduler = AsyncIOScheduler(timezone=BUCHAREST_TZ)
        self.message_callback = message_callback
        self.is_running = False
    
    async def setup_schedules(self):
        """Set up all spawn notification schedules."""
        try:
            logger.info("Setting up spawn notification schedules...")
            
            for config in SPAWN_CONFIGS:
                await self._add_spawn_schedule(config)
            
            logger.info(f"Successfully configured {len(SPAWN_CONFIGS)} spawn schedules")
            
        except Exception as e:
            logger.error(f"Failed to setup schedules: {e}")
            raise
    
    async def _add_spawn_schedule(self, config):
        """
        Add a single spawn schedule.
        
        Args:
            config: Dictionary containing spawn configuration
        """
        try:
            job_id = config["job_id"]
            followup_job_id = config["followup_job_id"]
            interval_hours = config["interval_hours"]
            message = config["message"]
            followup_message = config["followup_message"]
            name = config["name"]
            
            # Calculate the initial start time in Bucharest timezone
            now_bucharest = datetime.now(BUCHAREST_TZ)
            start_datetime = now_bucharest.replace(
                hour=START_TIME.hour,
                minute=START_TIME.minute,
                second=0,
                microsecond=0
            )
            
            # If the start time has passed today, schedule for the next occurrence
            if start_datetime <= now_bucharest:
                # Calculate next occurrence based on interval
                hours_passed = (now_bucharest - start_datetime).total_seconds() / 3600
                intervals_passed = int(hours_passed // interval_hours) + 1
                start_datetime = start_datetime.replace(
                    hour=(START_TIME.hour + (intervals_passed * interval_hours)) % 24
                )
                
                # If we overflow to next day, adjust the date
                if (START_TIME.hour + (intervals_passed * interval_hours)) >= 24:
                    days_to_add = (START_TIME.hour + (intervals_passed * interval_hours)) // 24
                    start_datetime = start_datetime.replace(
                        day=start_datetime.day + days_to_add,
                        hour=(START_TIME.hour + (intervals_passed * interval_hours)) % 24
                    )
            
            # Create followup start time (5 minutes after main notification)
            from datetime import timedelta
            followup_start_datetime = start_datetime + timedelta(minutes=5)
            
            # Create interval trigger for main notification
            trigger = IntervalTrigger(
                hours=interval_hours,
                start_date=start_datetime,
                timezone=BUCHAREST_TZ
            )
            
            # Create interval trigger for followup notification
            followup_trigger = IntervalTrigger(
                hours=interval_hours,
                start_date=followup_start_datetime,
                timezone=BUCHAREST_TZ
            )
            
            # Add main job to scheduler
            self.scheduler.add_job(
                self._send_spawn_notification,
                trigger=trigger,
                args=[message, name],
                id=job_id,
                name=f"{name} Spawn Notification",
                misfire_grace_time=60,  # Allow 60 seconds grace time for missed jobs
                coalesce=True,  # Coalesce missed jobs
                max_instances=1  # Only one instance of each job at a time
            )
            
            # Add followup job to scheduler
            self.scheduler.add_job(
                self._send_spawn_notification,
                trigger=followup_trigger,
                args=[followup_message, f"{name} Followup"],
                id=followup_job_id,
                name=f"{name} Followup Notification",
                misfire_grace_time=60,
                coalesce=True,
                max_instances=1
            )
            
            logger.info(f"Scheduled {name} notifications every {interval_hours}h starting at {start_datetime}")
            logger.info(f"Scheduled {name} followup notifications every {interval_hours}h starting at {followup_start_datetime}")
            
        except Exception as e:
            logger.error(f"Failed to add schedule for {config.get('name', 'unknown')}: {e}")
            raise
    
    async def _send_spawn_notification(self, message, spawn_name):
        """
        Send a spawn notification message.
        
        Args:
            message: The message to send
            spawn_name: Name of the spawn for logging
        """
        try:
            logger.info(f"Sending {spawn_name} spawn notification")
            await self.message_callback(message)
            logger.info(f"Successfully sent {spawn_name} notification")
            
        except Exception as e:
            logger.error(f"Failed to send {spawn_name} notification: {e}")
    
    async def start(self):
        """Start the scheduler."""
        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                logger.info("Spawn scheduler started successfully")
                
                # Log next run times for all jobs
                self._log_next_run_times()
                
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler."""
        try:
            if self.is_running:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                logger.info("Spawn scheduler stopped")
                
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def _log_next_run_times(self):
        """Log the next run times for all scheduled jobs."""
        try:
            jobs = self.scheduler.get_jobs()
            logger.info("Next scheduled spawn notifications:")
            
            for job in jobs:
                next_run = job.next_run_time
                if next_run:
                    # Convert to Bucharest time for logging
                    next_run_bucharest = next_run.astimezone(BUCHAREST_TZ)
                    logger.info(f"  {job.name}: {next_run_bucharest.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                else:
                    logger.warning(f"  {job.name}: No next run time scheduled")
                    
        except Exception as e:
            logger.error(f"Error logging next run times: {e}")
    
    def get_status(self):
        """Get the current status of all scheduled jobs."""
        try:
            jobs = self.scheduler.get_jobs()
            status = {
                "running": self.is_running,
                "job_count": len(jobs),
                "jobs": []
            }
            
            for job in jobs:
                job_info = {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                status["jobs"].append(job_info)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {"error": str(e)}
