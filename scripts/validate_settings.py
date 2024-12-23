import os
import re
import logging
from ruamel.yaml import YAML
from scripts.settings import load_settings

yaml = YAML()

# Get logger from the main.py logging configuration
logger = logging.getLogger(__name__)  # This ensures you use the same logger instance from main.py
settings_filename = "overlay-settings.yml"

indent1 = "  " # indent for 1st level sections
indent2 = "    " # indent for 2nd level sections

############################
# Validate Settings File   #
############################

def validate_settings(config_directory):
    settings_file_path = os.path.join(config_directory, settings_filename)

    if not os.path.exists(settings_file_path):
        logger.error(f"Settings file not found at '{settings_file_path}.")
        return False

    try:
        settings = load_settings(config_directory)
        if not isinstance(settings, dict):
            logger.error("Settings file format is invalid. Expected a dictionary.")
            return False

        # Validate top-level sections
        required_sections = ['libraries', 'overlay_settings', 'use_overlays', 'returning_soon_collection']
        for section in required_sections:
            if section not in settings or not isinstance(settings[section], dict) or not settings[section]:
                logger.error(f"The settings file does not contain a valid '{section}' section or it is empty.")
                return False

        # Validate individual sections
        if not validate_libraries(settings['libraries']):
            return False
        if not validate_overlay_settings(settings['overlay_settings'], config_directory):
            return False
        if not validate_use_overlays(settings['use_overlays']):
            return False
        if not validate_returning_soon_collection(settings['returning_soon_collection'], config_directory):
            return False

        return True

    except Exception as e:
        logger.error(f"An error occurred during settings validation: {e}")
        return False

def validate_libraries(libraries):
    logger.info("libraries:")
    for library_name, library_settings in libraries.items():
        logger.info(f"{indent1}{library_name}:")
        if not library_settings:
            logger.error(f"{indent1}{library_name}: No settings found for library: {library_name}")
            return False

        validate_boolean_setting(library_settings, 'is_anime', False)
        validate_boolean_setting(library_settings, 'use_watch_region', True)

    return True


def validate_overlay_settings(overlay_settings, config_directory):
    logger.info("")
    logger.info(f"overlay_settings:")
    validate_integer_setting(overlay_settings, 'days_ahead', 30, 1, 30)
    validate_string_setting(overlay_settings, 'overlay_save_folder', config_directory, True)
    validate_string_setting(overlay_settings, 'font', f"{config_directory}/fonts/Inter-Medium.ttf", True)
    validate_integer_setting(overlay_settings, 'font_size', 45, 1, None)
    validate_color_setting(overlay_settings, 'font_color', '#FFFFFF')
    validate_choice_setting(overlay_settings, 'horizontal_align', ['center', 'left', 'right'], 'center')
    validate_choice_setting(overlay_settings, 'vertical_align', ['top', 'center', 'bottom'], 'top')
    validate_integer_setting(overlay_settings, 'horizontal_offset', 0, 0, None)
    validate_integer_setting(overlay_settings, 'vertical_offset', 38, 0, None)
    validate_integer_setting(overlay_settings, 'back_width', 475, 0, None)
    validate_integer_setting(overlay_settings, 'back_height', 55, 0, None)
    validate_integer_setting(overlay_settings, 'back_radius', 30, 0, None)
    validate_choice_setting(overlay_settings, 'ignore_blank_results', ['true', 'false'], 'true')
    validate_integer_setting(overlay_settings, 'with_status', 0, 0, 5)
    validate_string_length_setting(overlay_settings, 'watch_region', 2, 'US')
    validate_string_length_setting(overlay_settings, 'with_original_language', 2, 'en')
    validate_monetization_types(overlay_settings, 'with_watch_monetization_types', 'flatrate|free|ads|rent|buy')
    logger.info("")

    return True

def validate_use_overlays(use_overlays):
    logger.info("")
    logger.info(f"use_overlays:")
    for overlay_name, optional_settings in use_overlays.items():
        logger.info(f"{indent1}{overlay_name}:")
        if not optional_settings:
            logger.error(f"No settings found for overlay: {overlay_name}")
            return False

        validate_boolean_setting(optional_settings, 'use', True)
        validate_color_setting(optional_settings, 'back_color', '#FFFFFF')
        validate_string_setting(optional_settings, 'text', 'default_text')
        validate_color_setting(optional_settings, 'font_color', '#FFFFFF')
        logger.info("")

    return True

