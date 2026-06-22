import os
import re
import logging
from ruamel.yaml import YAML
from scripts.settings import load_settings

yaml = YAML()

logger = logging.getLogger(__name__)
settings_filename = "settings.yml"

indentlog = "   " # indent for 3 spaces in log
indentlog2 = "      " # indent for 6 spaces in log
indentlog3 = "          " #indent for 9 spaces in log

############################
# Validate Settings File   #
############################

def validate_settings(config_directory):
    settings_file_path = os.path.join(config_directory, settings_filename)

    if not os.path.exists(settings_file_path):
        logger.error(f"{indentlog}Settings file not found at '{settings_file_path}.")
        return False

    try:
        settings = load_settings(config_directory)
        if not isinstance(settings, dict):
            logger.error(f"{indentlog}Settings file format is invalid. Expected a dictionary.")
            return False

        required_sections = ['libraries', 'status_overlay', 'returning_soon_collection', 'movie_new_release', 'in_history_collection', 'streaming_overlay', 'top_10']
        for section in required_sections:
            if section not in settings or not isinstance(settings[section], dict) or not settings[section]:
                logger.error(f"{indentlog}The settings file does not contain a valid '{section}' section or it is empty.")
                return False

        if not validate_libraries(settings['libraries']):
            return False
        if not validate_status_overlay(settings['status_overlay'], config_directory):
            return False
        if not validate_movie_new_release(settings['movie_new_release'], config_directory):
            return False
        if not validate_returning_soon_collection(settings['returning_soon_collection'], config_directory):
            return False
        if not validate_in_history_collection(settings['in_history_collection'], config_directory):
            return False
        if not validate_streaming_overlay(settings['streaming_overlay'], config_directory):
            return False
        if not validate_top_10(settings['top_10'], config_directory):
            return False

        return True

    except Exception as e:
        logger.error(f"An error occurred during settings validation: {e}")
        return False

def validate_libraries(libraries):
    logger.info(f"{indentlog}libraries:")
    for library_name, library_settings in libraries.items():
        logger.info(f"{indentlog2}{library_name}:")
        if not library_settings:
            logger.error(f"{indentlog2}{library_name}: No settings found for library: {library_name}")
            return False
        validate_choice_setting(library_settings, 'library_type', ['show', 'movie'], 'movie')
        validate_boolean_setting(library_settings, 'is_anime', False)
        validate_boolean_setting(library_settings, 'use_watch_region', True)

    return True

