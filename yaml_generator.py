import os
import re
import sys
import signal
import logging
from settings import load_settings
from ruamel.yaml import YAML
from datetime import datetime, timedelta

# Initialize YAML handler for writing to files
yaml = YAML()
config_directory = '/config'

# Get logger from the main.py logging configuration
logger = logging.getLogger(__name__)  # This ensures you use the same logger instance from main.py

# Default settings
DEFAULTS = {
    'is_anime': False,
    'use_watch_region': True,
    'days_ahead': 28,
    'font': "{config_directory}/fonts/Inter-Medium.ttf",
    'font_size': 45,
    'font_color': '"#FFFFFF"',
    'horizontal_align': 'center',
    'vertical_align': 'top',
    'horizontal_offset': 0,
    'vertical_offset': 38,
    'back_width': 475,
    'back_height': 55,
    'back_radius': 30,
    'ignore_blank_results': "true",
    'timezone': 'America/New_York',
    'with_status': 0,
    'watch_region': 'US',
    'with_original_languge': 'en',
    'limit': 500,
    'with_watch_monetization_types': 'flatrate|free|ads|rent|buy',

    'use': True,

    'upcoming_back_color': '#FC4E03',
    'upcoming_text': 'U P C O M I N G',

    'new_back_color': '#008001',
    'new_text': 'N E W  S E R I E S',

    'new_airing_back_color': '#008001',
    'new_airing_text': 'N E W - A I R S',

    'airing_back_color': '#003880',
    'airing_text': 'A I R I N G',
    'today_text': 'A I R S  T O D A Y',
    'next_text': 'A I R I N G ',

    'ended_back_color': '#000000',
    'ended_text': 'E N D E D',

    'canceled_back_color': '#CF142B',
    'canceled_text': 'C A N C E L E D',

    'returning_back_color': '#103197',
    'returning_text': 'R E T U R N I N G',
    'returns_text': 'R E T U R N S ',

    'collection_use': True,
    'poster_source': 'url',
    'poster_path': 'https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/chart/Returning%20Soon.jpg',
    'visible_home': True,
    'visible_shared': True,
    "summary": 'TV Shows returning soon!',
    "minimum_items": '1',
    "delete_below_minimum": 'true',
    "sort_title": '!010_Returning'
}

timezone = os.getenv('TZ', DEFAULTS['timezone'])

def get_with_defaults(settings, primary_key, fallback_key=None):
    def is_valid_color(value):
        # Check if the value is a valid #RGB, #RGBA, #RRGGBB, or #RRGGBBAA color code.
        pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
        return isinstance(value, str) and re.match(pattern, value)

    # Retrieve the value from settings
    value = settings.get(primary_key)
    
    # If the value is None and a fallback_key is provided, use the fallback
    if value is None and fallback_key is not None:
        value = DEFAULTS.get(fallback_key)

    # Validate the value for font_color specifically
    if primary_key == 'font_color' and not is_valid_color(value):
        # Fallback to the default font_color if invalid
        value = DEFAULTS.get('font_color', '#FFFFFF')  # Default to #FFFFFF if no default exists

    # Perform string substitution for {main_directory}, if applicable
    if isinstance(value, str) and "{config_directory}" in value:
        value = value.replace("{config_directory}", config_directory)

    return value 

############################
# Create Overlay Template  #
############################
indentlog = "   " # indent for 3 spaces in log
indentlog2 = "      " # indent for 6 spaces in log
indentlog3 = "          " #indent for 9 spaces in log
indent2 = "    "  # indent 2 tabs (4 spaces) for kometa yaml spacing
indent3 = "      " # indent 3 tabs (6 spaces) for kometa yaml spacing

