import os
import re
import logging
from ruamel.yaml import YAML
from settings import load_settings

yaml = YAML()

# Get logger from the main.py logging configuration
logger = logging.getLogger(__name__)  # This ensures you use the same logger instance from main.py
settings_filename = "overlay-settings.yml"

############################
# Validate Settings File   #
############################

def validate_settings(main_directory):
    settings_file_path = os.path.join(main_directory, settings_filename)

    if not os.path.exists(settings_file_path):
        logger.error(f"Settings file not found at '{settings_file_path}.")
        return False
    
    try:
        # Load settings dynamically when needed
        settings = load_settings(main_directory)
        
        indent1 = "  " # indent for 1st level sections
        indent2 = "    " # indent for 2nd level sectoins
        
        if not isinstance(settings, dict):
            logger.error("Settings file format is invalid. Expected a dictionary. Missing 'libraries:', 'overlay_settings:', 'use_overlays:', and 'returning_soon_collection:' top level sections.")
            return False
        
############################
#   Top Level Validation   #
############################
# Validation of top level sections and libraries - Will cause script stopping on failure

        # Check if the 'libraries' top-level section exists and is non-empty
        if 'libraries' not in settings or not isinstance(settings['libraries'], dict) or not settings['libraries']:
            logger.error("The settings file does not contain a valid 'libraries' section or it is empty.")
            logger.error("Exiting script... Add top level 'libaries:' section with second level 'library name': [is_anime:, use_watch_region:] with settings.")
            return False  # Indicate failure

        libraries = settings['libraries']

        # Check if the 'default_settings' section exists and is non-empty
        if 'overlay_settings' not in settings or not isinstance(settings['overlay_settings'], dict) or not settings['overlay_settings']:
            logger.error("The settings file does not contain a valid 'overlay_settings' section or it is empty.")
            logger.error("Exiting script... Add top level 'overlay_settings:' section with second level overlay settings.")
            return False  # Indicate failure

        overlay_settings = settings['overlay_settings']

        # Check if the 'use_overlays' section exists and is non-empty
        if 'use_overlays' not in settings or not isinstance(settings['use_overlays'], dict) or not settings['use_overlays']:
            logger.error("The settings file does not contain a valid 'use_overlays' section or it is empty.")
            logger.error("Exiting script... Add top level 'use_overlays' section with second level 'overlay_name: [use:, back_color:, text:, font_color:, ]")
            return False  # Indicate failure

        use_overlays = settings['use_overlays']

        # Check if the 'returning_soon_collection' section exists and is non-empty
        if 'returning_soon_collection' not in settings or not isinstance(settings['returning_soon_collection'], dict) or not settings['returning_soon_collection']:
            logger.error("The settings file does not contain a valid 'returning_soon_collection' section or it is empty.")
            logger.error("Exiting script... Add top level 'returnign_soon_collection' section with second level 'use:, collection_save_folder:, poster_source:, poster_path:, visible_home:, and visible_shared:'")
            return False  # Indicate failure

        collection_settings = settings['returning_soon_collection']

        # Iterate through each library in the 'libraries' section
        logger.info("libraries:")
        
        for library_name, library_settings in libraries.items():
            # Check if the second-level library name has settings
            logger.info(f"  {library_name}:")
            if not library_settings:
                logger.error(f"No settings found for library: {library_name}")
                logger.error("Exiting script...")
                return False  # Indicate failure

############################
# Library/Default Settings #
############################

