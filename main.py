import os
import shutil
import signal
import sys
import logging
import argparse
from logger import log_setup
from scheduler import schedule_main, scheduler
from settings import create_settings_file, update_settings_file
from validate_settings import validate_settings
from yaml_generator import create_library_yaml, create_collection_yaml

config_directory = '/config'
settings_file_path = os.path.join(config_directory, "overlay-settings.yml")
run_now = os.getenv("RUN_NOW", "false").strip().lower() == "true"
logger = logging.getLogger(__name__)
font_src = "/fonts"
font_dest = "/config/fonts"

def graceful_shutdown(signal_num, _):
    logger.info(f"Received signal {signal_num} ({signal.Signals(signal_num).name}). Initiating graceful shutdown...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    sys.exit(0)

def main():
    if not os.path.exists(font_dest):
        shutil.copytree(font_src, font_dest)

    try:
        if not os.path.exists(settings_file_path):
            logger.info(f"Settings file not found at '{settings_file_path}'.")
            logger.info("Creating default settings file.")

            create_settings_file(config_directory)
            
            logger.info("Please edit the 'overlay-settings.yml' to your preferred Kometa settings and rerun the script.")
            return  # Exit the script after creating the settings file
        
        logger.info("Updating settings file with missing sections...")
        update_settings_file(config_directory)

        logger.info("Validating settings file...")
        if not validate_settings(config_directory):
            logger.error("Validation failed. Please fix the issues in the settings file and rerun the script.")
            return  # Exit if validation fails
        
        # Generate overlay files and collection files after validation succeeds
        logger.info("")
        logger.info("Validation successful. Generating overlay files for Kometa.")
        logger.info("")

        create_library_yaml(config_directory)
        create_collection_yaml(config_directory)

        logger.info("All library overlay and collection files created.")
        logger.info("")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    log_setup()
    
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)

    parser = argparse.ArgumentParser(description="Run the main script.")
    parser.add_argument('-r', '--run-now', action='store_true', help="Run the script immediately and bypass the schedule.")
    
    args = parser.parse_args()
    run_now_env = os.getenv("RUN_NOW", "false").strip().lower() == "true"
    
    if args.run_now or run_now_env:
        logger.info("RUN_NOW is set to true. Running main.py immediately.")
        main()
        if args.run_now:
            logger.info("Exiting script after manual run.")
            sys.exit(0)        
        logger.info("Reverting to scheduled runs.")
        schedule_main(main)
    else:
        logger.info("RUN_NOW is set to false. Scheduling main.py.")
        schedule_main(main)
