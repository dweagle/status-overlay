import os
import logging
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
schedule_logger = logging.getLogger('schedule')

scheduler = BackgroundScheduler()

def schedule_main(main):
    schedule = os.getenv("SCHEDULE", "06:00").strip()

    time_parts = schedule.split(":")
    if len(time_parts) != 2:
        logger.warning("Invalid schedule format. Using default time: 07:00.")
        logger.warning("Fix the 'SCHEDULE' environment setting in Docker. HH:MM required.")
        schedule = "07:00"
        time_parts = schedule.split(":")

    hour, minute = time_parts
    hour = hour.zfill(2)
    schedule_logger.info(f"Scheduling the job to run at: {hour}:{minute}.")

    scheduler.add_job(
        main,
        CronTrigger(hour=hour, minute=minute),
        id="run_main_job",
        replace_existing=True,
    )

    scheduler.start()
    schedule_logger.info("Scheduler is running.")

    last_log_time = datetime.now() - timedelta(minutes=15)  # Log immediately on the first run
    log_interval = timedelta(minutes=15)  # 15-minute interval for logging this message

    try:
        while True:
            time.sleep(60)  # Sleep to reduce CPU usage
            current_time = datetime.now()
            if current_time - last_log_time >= log_interval:
                schedule_logger.info(f"Checking schedule...Next run at {hour}:{minute}.")
                last_log_time = current_time
    except (KeyboardInterrupt, SystemExit):
        schedule_logger.info("Shutting down scheduler...")
        scheduler.shutdown()