#Validation of library and default settings - if missing or invalid, will cause script to use defaults
            
            # Check for third-level settings 'is_anime' and 'use_watch_region'
            # Validate 'is_anime' setting
            is_anime = library_settings.get('is_anime', None)
            if is_anime is None:
                logger.warning(f"{indent2}is_anime: Missing 'is_anime' setting for library: {library_name}. Defaulting to False.")
            elif not isinstance(is_anime, bool):
                logger.warning(f"{indent2}is_anime: 'is_anime' setting for library: {library_name} is not a valid True or False. Defaulting to False.")
            else:
                logger.info(f"{indent2}is_anime: {is_anime}")

            # Validate 'use_watch_region' setting
            use_watch_region = library_settings.get('use_watch_region', None)
            if use_watch_region is None:
                logger.warning(f"{indent2}use_watch_region: Missing 'use_watch_region' setting for library: {library_name}. Defaulting to True.")
            elif not isinstance(use_watch_region, bool):
                logger.warning(f"{indent2}use_watch_region: 'use_watch_region' setting for library: {library_name} is not a valid True or False. Defaulting to True.")
            else:
                logger.info(f"{indent2}use_watch_region: {use_watch_region}")

        # Validate individual settings within 'overlay_settings'
        logger.info("")
        logger.info("overlay_settings:")
        days_ahead = overlay_settings.get('days_ahead')
        if days_ahead is None:
            logger.warning(f"{indent1}days_ahead: Missing 'days_ahead' value. Defaulting to 28 days.")
        elif not isinstance(days_ahead, int) or days_ahead < 0 or days_ahead > 30:
            logger.warning(f"{indent1}days_ahead: Invalid 'days_ahead' value: {days_ahead}. Enter 1 to 30. Max is 30.")
            return False  # Log an issue and exit if the value is invalid
        else:
            logger.info(f"{indent1}days_ahead: {days_ahead}")

        overlay_save_folder = overlay_settings.get('overlay_save_folder', None)
        if overlay_save_folder is None:
            logger.warning(f"{indent1}overalay_save_folder: 'overlay_save_folder' not provided. Defaulting to '{main_directory}.")
        else:
            logger.info(f"{indent1}overlay_save_folder: {overlay_save_folder}")

        font = overlay_settings.get('font', None)
        if font is None:
            logger.warning(f"{indent1}font_path: 'font' path not provided. Defaulting to '{main_directory}/fonts/Inter-Medium.ttf'.")
        else:
            logger.info(f"{indent1}font: {font}")

        font_size = overlay_settings.get('font_size')
        if font_size is None:
            logger.warning(f"{indent1}font_size: 'font_size is missing. Defaulting to 45.")
        elif not isinstance(font_size, int) or font_size <= 0:
            logger.warning(f"{indent1}font_size: 'font_size' invalid value: {font_size}. Defaulting to 45.")
        else:
            logger.info(f"{indent1}font_size: {font_size}")

        font_color = overlay_settings.get('font_color')
        pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
        if font_color is None:
            logger.warning(f"{indent1}font_color: 'font_color' is missing. kometa requires #RGB, #RGBA, #RRGGBB or #RRGGBBAA. Defaulting to '#FFFFFF'.")
        elif not re.match(pattern, font_color):
            logger.warning(f"{indent1}font_color: Invalid 'font_color' value: {font_color}.  Defaulting to #FFFFFF.")
        else:
            logger.info(f"{indent1}font_color: {font_color}")

        horizontal_align = overlay_settings.get('horizontal_align')
        if horizontal_align is None:
            logger.warning(f"{indent1}horizontal_align: 'horizontal_align' is missing or blank.  Defaulting to 'center'.")
        elif horizontal_align not in ['center', 'left', 'right']:
            logger.warning(f"{indent1}horizontal_align: Invalid 'horizontal_align' value: {horizontal_align}. Must be 'center', 'left' or 'right'. Defaulting to 'center'.")
        else:
            logger.info(f"{indent1}horizontal_align: {horizontal_align}")

        vertical_align = overlay_settings.get('vertical_align')
        if vertical_align is None:
            logger.warning(f"{indent1}vertical_align: 'vertical_align' is missing or blank.  Defaulting to 'center'.")
        elif horizontal_align not in ['top', 'center', 'bottom']:
            logger.warning(f"{indent1}vertical_align: Invalid 'vertical_align' value: {vertical_align}. Must be 'top', 'center' or 'bottom'. Defaulting to 'top'.")
        else:
            logger.info(f"{indent1}vertical_align: {vertical_align}")

        horizontal_offset = overlay_settings.get('horizontal_offset')
        if horizontal_offset is None:
            logger.warning(f"{indent1}horizontal_offset: 'horizontal_offset' is missing. Defaulting to 0.")
        elif not isinstance(horizontal_offset, int) or horizontal_offset < 0:
            logger.warning(f"{indent1}horizontal_offset: 'horizontal_offset' invalid value: {horizontal_offset}. Defaulting to 0.")
        else:
            logger.info(f"{indent1}horizontal_offset: {horizontal_offset}")

        vertical_offset = overlay_settings.get('vertical_offset')
        if vertical_offset is None:
            logger.warning(f"{indent1}vertical_offset: 'vertical_offset' is missing. Defaulting to 38.")
        elif not isinstance(vertical_offset, int) or vertical_offset < 0:
            logger.warning(f"{indent1}vertical_offset: 'vertical_offset' invalid value: {vertical_offset}. Defaulting to 38.")
        else:
            logger.info(f"{indent1}vertical_offset: {vertical_offset}")

        back_width = overlay_settings.get('back_width')
        if back_width is None:
            logger.warning(f"{indent1}back_width: 'back_width' is missing. Defaulting to 475.")
        elif not isinstance(back_width, int) or back_width < 0:
            logger.warning(f"{indent1}back_width: 'back_width' invalid value: {back_width}. Defaulting to 475.")
        else:
            logger.info(f"{indent1}back_width: {back_width}")

        back_height = overlay_settings.get('back_height')
        if back_height is None:
            logger.warning(f"{indent1}back_height: 'back_height' is missing. Defaulting to 55.")
        elif not isinstance(back_height, int) or back_height < 0:
            logger.warning(f"{indent1}back_height: 'back_height' invalid value: {back_height}. Defaulting to 55.")
        else:
            logger.info(f"{indent1}back_height: {back_height}")

        back_radius = overlay_settings.get('back_radius')
        if back_radius is None:
            logger.warning(f"{indent1}back_radius: 'back_radius' is missing. Defaulting to 30.")
        elif not isinstance(back_radius, int) or back_radius < 0:
            logger.warning(f"{indent1}back_radius: 'back_radius' invalid value: {back_radius}. Defaulting to 30.")
        else:
            logger.info(f"{indent1}back_radius: {back_radius}")

        ignore_blank_results = overlay_settings.get('ignore_blank_results')
        if ignore_blank_results is None:
            logger.warning(f"{indent1}ignore_blank_results: 'ignore_blank_results' is missing or blank.  Defaulting to 'true'.")
        elif ignore_blank_results not in ['true', 'false']:
            logger.warning(f"{indent1}ignore_blank_results: Invalid 'ignore_blank_results' value: {ignore_blank_results}. Must be true or false. Defaulting to 'true'.")
        else:
            logger.info(f"{indent1}ignore_blank_results: {ignore_blank_results}")

        with_status = overlay_settings.get('with_status')
        valid_status = {0, 1, 2, 3, 4, 5}
        if with_status is None:
            logger.warning(f"{indent1}with_status: 'with_status' is missing or blank. Defaulting to 0.")
        elif with_status not in valid_status:
            logger.warning(f"{indent1}with_status: Invalid 'with_status' value: {with_status}. Must be 0, 1, 2, 3, 4, or 5. Defaulting to 0")
        else:
            logger.info(f"{indent1}with_status: {with_status}")

        watch_region = overlay_settings.get('watch_region')
        valid_region_length = 2
        if watch_region is None:
            logger.warning(f"{indent1}watch_region: 'watch_region' is missing.  Defaulting to 'US'.")
        elif not isinstance(watch_region, str) or len(watch_region) != valid_region_length or not watch_region.isupper():
            logger.warning(f"{indent1}watch_region: 'Invalid 'watch_region' value: {watch_region}. Must be 2-character uppercase string.  Defaulting to 'US'.")
        else:
            logger.info(f"{indent1}watch_region: {watch_region}")

        with_original_language = overlay_settings.get('with_original_language')
        valid_language_length = 2
        if with_original_language is None:
            logger.warning(f"{indent1}with_original_language: 'with_original_language' is missing.  Defaulting to 'en'.")
        elif not isinstance(with_original_language, str) or len(with_original_language) != valid_language_length or not with_original_language.islower():
            logger.warning(f"{indent1}with_original_language: 'Invalid 'with_original_language' value: {with_original_language}. Must be 2-character lowercase string.  Defaulting to 'en'.")
        else:
            logger.info(f"{indent1}with_original_language: {with_original_language}")

        with_watch_monetization_types = overlay_settings.get('with_watch_monetization_types')
        allowed_types = {"flatrate", "free", "ads", "rent", "buy"}  # Allowed monetization types
        separators = {"|", ","}  # Allowed separators

        if with_watch_monetization_types is None:
            logger.warning(f"{indent1}with_watch_monetization_types: 'with_watch_monetization_types' is missing. Defaulting to 'flatrate|free|ads|rent|buy'.")
        else:
            # Validate the string format
            try:
                # Determine the separator dynamically
                separator = next((sep for sep in separators if sep in with_watch_monetization_types), None)

                if separator:
                    types = with_watch_monetization_types.split(separator)
                else:
                    types = [with_watch_monetization_types]  # Single value case

                # Check if all types are valid
                invalid_types = [t for t in types if t not in allowed_types]
                if invalid_types:
                    logger.warning(f"{indent1}with_watch_monetization_types: Invalid 'with_watch_monetization_types' values: {invalid_types}. Defaulting to 'flaterate|free|ads|rent|buy'.")
                elif len(types) > 5:
                    logger.warning(f"{indent1}with_watch_monetization_types: Too many 'with_watch_monetization_types' specified: {types}. Defaulting to 'flaterate|free|ads|rent|buy'.")
                else:
                    logger.info(f"{indent1}with_watch_monetization_types: {with_watch_monetization_types}")

            except Exception as e:
                logger.warning(f"{indent1}with_watch_monetization_types: Error validating 'with_watch_monetization_types': {e}. Defaulting to 'flaterate|free|ads|rent|buy'.")