def create_library_yaml(config_directory):
    try:
        # Load settings dynamically when needed
        settings = load_settings(config_directory, log_message=False)

        # Date calculation for the script
        current_date = datetime.now()

        # Calculate date for 21 days prior to current date (used in New Series and New Airing Next sections)
        date_21_days_prior = (current_date - timedelta(days=21)).strftime('%m/%d/%Y')

        # Calculate dates for the Airing Series section
        date_15_days_prior = (current_date - timedelta(days=15)).strftime('%m/%d/%Y')

        # Calculate todays date for Airing Today section
        air_date_today= (current_date).strftime('%m/%d/%Y')

        # Calculate dates for the Returns Next section
        date_14_days_prior = (current_date - timedelta(days=14)).strftime('%m/%d/%Y')

        # Get section settings from loaded settings
        libraries = settings.get('libraries', {})

        overlay_settings = settings.get('overlay_settings', {})

        use_overlays = settings.get('use_overlays', {})

        # Get settings for each library and create yamls
        for library_name, library_settings in libraries.items():
            is_anime = get_with_defaults(library_settings, 'is_anime', 'is_anime')
            use_watch_region = get_with_defaults(library_settings, 'use_watch_region', 'use_watch_region')
            logger.info(f"-- Creating main template yaml for {library_name} --")

            # Define the template using a string with placeholders
            template_string = f"""# {library_name} Template
templates:
  {library_name} Status:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: <<weight>>
      name: text(<<text>>)
      font: "{get_with_defaults(overlay_settings, 'font', 'font')}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: <<font_color>>
      horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}
      vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'veritcal_align')}
      horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}
      vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}
      back_color: <<back_color>>
      back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}
      back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}
      back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results')}
    tmdb_discover:
      air_date.gte: <<date>>
      air_date.lte: <<date>>
      timezone: {timezone}
      with_status: <<status>>
"""
        
            # Conditionally add the "watch_region" and "with_watch_monetization_types" line
            if use_watch_region:
                logger.info(f"{indentlog}'watch_region' set to 'true'")
                logger.info(f"{indentlog2}Adding 'watch_region: {get_with_defaults(overlay_settings, 'watch_region', 'watch_region')}'.")
                logger.info(f"{indentlog2}Adding 'with_watch_monetization_type: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}'.")
                template_string += f"{indent3}watch_region: {get_with_defaults(overlay_settings, 'watch_region')}\n"
                template_string += f"{indent3}with_watch_monetization_types: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}\n"

            else:
                logger.info(f"{indentlog}'watch_region' set to 'false'")
                logger.info(f"{indentlog2}Removing 'watch_region'.")
                logger.info(f"{indentlog2}Removing 'with_watch_monetizaion_types'.")
            
            # Conditionally add the 'with_original_language' line
            if not is_anime:
                logger.info(f"{indentlog}'is_anime' set to 'false'")
                logger.info(f"{indentlog2}Adding 'with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}'.")
                template_string += f"{indent3}with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}\n"

            else:
                logger.info(f"{indentlog}'is_anime' set to 'true'")
                logger.info(f"{indentlog2}Removing 'with_original_language'.")

            # Add the 'limit' setting, always included
            template_string += f"{indent3}limit: {get_with_defaults(overlay_settings, 'limit', 'limit')}\n"
            
            # Add the overlays section (always present) after the templates section
            template_string += "\noverlays:"

            logger.info("Main template created")
            logger.info("")
            logger.info("-- Creating optional overlays --")