def validate_status_overlay(status_overlay, config_directory):
    logger.info("")
    logger.info(f"{indentlog}status_overlay_settings:")

    if 'overlay_settings' in status_overlay:
        overlay_settings = status_overlay['overlay_settings']
        logger.info(f"{indentlog2}overlay_settings:")
        validate_integer_setting(overlay_settings, 'days_ahead', 30, 1, 30)
        validate_path_setting(overlay_settings, 'overlay_save_folder', config_directory, True)
        validate_date_format_setting(overlay_settings, 'date_format', "%m/%d")
        validate_choice_setting(overlay_settings, 'date_delimiter', ['/', '.', '-', '_'], '/')
        validate_boolean_setting(overlay_settings, 'remove_leading_zero', False)
        validate_path_setting(overlay_settings, 'font', f"{config_directory}/fonts/Inter-Medium.ttf", True)
        validate_integer_setting(overlay_settings, 'font_size', 45, 1, None)
        validate_color_setting(overlay_settings, 'font_color', '#FFFFFF')
        validate_choice_setting(overlay_settings, 'horizontal_align', ['center', 'left', 'right'], 'center')
        validate_choice_setting(overlay_settings, 'vertical_align', ['top', 'center', 'bottom'], 'top')
        validate_integer_setting(overlay_settings, 'horizontal_offset', 0, 0, None)
        validate_integer_setting(overlay_settings, 'vertical_offset', 38, 0, None)
        validate_boolean_setting(overlay_settings, 'use_backdrop', True)
        validate_integer_setting(overlay_settings, 'back_width', 475, 0, None)
        validate_integer_setting(overlay_settings, 'back_height', 55, 0, None)
        validate_integer_setting(overlay_settings, 'back_radius', 30, 0, None)
        validate_choice_setting(overlay_settings, 'ignore_blank_results', ['true', 'false', True, False], 'true')
        validate_integer_setting(overlay_settings, 'with_status', 0, 0, 5)
        validate_string_length_setting(overlay_settings, 'watch_region', 2, 'US')
        validate_string_length_setting(overlay_settings, 'with_original_language', 2, 'en')
        validate_monetization_types(overlay_settings, 'with_watch_monetization_types', 'flatrate|free|ads|rent|buy')
    else:
        logger.error(f"{indentlog2}Missing 'overlay_settings' section in 'status_overlay_settings'.")
        return False

    if 'use_overlays' in status_overlay:
        use_overlays = status_overlay['use_overlays']
        logger.info(f"{indentlog2}use_overlays:")
        for overlay_name, optional_settings in use_overlays.items():
            logger.info(f"{indentlog3}{overlay_name}:")
            if not optional_settings:
                logger.error(f"{indentlog3}No settings found for overlay: {overlay_name}")
                return False

            validate_boolean_setting(optional_settings, 'use', True)
            validate_color_setting(optional_settings, 'back_color', '#FFFFFF')
            validate_string_setting(optional_settings, 'text', 'default_text')
            validate_color_setting(optional_settings, 'font_color', '#FFFFFF')
            if 'back_width' in optional_settings:
                validate_integer_setting(optional_settings, 'back_width', 475, 0, None)
            if 'back_height' in optional_settings:
                validate_integer_setting(optional_settings, 'back_height', 55, 0, None)
            if 'back_radius' in optional_settings:
                validate_integer_setting(optional_settings, 'back_radius', 30, 0, None)
            if 'backdrop_image' in optional_settings:
                validate_path_setting(optional_settings, 'backdrop_image', '', True)
            if 'bd_horizontal_align' in optional_settings:
                validate_choice_setting(optional_settings, 'bd_horizontal_align', ['center', 'left', 'right'], 'center')
            if 'bd_vertical_align' in optional_settings:
                validate_choice_setting(optional_settings, 'bd_vertical_align', ['top', 'center', 'bottom'], 'top')
            if 'bd_horizontal_offset' in optional_settings:
                validate_integer_setting(optional_settings, 'bd_horizontal_offset', 0, 0, None)
            if 'bd_vertical_offset' in optional_settings:
                validate_integer_setting(optional_settings, 'bd_vertical_offset', 38, 0, None)
            if 'text_horizontal_align' in optional_settings:
                validate_choice_setting(optional_settings, 'text_horizontal_align', ['center', 'left', 'right'], 'center')
            if 'text_vertical_align' in optional_settings:
                validate_choice_setting(optional_settings, 'text_vertical_align', ['top', 'center', 'bottom'], 'top')
            if 'text_horizontal_offset' in optional_settings:
                validate_integer_setting(optional_settings, 'text_horizontal_offset', 0, 0, None)
            if 'text_vertical_offset' in optional_settings:
                validate_integer_setting(optional_settings, 'text_vertical_offset', 38, 0, None)
    else:
        logger.error(f"{indentlog2}Missing 'use_overlays' section in 'status_overlay_settings'.")
        return False

    return True