#############################
# Library/Optional Settings #
#############################

# Validation of each optional overlay section. - Will stop script if top level is missing. Items and settings errors force default values.
        # Iterate through each overlay in the 'use_overlays' section
        logger.info("")
        logger.info("use_overlays:")
        for overlay_name, optional_settings in use_overlays.items():
            logger.info(f"{indent1}{overlay_name}:")
            if not optional_settings:
                logger.error(f"No settings found for overlay: {overlay_name}")
                logger.error("Exiting script...")
                logger.error(f"Please add [use:, back_color:, text:, and font_color:] to {overlay_name}")
                return False  # Indicate failure
            
            # Validate 'use' field (True or False)
            use_value = optional_settings.get("use", None)
            if use_value is None:
                logger.info(f"{indent2}use: 'use' is missing. Defaulting to 'True'")
            elif not isinstance(use_value, bool):
                logger.warning(f"{indent2}use: Invalid 'use' value in '{overlay_name}': {use_value}. It must be True or False.")
            else:
                logger.info(f"{indent2}use: {use_value}")

            # Validate 'back_color' (should be a valid color code)
            back_color = optional_settings.get("back_color")
            pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
            if back_color is None:
                logger.warning(f"{indent2}back_color: 'back_color' is missing. kometa requires #RGB, #RGBA, #RRGGBB or #RRGGBBAA. Defaulting to '#FFFFFF'.")
            elif not re.match(pattern, font_color):
                logger.warning(f"{indent2}back_color: Invalid 'back_color' value: {font_color}.  Defaulting to #FFFFFF.")
            else:
                logger.info(f"{indent2}back_color: {back_color}")

            # Validate 'text' field
            text_value = optional_settings.get("text", "")
            if not isinstance(text_value, str):
                logger.warning(f"{indent2}text: Invalid 'text' value in '{overlay_name}': {text_value}. It must be a string Defaulting to overlay name.")
            else:
                logger.info(f"{indent2}text: {text_value}")

            # Validate 'font_color' (should be a valid color code)
            font_color = optional_settings.get("font_color")
            if not isinstance(font_color, str) or not font_color.startswith("#") or len(font_color) not in {4, 7, 9}:
                logger.warning(f"{indent2}font_color: Invalid 'font_color' value in '{overlay_name}': {font_color}. It must be in #RGB, #RGBA, #RRGGBB, or #RRGGBBAA format. Defaulting to '#FFFFFF'")
            else:
                logger.info(f"{indent2}font_color: {font_color}")
                logger.info("")