def validate_returning_soon_collection(collection_settings, config_directory):
    logger.info("")
    logger.info(f"{indent1}returning_soon_collection:")

    validate_boolean_setting(collection_settings, 'use', True)
    validate_string_setting(collection_settings, 'collection_save_folder', config_directory, True)
    validate_choice_setting(collection_settings, 'poster_source', ['url', 'file'], 'url')
    validate_string_setting(collection_settings, 'poster_path', 'https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager-Images/master/chart/Returning%20Soon.jpg', True)
    validate_choice_setting(collection_settings, 'visible_home', ['true', 'false'], 'true')
    validate_choice_setting(collection_settings, 'visible_shared', ['true', 'false'], 'true')
    validate_string_setting(collection_settings, 'summary', 'Shows returning soon!', True)
    validate_integer_setting(collection_settings, 'minimum_items', 1, 1, None)
    validate_choice_setting(collection_settings, 'delete_below_minimum', ['true', 'false'], 'true')
    validate_string_setting(collection_settings, 'sort_title', '!010_Returning', True)
    logger.info("")

    return True

def validate_boolean_setting(settings, key, default):
    value = settings.get(key, None)
    if value is None:
        logger.warning(f"{indent2}{key}: Missing '{key}' setting. Defaulting to {default}.")
    elif not isinstance(value, bool):
        logger.warning(f"{indent2}{key}: '{key}' setting is not a valid True or False. Defaulting to {default}.")
    else:
        logger.info(f"{indent2}{key}: {value}")

def validate_integer_setting(settings, key, default, min_value, max_value):
    value = settings.get(key)
    if value is None:
        logger.warning(f"{indent2}{key}: Missing '{key}' value. Defaulting to {default}.")
    elif not isinstance(value, int) or (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
        logger.warning(f"{indent2}{key}: Invalid '{key}' value: {value}. Must be number between {min_value} and {max_value}. Defaulting to {default}.")
    else:
        logger.info(f"{indent2}{key}: {value}")

def validate_string_setting(settings, key, default, allow_blank=False):
    value = settings.get(key, default)
    if value is None or (not allow_blank and not value.strip()):
        logger.warning(f"{indent2}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    else:
        if not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'
        logger.info(f"{indent2}{key}: {value}")

def validate_string_length_setting(settings, key, length, default):
    value = settings.get(key, None)
    if value is None:
        logger.warning(f"{indent2}{key}: Missing '{key}'. Defaulting to '{default}'.")
    elif not isinstance(value, str) or len(value) != length:
        logger.warning(f"{indent2}{key}: Invalid '{key}' value: {value}. Must be a {length}-character string. Defaulting to '{default}'.")
    else:
        logger.info(f"{indent2}{key}: {value}")

def validate_color_setting(settings, key, default):
    pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
    value = settings.get(key, None)
    if value is None:
        if not (default.startswith('"') and default.endswith('"')):
            default = f'"{default}"'
        logger.warning(f"{indent2}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    elif not re.match(pattern, value):
        if not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'
        logger.warning(f"{indent2}{key}: Invalid '{key}' value: {value}. Must be a valid color code. Defaulting to '{default}'.")
    else:
        if not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'
        logger.info(f"{indent2}{key}: {value}")

def validate_choice_setting(settings, key, choices, default):
    value = settings.get(key, None)
    if value is None:
        logger.warning(f"{indent2}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    elif value not in choices:
        logger.warning(f"{indent2}{key}: Invalid '{key}' value: {value}. Must be one of {choices}. Defaulting to '{default}'.")
    else:
        logger.info(f"{indent2}{key}: {value}")

def validate_monetization_types(settings, key, default):
    allowed_types = {"flatrate", "free", "ads", "rent", "buy"}
    separators = {"|", ","}
    value = settings.get(key, default)

    if value is None:
        logger.warning(f"{indent2}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    else:
        try:
            separator = next((sep for sep in separators if sep in value), None)
            types = value.split(separator) if separator else [value]
            invalid_types = [t for t in types if t not in allowed_types]
            if invalid_types:
                logger.warning(f"{indent2}{key}: Invalid '{key}' values: {invalid_types}. Defaulting to '{default}'.")
            else:
                logger.info(f"{indent2}{key}: {value}")
        except Exception as e:
            logger.warning(f"{indent2}{key}: Error validating '{key}': {e}. Defaulting to '{default}'.")