def validate_movie_new_release(movie_new_release_settings, config_directory):
    logger.info("")
    logger.info(f"{indentlog}movie_new_release:")

    validate_boolean_setting(movie_new_release_settings, 'use', True)
    validate_path_setting(movie_new_release_settings, 'new_movie_save_folder', config_directory, True)
    validate_integer_setting(movie_new_release_settings, 'days_to_consider_new', 90, 1, 90)
    validate_boolean_setting(movie_new_release_settings, 'use_backdrop', True)
    validate_color_setting(movie_new_release_settings, 'back_color', '#008001')
    validate_string_setting(movie_new_release_settings, 'text', 'default_text')
    validate_color_setting(movie_new_release_settings, 'font_color', '#FFFFFF')
    if 'back_width' in movie_new_release_settings:
        validate_integer_setting(movie_new_release_settings, 'back_width', 475, 0, None)
    if 'back_height' in movie_new_release_settings:
        validate_integer_setting(movie_new_release_settings, 'back_height', 55, 0, None)
    if 'back_radius' in movie_new_release_settings:
        validate_integer_setting(movie_new_release_settings, 'back_radius', 30, 0, None)
    if 'backdrop_image' in movie_new_release_settings:
        validate_path_setting(movie_new_release_settings, 'backdrop_image', '', True)
    if 'bd_horizontal_align' in movie_new_release_settings:
        validate_choice_setting(movie_new_release_settings, 'bd_horizontal_align', ['center', 'left', 'right'], 'center')
    if 'bd_vertical_align' in movie_new_release_settings:
        validate_choice_setting(movie_new_release_settings, 'bd_vertical_align', ['top', 'center', 'bottom'], 'top')
    if 'bd_horizontal_offset' in movie_new_release_settings:
        validate_integer_setting(movie_new_release_settings, 'bd_horizontal_offset', 0, 0, None)
    if 'bd_vertical_offset' in movie_new_release_settings:
        validate_integer_setting(movie_new_release_settings, 'bd_vertical_offset', 38, 0, None)
    if 'text_horizontal_align' in movie_new_release_settings:
        validate_choice_setting(movie_new_release_settings, 'text_horizontal_align', ['center', 'left', 'right'], 'center')
    if 'text_vertical_align' in movie_new_release_settings:
        validate_choice_setting(movie_new_release_settings, 'text_vertical_align', ['top', 'center', 'bottom'], 'top')
    if 'text_horizontal_offset' in movie_new_release_settings:
        validate_integer_setting(movie_new_release_settings, 'text_horizontal_offset', 0, 0, None)
    if 'text_vertical_offset' in movie_new_release_settings:
        validate_integer_setting(movie_new_release_settings, 'text_vertical_offset', 38, 0, None)

    return True

def validate_returning_soon_collection(collection_settings, config_directory):
    logger.info("")
    logger.info(f"{indentlog}returning_soon_collection:")

    validate_boolean_setting(collection_settings, 'use', True)
    validate_path_setting(collection_settings, 'collection_save_folder', config_directory, True)
    validate_integer_setting(collection_settings, 'collection_days_ahead', 30, 1, None)
    validate_integer_setting(collection_settings, 'days_last_aired', 45, 1, None)
    validate_boolean_setting(collection_settings, 'use_poster', False)
    validate_choice_setting(collection_settings, 'poster_source', ['url', 'file'], 'url')
    validate_path_setting(collection_settings, 'poster_path', f"{config_directory}/posters/Kometa Returning Soon.jpg", True)
    validate_choice_setting(collection_settings, 'visible_home', ['true', 'false', True, False], 'true')
    validate_choice_setting(collection_settings, 'visible_library', ['true', 'false', True, False], 'true')
    validate_choice_setting(collection_settings, 'visible_shared', ['true', 'false', True, False], 'true')
    validate_string_setting(collection_settings, 'summary', 'Shows returning soon!', True)
    validate_integer_setting(collection_settings, 'minimum_items', 1, 1, None)
    validate_choice_setting(collection_settings, 'delete_below_minimum', ['true', 'false', True, False], 'true')
    validate_string_setting(collection_settings, 'sort_title', '!010_Returning', True)

    return True