######################################
# Returning Soon Collection Settings #
######################################
        # Validate individual settings within 'returning_soon_collection'
        logger.info("returning_soon_collection:")

        # Validate 'use' field
        use_value = collection_settings.get("use", None)
        if use_value is None:
            logger.info(f"{indent1}use: 'use' is missing. Defaulting to 'True'")
        elif not isinstance(use_value, bool):
            logger.warning(f"{indent1}use: Invalid 'use' value in 'returning_soon_collection: {use_value}'. It must be True or False.")
        else:
            logger.info(f"{indent1}use: {use_value}")

        # Validate 'collection_save_folder'
        collection_save_folder = collection_settings.get('collection_save_folder', None)
        if collection_save_folder is None:
            logger.warning(f"{indent1}collection_save_folder: 'collection_save_folder' not provided. Defaulting to '{main_directory}.")
        else:
            logger.info(f"{indent1}collection_save_folder: {collection_save_folder}")

        # Validate 'poster_soruce'
        poster_source = collection_settings.get('poster_source')
        if poster_source is None:
            logger.warning(f"{indent1}poster_source: 'poster_source' is missing or blank.  Defaulting to 'url'.")
        elif poster_source not in ['url', 'file']:
            logger.warning(f"{indent1}poster_source: Invalid 'poster_source' value: {poster_source}. Must be 'file', or 'url'. Defaulting to 'url'.")
        else:
            logger.info(f"{indent1}poster_source: {poster_source}")

        # Validate 'poster_path'
        poster_path = collection_settings.get('poster_path', None)
        if poster_path is None:
            logger.warning(f"{indent1}poster_path:'poster_path' not provided. Defaulting to 'https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/chart/Returning%20Soon.jpg'.")
        else:
            logger.info(f"{indent1}poster_path: {poster_path}")

        # Validate 'visible_home'
        visible_home = collection_settings.get('visible_home')
        if visible_home is None:
            logger.warning(f"{indent1}visible_home: 'visiible_home' is missing or blank.  Defaulting to 'true'.")
        elif visible_home not in ['true', 'false']:
            logger.warning(f"{indent1}visible_home: Invalid 'visible_home' value: {visible_home}. Must be true or false. Defaulting to 'true'.")
        else:
            logger.info(f"{indent1}visible_home: {visible_home}")

        # Validate 'visible_shared'
        visible_shared = collection_settings.get('visible_shared')
        if visible_shared is None:
            logger.warning(f"{indent1}visible_shared: 'visiible_shared' is missing or blank.  Defaulting to 'true'.")
        elif visible_shared not in ['true', 'false']:
            logger.warning(f"{indent1}visible_shared: Invalid 'visible_shared' value: {visible_shared}. Must be true or false. Defaulting to 'true'.")
        else:
            logger.info(f"{indent1}visible_shared: {visible_shared}")

        # Validate 'summary'
        summary = collection_settings.get('summary')
        if summary is None:
            logger.warning(f"{indent1}summary: 'summary' not provided. Defaulting to 'TV Shows returning soon!.'")
        else:
        # Add quotes around the summary if not already present
            if not (summary.startswith('"') and summary.endswith('"')):
                summary = f'"{summary}"'
            logger.info(f"{indent1}summary: {summary}")

        # Validate 'minimum_items'
        minimum_items = collection_settings.get('minimum_items')
        if minimum_items is None:
            logger.warning(f"{indent1}minimum_items: 'minimum_items is missing. Defaulting to 1.")
        elif not isinstance(minimum_items, int) or minimum_items <= 0:
            logger.warning(f"{indent1}minimum_items: 'minimum_items' invalid value: {minimum_items}. Defaulting to 1.")
        else:
            logger.info(f"{indent1}minimum_items: {minimum_items}")

        # Validate 'visible_home'
        delete_below_minimum = collection_settings.get('delete_below_minimum')
        if delete_below_minimum is None:
            logger.warning(f"{indent1}delete_below_minimum: 'delete_below_minimum' is missing or blank.  Defaulting to 'true'.")
        elif delete_below_minimum not in ['true', 'false']:
            logger.warning(f"{indent1}delete_below_minimum: Invalid 'delete_below_minimum' value: {delete_below_minimum}. Must be true or false. Defaulting to 'true'.")
        else:
            logger.info(f"{indent1}delete_below_minimum: {delete_below_minimum}")

        sort_title = collection_settings.get('sort_title')
        if sort_title is None:
            logger.warning(f"{indent1}sort_title: 'sort_title' not provided. Defaulting to '!010_Returning.'")
        else:
        # Add quotes around the summary if not already present
            if not (sort_title.startswith('"') and sort_title.endswith('"')):
                sort_title= f'"{sort_title}"'
            logger.info(f"{indent1}sort_title: {sort_title}")

        return True # Validation Succes.  Returns to main.py
        
    except Exception as e:
        logger.error(f"An error occurred during settings validation: {e}")
        return False  # Indicate failure