##########################
#### UPCOMING SERIES #####
##########################

            # Check if the upcoming_series section is used
            upcoming_series_settings = use_overlays.get("upcoming_series", {})
            if get_with_defaults(upcoming_series_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'Upcoming' set to true. Creating 'Upcoming' overlay.")

                #Add Upcoming section to the template
                upcoming_section = f"""
# UPCOMING SERIES OVERLAY
  {library_name} Upcoming Series:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: 100
      name: text({get_with_defaults(upcoming_series_settings, 'text', 'upcoming_text')})
      font: "{get_with_defaults(overlay_settings, 'font', 'font')}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: "{get_with_defaults(upcoming_series_settings, 'font_color', 'font_color')}"
      horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}
      vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}
      horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}
      vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}
      back_color: "{get_with_defaults(upcoming_series_settings, 'back_color', 'upcoming_back_color')}"
      back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}
      back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}
      back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results')}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      release.after: today
"""

                template_string += upcoming_section
            else:
                logger.info(f"{indentlog}'Upcoming' set to false. 'Upcoming' overlay not created.")

##########################
####    NEW SERIES   #####
##########################

            # Check if the new_series section is used
            new_series_settings = use_overlays.get("new_series", {})
            if get_with_defaults(new_series_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'New Series' set to true. Creating 'New Series' overlay.")
                # Add New Series section to template
                new_series_section = f"""
# NEW SERIES BANNER/TEXT
  {library_name} New Series:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: 76
      name: text({get_with_defaults(new_series_settings, 'text', 'new_text')})
      font: "{get_with_defaults(overlay_settings, 'font', 'font')}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: "{get_with_defaults(new_series_settings, 'font_color', 'font_color')}"
      horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}
      vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}
      horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}
      vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_align')}
      back_color: "{get_with_defaults(new_series_settings, 'back_color', 'new_back_color')}"
      back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}
      back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}
      back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results')}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
        - ended
        - canceled
      first_episode_aired.after: {date_21_days_prior}
"""
                template_string += new_series_section  # Add New Series section at the end
            else:
                logger.info(f"{indentlog}'New Series' set to false. Creating 'New Series' overaly.")


##########################
###  NEW AIRING NEXT   ###
##########################

            # New Airing Next section - repeated 14 times
            new_airing_next_settings = use_overlays.get('new_airing_next', {})

            # Calculate dates for the New Airing Next sections
            new_airing_next_dates = [(current_date + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(1, 15)]

            if get_with_defaults(new_airing_next_settings, "use", "use"):  # If 'use' is True, include this section
                logger.info(f"{indentlog}'New Airing Next' set to true. Creating 'New Airing Next' overlay.")
                
                for i, next_day_date_str in enumerate(new_airing_next_dates, start=1):  # Loop over the next 14 days
                    next_day_date = datetime.strptime(next_day_date_str, '%m/%d/%Y')
                    mmdd = next_day_date.strftime('%m/%d')
                    mmddyyyy = next_day_date.strftime('%m/%d/%Y')

                    weight = 90 - i + 1  # Start with weight 89 and decrease by 1 each iteration
                    
                    new_airing_next_section = f"""
# NEW AIRING NEXT BANNER/TEXT DAY {i}
  {library_name} New Airing Next {mmddyyyy}: 
    variables: {{text: {get_with_defaults(new_airing_next_settings, 'text', 'new_airing_text')} {mmdd}, weight: {weight}, font_color: "{get_with_defaults(new_airing_next_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(new_airing_next_settings, 'back_color', 'new_airing_back_color')}", date: {mmddyyyy}, status: 0}}
    template: {{name: {library_name} Status}}
    filters:
      first_episode_aired.after: {date_21_days_prior}
    """

                    template_string += new_airing_next_section  # Add each "New Airing Next" section

            else:
                logger.info(f"{indentlog}'New Airing Next' set to false. 'New Airing Next' Overlay not created")
                
##########################
####  AIRING SERIES  #####
##########################

            # Check if the airing_series section is used
            airing_series_settings = use_overlays.get("airing_series", {})
            if get_with_defaults(airing_series_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'Airing Series' set to true. Creating 'Airing' overlay")
                
                # Add Airing Series section to template
                airing_series_section = f"""
# AIRING SERIES BANNER/TEXT
  {library_name} Airing Series:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: 43
      name: text({get_with_defaults(airing_series_settings, 'text', 'airing_text')})
      font: "{get_with_defaults(overlay_settings, 'font', 'font')}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: "{get_with_defaults(airing_series_settings, 'font_color', 'font_color')}"
      horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}
      vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}
      horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}
      vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}
      back_color: "{get_with_defaults(airing_series_settings, 'back_color', 'airing_back_color')}"
      back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}
      back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}
      back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results')}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      last_episode_aired.after: {date_15_days_prior}
    """
                template_string += airing_series_section  # Add Airing Series section at the end

            else:
                logger.info(f"{indentlog}'Airing Series' set to false. 'Airing' Overlay not created.")

##########################
####  AIRING TODAY   #####
##########################

            # Check if the Airing Today section is used
            airing_today_settings = use_overlays.get("airing_today", {})
            if get_with_defaults(airing_today_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'Airing Today' set to true. Creating 'Airing Today' overlay.")
                
                # is_anime = get_with_defaults(library_settings, 'is_anime')
                # use_watch_region = get_with_defaults(library_settings, 'use_watch_region')
                
                # Add Airing Today section to template
                airing_today_section = f"""
# AIRING TODAY BANNER/TEXT
  {library_name} Airing Today:
    variables: {{text: {get_with_defaults(airing_today_settings, 'text', 'today_text')}, weight: 75, font_color: "{get_with_defaults(airing_today_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(airing_today_settings, 'back_color', 'airing_back_color')}", date: {air_date_today}, status: 0}}
    template: {{name: {library_name} Status}}
"""
                template_string += airing_today_section  # Add Airing Today section at the end

            else:
                logger.info(f"{indentlog}Airing Today set to false. 'Airing Today' overlay not created")

##########################
####   AIRING NEXT   #####
##########################

            # Airing Next section - repeated according to days_ahead setting
            airing_next_settings = use_overlays.get('airing_next', {})

            # Calculate dates for Airing Next Section based off days_ahead in settings
            days_ahead = min(settings.get('days_ahead', 28), 30)  # Ensure it doesn't exceed 30 days
            airing_next_dates = [(current_date + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(1, days_ahead + 1)]

            if get_with_defaults(airing_next_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'Airing Next' set to true. 'days_ahead:' set to {days_ahead}. Creating {days_ahead} 'Airing Next' overlay/s")
                
                for i, next_day_date_str in enumerate(airing_next_dates, start=1):  # Loop over the next x days
                    next_day_date = datetime.strptime(next_day_date_str, '%m/%d/%Y')
                    mmdd = next_day_date.strftime('%m/%d')
                    mmddyyyy = next_day_date.strftime('%m/%d/%Y')

                    weight = 74 - i + 1  # Start with weight 74 and decrease by 1 each iteration
                    
                    airing_next_section = f"""
# AIRING NEXT BANNER/TEXT DAY {i}
  {library_name} Airing Next {mmddyyyy}:
    variables: {{text: {get_with_defaults(airing_next_settings, 'text', 'next_text')} {mmdd}, weight: {weight}, font_color: "{get_with_defaults(airing_next_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(airing_next_settings, 'back_color', 'airing_back_color')}", date: {mmddyyyy}, status: 0}}
    template: {{name: {library_name} Status}}
    filters:
      last_episode_aired.after: {date_15_days_prior}
    """

                    template_string += airing_next_section  # Add each "New Airing Next" section
            else:
                logger.info(f"{indentlog}'Airing Next' set to false. 'Airing Next' overlay not created.")

##########################
####   ENDED SERIES   ####
##########################

            # Check if the Ended Series section is used
            ended_series_settings = use_overlays.get("ended_series", {})

            if get_with_defaults(ended_series_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'Ended Series' set to true. Creating 'Ended Series' overlay.")
                
                # Add Ended Series section to template
                ended_series_section = f"""
# ENDED SERIES BANNER/TEXT
  {library_name} Ended Series:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: 9
      name: text({get_with_defaults(ended_series_settings, 'text', 'ended_text')}) 
      font: "{get_with_defaults(overlay_settings, 'font', 'font')}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: "{get_with_defaults(ended_series_settings, 'font_color', 'font_color')}"
      horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}
      vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}
      horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}
      vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}
      back_color: "{get_with_defaults(ended_series_settings, 'back_color', 'ended_back_color')}"
      back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}
      back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}
      back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results')}
    plex_all: true
    filters:
      tmdb_status:
        - ended
    """
                template_string += ended_series_section  # Add Ended Series section at the end
            else:
                logger.info(f"{indentlog}'Ended Sereies' set to false. 'Ended Series' overlay not created")
            
##########################
#### CANCELED SERIES  ####
##########################

            # Check if the Canceled Series section is used
            canceled_series_settings = use_overlays.get("canceled_series", {})

            if get_with_defaults(canceled_series_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'Canceled Series' set to true. Creating 'Canceled Series' overlay.")
                
                # Add Canceled Series section to template
                canceled_series_section = f"""
# CANCELED SERIES BANNER/TEXT
  {library_name} Canceled Series:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: 10
      name: text({get_with_defaults(canceled_series_settings, 'text', 'canceled_text')}) 
      font: "{get_with_defaults(overlay_settings, 'font', 'font')}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: "{get_with_defaults(canceled_series_settings, 'font_color', 'font_color')}"
      horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}
      vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}
      horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_align')}
      vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}
      back_color: "{get_with_defaults(canceled_series_settings, 'back_color', 'canceled_back_color')}"
      back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}
      back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_width')}
      back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results')}
    plex_all: true
    filters:
      tmdb_status:
        - canceled
    """
                template_string += canceled_series_section  # Add Ended Series section at the end
            else:
                logger.info(f"{indentlog}'Canceled Series' set to false. 'Canceled Series' overlay not created.")
            
##########################
#### RETURNING SERIES ####
##########################

            # Check if the Returning Series section is used
            returning_series_settings = use_overlays.get("returning_series", {})

            if get_with_defaults(returning_series_settings, "use", "use"):  # If "use" is True, include this section
                logger.info(f"{indentlog}'Returning Series' set to true. Creating 'Returning' overlay.")
                
                # Add Returning Series section to template
                returning_series_section = f"""
# RETURNING SERIES BANNER/TEXT
  {library_name} Returning Series:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: 13
      name: text({get_with_defaults(returning_series_settings, 'text', 'returning_text')}) 
      font: "{get_with_defaults(overlay_settings, 'font', 'font')}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: "{get_with_defaults(returning_series_settings, 'font_color', 'font_color')}"
      horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}
      vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}
      horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_align')}
      vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}
      back_color: "{get_with_defaults(returning_series_settings, 'back_color', 'returning_back_color')}"
      back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}
      back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}
      back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results')}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
    """
                template_string += returning_series_section  # Add Returning Series section at the end
            else:
                logger.info(f"{indentlog}'Returning' set to false. 'Returning' overlay not created")

##########################
####   RETURNS NEXT  #####
##########################

            # Returns Next section - repeated according to days_ahead setting
            returns_next_settings = use_overlays.get('returns_next', {})

            # Calculate dates for Returns Next Section based off days_ahead in settings
            days_ahead = min(settings.get('days_ahead', 28), 30)  # Ensure it doesn't exceed 30 days
            returns_next_dates = [(current_date + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(1, days_ahead + 1)]

            if get_with_defaults(returns_next_settings, "use", "use"):  # If 'use' is True, include this section
                logger.info(f"{indentlog}'Returns Next' set to true. 'days_ahead:' set to {days_ahead}. Creating {days_ahead} 'Returns Next' overlay/s")
                
                for i, next_day_date_str in enumerate(returns_next_dates, start=1):  # Loop over the next x days
                    next_day_date = datetime.strptime(next_day_date_str, '%m/%d/%Y')
                    mmdd = next_day_date.strftime('%m/%d')
                    mmddyyyy = next_day_date.strftime('%m/%d/%Y')

                    weight = 43 - i + 1  # Start with weight 43 and decrease by 1 each iteration
                    
                    returns_next_section = f"""
# RETURNS NEXT BANNER/TEXT DAY {i}
  {library_name} Returns Next {mmddyyyy}:
    variables: {{text: {get_with_defaults(returns_next_settings, 'text', 'returns_text')} {mmdd}, weight: {weight}, font_color: "{get_with_defaults(returns_next_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(returns_next_settings, 'back_color', 'returning_back_color')}", date: {mmddyyyy}, status: 0}}
    template: {{name: {library_name} Status}}
    filters:
      last_episode_aired.before: {date_14_days_prior}
    """

                    template_string += returns_next_section  # Add each "Returns Next" section

            else:
                logger.info(f"{indentlog}'Returns Next' set to false. 'Returns Next' overlay/s not created")

############################
# WRITE TEMPLATE YAML FILE #
############################

            # Determine the save folder for overlays
            overlay_save_folder = overlay_settings.get('overlay_save_folder')

            if overlay_save_folder and isinstance(overlay_save_folder, str):
                overlay_save_folder = overlay_save_folder.strip()

            else:
                overlay_save_folder = ''

            if overlay_save_folder:
                logger.info(f"Using custom overlay save folder: {overlay_save_folder}")
            else:
                logger.info("No custom overlay save folder provided.  Using /config folder.")
                overlay_save_folder = config_directory

            # Ensure the save folder exists and exit script if it doesn't
            if not os.path.exists(overlay_save_folder):
                logger.warning(f"Overlay folder doesn't exist or permissions not set.  Exiting script")
                logger.warning(f"If using path outside of mounted container config volume, you need to mount a volume to this.")
                exit()

            # Normalize the library name
            normalized_library_name = library_name.lower().replace(' ', '-')

            # Create the output file path
            output_file_path = os.path.join(overlay_save_folder, f"overlay-status-{normalized_library_name}.yml")
            
            try:
                with open(output_file_path, 'w') as file:
                    file.write(template_string)
                logger.info(f"Generated overlay for {library_name} at '{output_file_path}'")
                logger.info("")
            except Exception as e:
                logger.error(f"Error generating overlay for {library_name}: {e}")
                logger.info("")

    except Exception as e:
        logger.error(f"An error occurred while generating overlay files: {e}")

#############################
# RETURNING SOON COLLECTION #
#############################

def create_collection_yaml(config_directory):
    try:
        # Load settings dynamically when needed
        settings = load_settings(config_directory, log_message=False)

        # Date calculation for the script
        current_date = datetime.now()

        # Calculate date for 21 days prior to current date
        date_45_days_prior = (current_date - timedelta(days=45)).strftime('%m/%d/%Y')

        # Calculate the date tomorrow
        air_date_tomorrow = (current_date + timedelta(days=1)).strftime('%m/%d/%Y')
        
        # Calculate 30 days past the current date
        thirty_days_past = (current_date + timedelta(days=30)).strftime('%m/%d/%Y')
        
        # Get section settings from loaded settings
        libraries = settings.get('libraries', {})

        overlay_settings = settings.get('overlay_settings', {})

        collection_settings = settings.get('returning_soon_collection', {})

        # Get settings for each library and create yamls
        for library_name, library_settings in libraries.items():
            is_anime = get_with_defaults(library_settings, 'is_anime', 'is_anime')
            use_watch_region = get_with_defaults(library_settings, 'use_watch_region', 'use_watch_region')
            
            if get_with_defaults(collection_settings, "use", "collection_use"):  # If "use" is True, include this section
                logger.info(f"-- Returning Soon Collection 'use:' set to true. Creating Returning Soon Collection yaml for {library_name}. --")

                # Create Returning Soon collection
                template_string = f"""
# RETURNING SOON COLLECTION
collections:
  Returning Soon:
    {get_with_defaults(collection_settings, 'poster_source', 'poster_source')}_poster: "{get_with_defaults(collection_settings, 'poster_path', 'poster_path')}"
    collection_order: custom
    visible_home: {get_with_defaults(collection_settings, 'visible_home', 'visible_home')}
    visible_shared: {get_with_defaults(collection_settings, 'visible_shared', 'visible_shared')}
    sync_mode: sync
    summary: "{get_with_defaults(collection_settings, 'summary', 'summary')}"
    minimum_items: {get_with_defaults(collection_settings, 'minimum_items', 'minimum_items')}
    delete_below_minimum: {get_with_defaults(collection_settings, 'delete_below_minimum', 'delete_below_minimum')}
    sort_title: "{get_with_defaults(collection_settings, 'sort_title', 'sort_title')}"
    tmdb_discover:
      air_date.gte: {air_date_tomorrow}
      air_date.lte: {thirty_days_past}
      timezone: {timezone}
      with_status: 0
"""
                # Conditionally add the "watch_region" and "with_watch_monetization_types" line
                if use_watch_region:
                    logger.info(f"{indentlog}'watch_region' set to 'true'")
                    logger.info(f"{indentlog2}Adding 'watch_region: {get_with_defaults(overlay_settings, 'watch_region', 'watch_region')}'.")
                    logger.info(f"{indentlog2}Adding 'with_watch_monetization_type: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}'.")
                    template_string += f"{indent3}watch_region: {get_with_defaults(overlay_settings, 'watch_region', 'watch_region')}\n"
                    template_string += f"{indent3}with_watch_monetization_types: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}\n"

                else:
                    logger.info(f"{indentlog}'watch_region' set to 'false'")
                    logger.info(f"{indentlog2}Removing 'watch_region'.")
                    logger.info(f"{indentlog2}Removing 'with_watch_monetizaion_types'.")
                
                # Conditionally add the 'with_original_language' line
                if not is_anime:
                    logger.info(f"{indentlog}'is_anime' set to 'false'")
                    logger.info(f"{indentlog2}Adding 'with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}'.")
                    template_string += f"{indent3}with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}\n"

                else:
                    logger.info(f"{indentlog}'is_anime' set to 'true'")
                    logger.info(f"{indentlog2}Removing 'with_original_language'.")

                    # Add the 'limit' setting, always included
                template_string += f"{indent3}limit: {get_with_defaults(overlay_settings, 'limit', 'limit')}\n"
                
                template_string += f"{indent2}filters:\n"
                template_string += f"{indent3}last_episode_aired.before: {date_45_days_prior}\n"

############################
#  WRITE COLLECTION YAML   #
############################

                # Determine the save folder for overlays
                collection_save_folder = collection_settings.get('collection_save_folder')

                if collection_save_folder and isinstance(collection_save_folder, str):
                    collection_save_folder = collection_save_folder.strip()

                else:
                    collection_save_folder = ''

                if collection_save_folder:
                    logger.info(f"Using custom collection save folder: {collection_save_folder}")
                else:
                    logger.info("No custom collection save folder provided.  Using /config folder.")
                    collection_save_folder = config_directory

                # Ensure the save folder exists and exit script if it doesn't
                if not os.path.exists(collection_save_folder):
                    logger.warning(f"Collection folder doesn't exist or permissions not set.  Exiting script")
                    logger.warning(f"If using path outside of mounted container config volume, you need to mount a volume to this.")
                    exit()

                # Normalize the library name
                normalized_library_name = library_name.lower().replace(' ', '-')

                # Create the output file path
                output_file_path = os.path.join(collection_save_folder, f"collection-returning-soon-{normalized_library_name}.yml")
                
                try:
                    with open(output_file_path, 'w') as file:
                        file.write(template_string)
                    logger.info(f"-- Generated Returning Soon Collection for {library_name} at '{output_file_path}' --")
                    logger.info("")
                except Exception as e:
                    logger.error(f"Error generating collection for {library_name}: {e}")
                    logger.info("")


            else:
                logger.info(f"{indentlog}'Returning Soon' collection 'use:' set to false. 'Returning Soon' collection not created")

    except Exception as e:
        logger.error(f"An error occurred while generating collection files: {e}")