def validate_in_history_collection(in_history_settings, config_directory):
    logger.info("")
    logger.info(f"{indentlog}in_history_collection:")

    validate_boolean_setting(in_history_settings, 'use', True)
    validate_path_setting(in_history_settings, 'in_history_save_folder', config_directory, True)
    validate_choice_setting(in_history_settings, 'in_history_range', ['days', 'weeks', 'months'], 'weeks')
    validate_integer_setting(in_history_settings, 'starting_year', 1980, 1000, None)
    validate_integer_setting(in_history_settings, 'ending_year', 2024, 1000, None)
    validate_boolean_setting(in_history_settings, 'use_poster', False)
    validate_choice_setting(in_history_settings, 'poster_source', ['url', 'file'], 'url')
    validate_path_setting(in_history_settings, 'poster_path', f"{config_directory}/posters/in-history.jpg", True)
    validate_choice_setting(in_history_settings, 'visible_home', ['true', 'false', True, False], 'false')
    validate_choice_setting(in_history_settings, 'visible_library', ['true', 'false', True, False], 'true')
    validate_choice_setting(in_history_settings, 'visible_shared', ['true', 'false', True, False], 'false')
    validate_integer_setting(in_history_settings, 'minimum_items', 1, 1, None)
    validate_choice_setting(in_history_settings, 'delete_below_minimum', ['true', 'false', True, False], 'true')
    validate_string_setting(in_history_settings, 'sort_title', '!012_In_History', True)

    return True

def validate_streaming_overlay(streaming_overlay, config_directory):
    logger.info("")
    logger.info(f"{indentlog}streaming_overlay:")

    gradient = streaming_overlay.get("logo_with_gradient", False)
    black = streaming_overlay.get("logo_with_black_backing", False)
    if gradient and black:
        logger.error(f"{indentlog2}Both 'logo_with_gradient' and 'logo_with_black_backing' are set to True. Only one can be True at a time.")
        return False
    
    validate_boolean_setting(streaming_overlay, 'use', True)
    validate_path_setting(streaming_overlay, 'streaming_save_folder', config_directory, True)
    validate_path_setting(streaming_overlay, 'streaming_image_folder', config_directory, True)
    validate_choice_setting(streaming_overlay, 'streaming_image_size', ['default', 'small'], 'default')
    validate_boolean_setting(streaming_overlay, 'logo_with_gradient', False)
    validate_boolean_setting(streaming_overlay, 'logo_with_black_backing', False)
    validate_choice_setting(streaming_overlay, 'vertical_align', ['top', 'center', 'bottom'], 'top')
    validate_choice_setting(streaming_overlay, 'horizontal_align', ['left', 'center', 'right'], 'left')
    validate_integer_setting(streaming_overlay, 'vertical_offset', 35, 0, None)
    validate_integer_setting(streaming_overlay, 'horizontal_offset', 30, 0, None)
    validate_boolean_setting(streaming_overlay, 'use_backdrop', True)
    validate_integer_setting(streaming_overlay, 'back_width', 215, 0, None)
    validate_integer_setting(streaming_overlay, 'back_height', 70, 0, None)
    validate_integer_setting(streaming_overlay, 'back_radius', 10, 0, None)
    validate_color_setting(streaming_overlay, 'back_color', '#000000B3')
    validate_choice_setting(streaming_overlay, 'ignore_blank_results', ['true', 'false', True, False], 'true')
    validate_string_length_setting(streaming_overlay, 'watch_region', 2, 'US')
    validate_string_length_setting(streaming_overlay, 'with_original_language', 2, 'en')
    validate_monetization_types(streaming_overlay, 'with_watch_monetization_types', 'flatrate|free|ads|rent|buy')
    validate_boolean_setting(streaming_overlay, 'use_vote_count', True)
    validate_integer_setting(streaming_overlay, 'vote_count', 2, 1, None)
    validate_boolean_setting(streaming_overlay, 'use_extra_streaming', True)

    if 'streaming_services' in streaming_overlay:
        logger.info(f"{indentlog2}streaming_services:")
        streaming_services = streaming_overlay['streaming_services']
        validate_streaming_services(streaming_services, 'default_streaming', 'DEFAULT OVERLAYS')
        validate_streaming_services(streaming_services, 'extra_streaming', 'EXTRA OVERLAYS')
    else:
        logger.error(f"{indentlog2}Missing 'streaming_services' section in 'streaming_overlay'.")
        return False

    return True

