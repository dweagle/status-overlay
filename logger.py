import os
import logging
from logging.handlers import RotatingFileHandler

config_directory = '/config'
log_directory = os.path.join(config_directory, "logs")

def log_setup():

    log_path =  os.path.join(log_directory, "status.log")
    need_roll = not os.path.isfile(log_path)

    os.makedirs(log_directory, exist_ok = True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_handler = RotatingFileHandler(log_path, maxBytes = 5 * 1024 * 1024, backupCount=5)
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)-9s %(message)s', "%m/%d/%Y %H:%M")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)

    console_handler = logging.StreamHandler()
    console_handler. setFormatter(log_formatter)
    logger.addHandler(console_handler)

    if need_roll:
        logger.info(f"Log folder created at '{log_directory}'")
    else:
        log_handler.doRollover()

    logger.info(f"Logging started. Logs located at '{log_path}'.")

    # apscheduler messages for console only
    apscheduler_logger = logging.getLogger('apscheduler')
    apscheduler_logger.setLevel(logging.WARNING)
    apscheduler_console_handler = logging.StreamHandler()
    apscheduler_console_handler.setFormatter(log_formatter)
    apscheduler_logger.addHandler(apscheduler_console_handler)
    apscheduler_logger.propagate = False

    # running schedule notification for console only
    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(logging.INFO)
    schedule_console_handler = logging.StreamHandler()
    schedule_console_handler.setFormatter(log_formatter)
    schedule_logger.addHandler(schedule_console_handler)
    schedule_logger.propagate = False