def validate_streaming_services(streaming_services, key, overlay_type):
    logger.info(f"{indentlog3}{key}:")
    logger.info(f"{indentlog3}# {overlay_type}")

    if key in streaming_services:
        services = streaming_services[key]
        for service_name, service_settings in services.items():
            logger.info(f"{indentlog3}{service_name}: {service_settings}")
            validate_boolean_setting(service_settings, 'use', True, log=False)
            validate_integer_setting(service_settings, 'limit', 1500, 1, None, log=False)
            validate_integer_setting(service_settings, 'weight', 180, 1, None, log=False)
    else:
        logger.error(f"{indentlog3}Missing '{key}' section in 'streaming_services'.")
        return False

    return True

def validate_top_10(top_10_settings, config_directory):
    logger.info("")
    logger.info(f"{indentlog}top_10:")

    if 'top_10_overlay' in top_10_settings:
        logger.info(f"{indentlog2}top_10_overlay:")
        overlay_settings = top_10_settings['top_10_overlay']
        validate_boolean_setting(overlay_settings, 'use', True)
        validate_path_setting(overlay_settings, 'overlay_save_folder', config_directory, True)
        validate_choice_setting(overlay_settings, 'vertical_align', ['top', 'center', 'bottom'], 'top')
        validate_choice_setting(overlay_settings, 'horizontal_align', ['left', 'center', 'right'], 'left')
        validate_integer_setting(overlay_settings, 'vertical_offset', 105, 0, None)
        validate_integer_setting(overlay_settings, 'horizontal_offset', 30, 0, None)
        validate_path_setting(overlay_settings, 'font', config_directory, True)
        validate_integer_setting(overlay_settings, 'font_size', 45, 1, None)
        validate_color_setting(overlay_settings, 'font_color', '#80FF40')
        validate_boolean_setting(overlay_settings, 'use_backdrop', True)
        validate_integer_setting(overlay_settings, 'back_width', 215, 0, None)
        validate_integer_setting(overlay_settings, 'back_height', 70, 0, None)
        validate_integer_setting(overlay_settings, 'back_radius', 10, 0, None)
        validate_color_setting(overlay_settings, 'back_color', '#000000B3')
    else:
        logger.error(f"{indentlog2}Missing 'top_10_overlay' section in 'top_10' settings.")
        return False

    if 'top_10_collection' in top_10_settings:
        logger.info(f"{indentlog2}top_10_collection:")
        collection_settings = top_10_settings['top_10_collection']
        validate_boolean_setting(collection_settings, 'use', True)
        validate_path_setting(collection_settings, 'collection_save_folder', config_directory, True)
        validate_choice_setting(collection_settings, 'visible_home', ['true', 'false', True, False], 'false')
        validate_choice_setting(collection_settings, 'visible_library', ['true', 'false', True, False], 'true')
        validate_choice_setting(collection_settings, 'visible_shared', ['true', 'false', True, False], 'false')
        validate_integer_setting(collection_settings, 'minimum_items', 1, 1, None)
        validate_choice_setting(collection_settings, 'delete_below_minimum', ['true', 'false', True, False], 'true')
        validate_string_setting(collection_settings, 'sort_title_prefix', '!020', True)
    else:
        logger.error(f"{indentlog2}Missing 'top_10_collection' section in 'top_10' settings.")
        return False

    return True

def validate_path_setting(settings, key, default, allow_blank=False, log=True):
    value = settings.get(key, default)
    if (value is None or (not allow_blank and isinstance(value, str) and value.strip() == "") or value in ["path/to/folder", "path/to/kometa-poster", "path/to/kometa-font"]):
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}' setting or path not set. Defaulting to '{default}'.")
    else:
        if log:
            logger.info(f"{indentlog3}{key}: {value}")

def validate_boolean_setting(settings, key, default, log=True):
    value = settings.get(key, None)
    if value is None:
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}' setting. Defaulting to {default}.")
    elif not isinstance(value, bool):
        if log:
            logger.warning(f"{indentlog3}{key}: '{key}' setting is not a valid True or False. Defaulting to '{default}'.")
    else:
        if log:
            logger.info(f"{indentlog3}{key}: {value}")

def validate_integer_setting(settings, key, default, min_value, max_value, log=True):
    value = settings.get(key)
    if value is None:
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}' value. Defaulting to {default}.")
    elif not isinstance(value, int) or (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
        if log:
            logger.warning(f"{indentlog3}{key}: Invalid '{key}' value: {value}. Must be number between {min_value} and {max_value}. Defaulting to '{default}'.")
    else:
        if log:
            logger.info(f"{indentlog3}{key}: {value}")

def validate_string_setting(settings, key, default, allow_blank=False, log=True):
    value = settings.get(key, default)
    if value is None or (not allow_blank and not value.strip()):
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    else:
        if not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'
        if log:
            logger.info(f"{indentlog3}{key}: {value}")

def validate_string_length_setting(settings, key, length, default, log=True):
    value = settings.get(key, None)
    if value is None:
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}'. Defaulting to '{default}'.")
    elif not isinstance(value, str) or len(value) != length:
        if log:
            logger.warning(f"{indentlog3}{key}: Invalid '{key}' value: {value}. Must be a {length}-character string. Defaulting to '{default}'.")
    else:
        if log:
            logger.info(f"{indentlog3}{key}: {value}")

def validate_color_setting(settings, key, default, log=True):
    pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
    value = settings.get(key, None)
    if value is None:
        if not (default.startswith('"') and default.endswith('"')):
            default = f'"{default}"'
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    elif not re.match(pattern, value):
        if not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'
        if log:
            logger.warning(f"{indentlog3}{key}: Invalid '{key}' value: {value}. Must be a valid color code. Defaulting to '{default}'.")
    else:
        if log:
            logger.info(f"{indentlog3}{key}: {value}")

def validate_choice_setting(settings, key, choices, default, log=True):
    value = settings.get(key, None)
    if value is None:
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    elif value not in choices:
        if log:
            logger.warning(f"{indentlog3}{key}: Invalid '{key}' value: {value}. Must be one of {choices}. Defaulting to '{default}'.")
    else:
        if log:
            logger.info(f"{indentlog3}{key}: {value}")

def validate_date_format_setting(settings, key, default, log=True):
    value = settings.get(key, None)
    if value in [1, 2, "1", "2"]:
        if log:
            logger.info(f"{indentlog3}{key}: {value}")
    elif isinstance(value, str) and value.strip():
        if log:
            logger.info(f"{indentlog3}{key}: {value} (custom format)")
    else:
        if log:
            logger.warning(f"{indentlog3}{key}: Invalid '{key}' value: {value}. Defaulting to '{default}'.")
        settings[key] = default

def validate_monetization_types(settings, key, default, log=True):
    allowed_types = {"flatrate", "free", "ads", "rent", "buy"}
    separators = {"|", ","}
    value = settings.get(key, default)

    if value is None:
        if log:
            logger.warning(f"{indentlog3}{key}: Missing '{key}' value. Defaulting to '{default}'.")
    else:
        try:
            separator = next((sep for sep in separators if sep in value), None)
            types = value.split(separator) if separator else [value]
            invalid_types = [t for t in types if t not in allowed_types]
            if invalid_types:
                if log:
                    logger.warning(f"{indentlog3}{key}: Invalid '{key}' values: {invalid_types}. Defaulting to '{default}'.")
            else:
                if log:
                    logger.info(f"{indentlog3}{key}: {value}")
        except Exception as e:
            if log:
                logger.warning(f"{indentlog3}{key}: Error validating '{key}': {e}. Defaulting to '{default}'.")