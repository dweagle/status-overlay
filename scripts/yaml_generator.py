import os
import re
import logging
import platform
from scripts.settings import load_settings
from ruamel.yaml import YAML
from datetime import datetime, timedelta

yaml = YAML()

logger = logging.getLogger(__name__)

DEFAULTS = {
    'is_anime': False,
    'use_watch_region': True,
    'days_ahead': 30,
    'date_format': '1',
    'date_delimiter': '/',
    'remove_leading_zero': False,
    'font': "{config_directory}/fonts/Inter-Medium.ttf",
    'font_size': 45,
    'font_color': '"#FFFFFF"',
    'horizontal_align': 'center',
    'vertical_align': 'top',
    'horizontal_offset': 0,
    'vertical_offset': 38,
    'use_backdrop': True,
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
    'collection_days_ahead': 30,
    'days_last_aired': 45,
    'poster_source': 'file',
    'poster_path':  "{config_directory}/posters/Kometa Returning Soon.jpg",
    'visible_home': True,
    'visible_shared': True,
    "summary": 'Shows returning soon!',
    "minimum_items": 1,
    "delete_below_minimum": 'true',
    "sort_title": '!010_Returning',

    "in_history_use": True,
    "range": "weeks",
    "start_year": 1980,
    "IH_poster_soruce": 'file',
    "IH_poster_path": "{config_directory}/posters/in-history.jpg",
    "IH_visible_home": False,
    "IH_visible_shared": False,
    "IH_visible_library": True,
    "IH_sort_title": '!012_In_History',

    'new_movie_use': True,
    'days_new': 90,
    'new_movie_back_color': '#103197',
    'new_movie_text': 'N E W  R E L E A S E',

    'streaming_overlay_use': True,
    'streaming_image_folder': "{config_directory}/streaming-images",
    "streaming_image_size": "default",
    "logo_with_gradient": False,
    "logo_with_black_backing": False,
    'streaming_vertical_align': 'top',
    'streaming_horizontal_align': 'left',
    'streaming_vertical_offset': 30,
    'streaming_horizontal_offset': 30,
    'streaming_back_width': 215,
    'streaming_back_height': 70,
    'streaming_back_radius': 10,
    'streaming_back_color': '#000000B3',
    'streaming_ignore_blank_results': "true",
    'streaming_watch_region': 'US',
    'streaming_with_original_languge': 'en',
    'streaming_with_watch_monetization_types': 'flatrate|free|ads|rent|buy',
    'use_vote_count': True,
    'vote_count': 2,
    'use_extra_streaming': True,

    'top_overlay_use': True,
    'top_vertical_align': 'top',
    'top_horizontal_align': 'left',
    'top_vertical_offset': 105,
    'top_horizontal_offset': 30,
    'top_font_size': 45,
    'top_font_color': '80FF40',
    'top_back_width': 215,
    'top_back_height': 70,
    'top_back_radius': 10,
    'top_back_color': '#000000B3',

    'top_collection_use': True,
    'top_visible_home': False,
    'top_visible_library': True,
    'top_visible_shared': False,
    'top_minimum_items': 1,
    'top_delete_below_minimum': 'true',
    'top_sort_title': '!020'
}

timezone = os.getenv('TZ', DEFAULTS['timezone'])

def get_with_defaults(settings, primary_key, fallback_key=None, config_directory=''):
    def is_valid_color(value):
        pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
        return isinstance(value, str) and re.match(pattern, value)

    value = settings.get(primary_key)
    
    if value is None and fallback_key is not None:
        value = DEFAULTS.get(fallback_key)

    if primary_key == 'font_color' and not is_valid_color(value):
        value = DEFAULTS.get('font_color', '#FFFFFF')

    if value in ["path/to/kometa-poster", "path/to/kometa-font", "path/to/images"]:
        value = DEFAULTS.get(primary_key)

    if isinstance(value, str) and "{config_directory}" in value:
        value = value.replace("{config_directory}", config_directory)

    return value 

TEXT_OVERRIDE_KEYS = (
    'back_width', 'back_height', 'back_radius',
    'text_horizontal_align', 'text_vertical_align',
    'text_horizontal_offset', 'text_vertical_offset',
)
BD_OVERRIDE_KEYS = (
    'bd_horizontal_align', 'bd_vertical_align',
    'bd_horizontal_offset', 'bd_vertical_offset',
)

def any_status_uses_overrides(use_overlays, keys):
    return any(
        key in status_settings
        for status_settings in use_overlays.values()
        if isinstance(status_settings, dict)
        for key in keys
    )

def get_backdrop_overrides(per_status_settings):
    overrides = ""
    for key in ('back_width', 'back_height', 'back_radius'):
        if key in per_status_settings:
            overrides += f", {key}: {per_status_settings[key]}"
    return overrides

def get_align_offset_overrides(per_status_settings):
    overrides = ""
    mapping = {
        'bd_horizontal_align': 'horizontal_align',
        'bd_vertical_align': 'vertical_align',
        'bd_horizontal_offset': 'horizontal_offset',
        'bd_vertical_offset': 'vertical_offset',
    }
    for setting_key, template_key in mapping.items():
        if setting_key in per_status_settings:
            overrides += f", {template_key}: {per_status_settings[setting_key]}"
    return overrides

def get_text_align_offset_overrides(per_status_settings):
    overrides = ""
    mapping = {
        'text_horizontal_align': 'horizontal_align',
        'text_vertical_align': 'vertical_align',
        'text_horizontal_offset': 'horizontal_offset',
        'text_vertical_offset': 'vertical_offset',
    }
    for setting_key, template_key in mapping.items():
        if setting_key in per_status_settings:
            overrides += f", {template_key}: {per_status_settings[setting_key]}"
    return overrides

def get_backdrop_image(backdrop_image, library_name, entry_name, weight, template_type, extra_vars="", align_offset_vars=""):
    if not backdrop_image:
        return ""
    return f"""
# {entry_name.upper()} STATUS IMAGE
  {library_name} {entry_name} Image:
    variables: {{weight: {weight}, file: {backdrop_image}{extra_vars}{align_offset_vars}}}
    template: {{name: {library_name} {template_type}}}
"""

def write_yaml_file(config_directory, save_folder, name, file_name, content):
    if save_folder and isinstance(save_folder, str):
        save_folder = save_folder.strip()
        if save_folder == "path/to/folder":
            save_folder = ''
    else:
        save_folder = ''

    if save_folder:
        logger.info(f"{indentlog2}Using {name} save folder: {save_folder}")
    else:
        logger.debug(f"{indentlog2}No {name} save folder provided.  Using '{config_directory}' folder.")
        save_folder = config_directory

    if not os.path.exists(save_folder):
        logger.error(f"{indentlog}{name} save folder doesn't exist or permissions not set.  Exiting main script")
        logger.error(f"{indentlog}If using path outside of mounted container config volume, you need to mount a volume to this.")
        return

    output_file_path = os.path.join(save_folder, f"{file_name}")
    
    try:
        with open(output_file_path, 'w') as file:
            file.write(content)
        logger.info(f"{indentlog}Generated {name} at '{output_file_path}'")
        logger.info("")
    except Exception as e:
        logger.error(f"{indentlog}Error generating {name}: {e}")
        logger.info("")

#########################
# Create Status Overlay #
#########################

indentlog = "   " # indent for 3 spaces in log
indentlog2 = "      " # indent for 6 spaces in log
indentlog3 = "         " # indent for 9 spaces in log
indentlog4 = "            " # indent for 12 spacees in log
indent2 = "    "  # indent 2 tabs (4 spaces) for kometa yaml spacing
indent3 = "      " # indent 3 tabs (6 spaces) for kometa yaml spacing
indent4 = "        " # indent 4 tabs (8 spaces) for kometa yaml spacing

def create_status_yaml(config_directory):
    try:
        settings = load_settings(config_directory, log_message=False)

        current_date = datetime.now()

        date_21_days_prior = (current_date - timedelta(days=21)).strftime('%m/%d/%Y')

        date_15_days_prior = (current_date - timedelta(days=15)).strftime('%m/%d/%Y')

        air_date_today= (current_date).strftime('%m/%d/%Y')

        date_14_days_prior = (current_date - timedelta(days=14)).strftime('%m/%d/%Y')

        libraries = settings.get('libraries', {})

        overlay_settings = settings.get('status_overlay', {}).get('overlay_settings', {})

        use_overlays = settings.get('status_overlay', {}).get('use_overlays', {})

        date_delimiter = get_with_defaults(overlay_settings, 'date_delimiter', '/')
        
        remove_leading_zero = get_with_defaults(overlay_settings, 'remove_leading_zero', False)

        date_format = get_with_defaults(overlay_settings, 'date_format', 'date_format')
        if not date_format:
            date_format = "%m/%d"

        try:
            date_format_int = int(date_format)
            if remove_leading_zero:
                if platform.system() == "Windows":
                    month = "%#m"
                    day = "%#d"
                elif platform.system() in ["Linux", "Darwin"]:
                    month = "%-m"
                    day = "%-d"
                else:
                    month = "%m"
                    day = "%d"
            else:
                month = "%m"
                day = "%d"

            if date_format_int == 2:
                date_format = f"{day}{date_delimiter}{month}"
                date_format_with_year = f"{day}{date_delimiter}{month}{date_delimiter}%Y"
            else:
                date_format = f"{month}{date_delimiter}{day}"
                date_format_with_year = f"{month}{date_delimiter}{day}{date_delimiter}%Y"
        except Exception:

            date_format_with_year = date_format
            if "%Y" not in date_format:
                date_format_with_year = date_format + "/%Y"

        for library_name, library_settings in libraries.items():
            if library_settings.get('library_type') != 'show':
                continue
            is_anime = get_with_defaults(library_settings, 'is_anime', 'is_anime')

            use_watch_region = get_with_defaults(library_settings, 'use_watch_region', 'use_watch_region')

            logger.info(f"{indentlog}Creating main status template YAML for {library_name}.")

            status_string = f"""# {library_name} Template
templates:
  {library_name} Status TMDB Discover:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: <<weight>>
      name: text(<<text>>)
      font: "{get_with_defaults(overlay_settings, 'font', 'font', config_directory)}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: <<font_color>>
"""
            use_backdrop = get_with_defaults(overlay_settings, 'use_backdrop', 'use_backdrop')
            use_text_overrides = any_status_uses_overrides(use_overlays, TEXT_OVERRIDE_KEYS)

            if use_text_overrides:
                status_string += f"{indent3}horizontal_align: <<horizontal_align>>\n"
                status_string += f"{indent3}vertical_align: <<vertical_align>>\n"
                status_string += f"{indent3}horizontal_offset: <<horizontal_offset>>\n"
                status_string += f"{indent3}vertical_offset: <<vertical_offset>>\n"
            else:
                status_string += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                status_string += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                status_string += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                status_string += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"

            if use_backdrop:
                logger.info(f"{indentlog2}'use_backdrop' set to 'true'")
                logger.info(f"{indentlog3}Adding backdrop settings to yaml")
                status_string += f"{indent3}back_color: <<back_color>>\n"
                if use_text_overrides:
                    status_string += f"{indent3}back_width: <<back_width>>\n"
                    status_string += f"{indent3}back_height: <<back_height>>\n"
                    status_string += f"{indent3}back_radius: <<back_radius>>\n"
                else:
                    status_string += f"{indent3}back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}\n"
                    status_string += f"{indent3}back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}\n"
                    status_string += f"{indent3}back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}\n"
            else:
                logger.info(f"{indentlog2}'use_backdrop' set to 'false'")
                logger.info(f"{indentlog3}Removing backdrop settings from status yaml.")

            if use_text_overrides:
                status_string += f"{indent2}default:\n"
                status_string += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                status_string += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                status_string += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                status_string += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"
                if use_backdrop:
                    status_string += f"{indent3}back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}\n"
                    status_string += f"{indent3}back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}\n"
                    status_string += f"{indent3}back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}\n"

            status_string += f"""{indent2}ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results').lower()}
    tmdb_discover:
      air_date.gte: <<date>>
      air_date.lte: <<date>>
      with_status: <<status>>
"""
            if use_watch_region:
                logger.info(f"{indentlog2}'watch_region' set to 'true'")
                logger.info(f"{indentlog3}Adding 'watch_region: {get_with_defaults(overlay_settings, 'watch_region', 'watch_region')}'.")
                logger.info(f"{indentlog3}Adding 'with_watch_monetization_type: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}'.")
                status_string += f"{indent3}watch_region: {get_with_defaults(overlay_settings, 'watch_region')}\n"
                status_string += f"{indent3}with_watch_monetization_types: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}\n"

            else:
                logger.info(f"{indentlog2}'watch_region' set to 'false'")
                logger.info(f"{indentlog3}Removing 'watch_region'.")
                logger.info(f"{indentlog3}Removing 'with_watch_monetizaion_types'.")
            
            if not is_anime:
                logger.info(f"{indentlog2}'is_anime' set to 'false'")
                logger.info(f"{indentlog3}Adding 'with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}'.")
                status_string += f"{indent3}with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}\n"

            else:
                logger.info(f"{indentlog2}'is_anime' set to 'true'")
                logger.info(f"{indentlog3}Removing 'with_original_language'.")

            status_string += f"{indent3}limit: {get_with_defaults(overlay_settings, 'limit', 'limit')}\n"

            plex_all = f"""
  {library_name} Status Plex All:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status
      weight: <<weight>>
      name: text(<<text>>)
      font: "{get_with_defaults(overlay_settings, 'font', 'font', config_directory)}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: <<font_color>>
"""
            if use_text_overrides:
                plex_all += f"{indent3}horizontal_align: <<horizontal_align>>\n"
                plex_all += f"{indent3}vertical_align: <<vertical_align>>\n"
                plex_all += f"{indent3}horizontal_offset: <<horizontal_offset>>\n"
                plex_all += f"{indent3}vertical_offset: <<vertical_offset>>\n"
            else:
                plex_all += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                plex_all += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                plex_all += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                plex_all += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"

            if use_backdrop:
                plex_all += f"{indent3}back_color: <<back_color>>\n"
                if use_text_overrides:
                    plex_all += f"{indent3}back_width: <<back_width>>\n"
                    plex_all += f"{indent3}back_height: <<back_height>>\n"
                    plex_all += f"{indent3}back_radius: <<back_radius>>\n"
                else:
                    plex_all += f"{indent3}back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}\n"
                    plex_all += f"{indent3}back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}\n"
                    plex_all += f"{indent3}back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}\n"

            if use_text_overrides:
                plex_all += f"{indent2}default:\n"
                plex_all += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                plex_all += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                plex_all += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                plex_all += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"
                if use_backdrop:
                    plex_all += f"{indent3}back_width: {get_with_defaults(overlay_settings, 'back_width', 'back_width')}\n"
                    plex_all += f"{indent3}back_height: {get_with_defaults(overlay_settings, 'back_height', 'back_height')}\n"
                    plex_all += f"{indent3}back_radius: {get_with_defaults(overlay_settings, 'back_radius', 'back_radius')}\n"

            plex_all += f"""{indent2}ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results').lower()}
"""
            status_string += plex_all

            use_bd_overrides = any_status_uses_overrides(use_overlays, BD_OVERRIDE_KEYS)

            image_discover_template = f"""
  {library_name} Backdrop Image TMDB Discover:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status_bg
      weight: <<weight>>
      name: status-image
      file: <<file>>
"""
            if use_bd_overrides:
                image_discover_template += f"{indent3}horizontal_align: <<horizontal_align>>\n"
                image_discover_template += f"{indent3}vertical_align: <<vertical_align>>\n"
                image_discover_template += f"{indent3}horizontal_offset: <<horizontal_offset>>\n"
                image_discover_template += f"{indent3}vertical_offset: <<vertical_offset>>\n"
                image_discover_template += f"{indent2}default:\n"
                image_discover_template += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                image_discover_template += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                image_discover_template += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                image_discover_template += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"
            else:
                image_discover_template += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                image_discover_template += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                image_discover_template += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                image_discover_template += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"

            image_discover_template += f"{indent2}ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results').lower()}\n"
            image_discover_template += f"""    tmdb_discover:
      air_date.gte: <<date>>
      air_date.lte: <<date>>
      with_status: <<status>>
"""
            if use_watch_region:
                image_discover_template += f"{indent3}watch_region: {get_with_defaults(overlay_settings, 'watch_region')}\n"
                image_discover_template += f"{indent3}with_watch_monetization_types: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}\n"
            if not is_anime:
                image_discover_template += f"{indent3}with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}\n"
            image_discover_template += f"{indent3}limit: {get_with_defaults(overlay_settings, 'limit', 'limit')}\n"

            image_plex_all_template = f"""
  {library_name} Backdrop Image Plex All:
    sync_mode: sync
    builder_level: show
    overlay:
      group: status_bg
      weight: <<weight>>
      name: status-image
      file: <<file>>
"""
            if use_bd_overrides:
                image_plex_all_template += f"{indent3}horizontal_align: <<horizontal_align>>\n"
                image_plex_all_template += f"{indent3}vertical_align: <<vertical_align>>\n"
                image_plex_all_template += f"{indent3}horizontal_offset: <<horizontal_offset>>\n"
                image_plex_all_template += f"{indent3}vertical_offset: <<vertical_offset>>\n"
                image_plex_all_template += f"{indent2}default:\n"
                image_plex_all_template += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                image_plex_all_template += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                image_plex_all_template += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                image_plex_all_template += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"
            else:
                image_plex_all_template += f"{indent3}horizontal_align: {get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align')}\n"
                image_plex_all_template += f"{indent3}vertical_align: {get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align')}\n"
                image_plex_all_template += f"{indent3}horizontal_offset: {get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset')}\n"
                image_plex_all_template += f"{indent3}vertical_offset: {get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset')}\n"

            image_plex_all_template += f"{indent2}ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results').lower()}\n"
            any_backdrop_image = any(v.get('backdrop_image') for v in use_overlays.values() if isinstance(v, dict))
            if any_backdrop_image:
                status_string += image_discover_template
                status_string += image_plex_all_template

            status_string += "\noverlays:"

            logger.info(f"{indentlog}Main template created")
            logger.info(f"{indentlog}Creating optional overlays")

##########################
#### UPCOMING SERIES #####
##########################

            upcoming_series_settings = use_overlays.get("upcoming_series", {})
            if get_with_defaults(upcoming_series_settings, "use", "use"):
                logger.info(f"{indentlog2}'Upcoming' set to true. Creating 'Upcoming' overlay.")

                si = upcoming_series_settings.get('backdrop_image')
                if si:
                    status_string += get_backdrop_image(si, library_name, "Upcoming Series", 100, "Backdrop Image Plex All", align_offset_vars=get_align_offset_overrides(upcoming_series_settings))
                    status_string += f"""    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      release.after: today
"""

                upcoming_section = f"""
# UPCOMING SERIES OVERLAY
  {library_name} Upcoming Series:
    variables: {{text: {get_with_defaults(upcoming_series_settings, 'text', 'upcoming_text')}, weight: 100, font_color: "{get_with_defaults(upcoming_series_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(upcoming_series_settings, 'back_color', 'upcoming_back_color')}"{get_backdrop_overrides(upcoming_series_settings)}{get_text_align_offset_overrides(upcoming_series_settings)}}}
    template: {{name: {library_name} Status Plex All}}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      release.after: today
"""
                status_string += upcoming_section
            else:
                logger.info(f"{indentlog2}'Upcoming' set to false. 'Upcoming' overlay not created.")

##########################
####    NEW SERIES   #####
##########################

            new_series_settings = use_overlays.get("new_series", {})
            if get_with_defaults(new_series_settings, "use", "use"):
                logger.info(f"{indentlog2}'New Series' set to true. Creating 'New Series' overlay.")

                si = new_series_settings.get('backdrop_image')
                if si:
                    status_string += get_backdrop_image(si, library_name, "New Series", 76, "Backdrop Image Plex All", align_offset_vars=get_align_offset_overrides(new_series_settings))
                    status_string += f"""    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
        - ended
        - canceled
      first_episode_aired.after: {date_21_days_prior}
"""

                new_series_section = f"""
# NEW SERIES BANNER/TEXT
  {library_name} New Series:
    variables: {{text: {get_with_defaults(new_series_settings, 'text', 'new_text')}, weight: 76, font_color: "{get_with_defaults(new_series_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(new_series_settings, 'back_color', 'new_back_color')}"{get_backdrop_overrides(new_series_settings)}{get_text_align_offset_overrides(new_series_settings)}}}
    template: {{name: {library_name} Status Plex All}}
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
                status_string += new_series_section
            else:
                logger.info(f"{indentlog2}'New Series' set to false. Creating 'New Series' overaly.")


##########################
###  NEW AIRING NEXT   ###
##########################

            new_airing_next_settings = use_overlays.get('new_airing_next', {})

            new_airing_next_dates = [(current_date + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(1, 15)]

            if get_with_defaults(new_airing_next_settings, "use", "use"):
                logger.info(f"{indentlog2}'New Airing Next' set to true. Creating 'New Airing Next' overlay.")
                
                for i, next_day_date_str in enumerate(new_airing_next_dates, start=1):
                    next_day_date = datetime.strptime(next_day_date_str, '%m/%d/%Y')
                    mmddyyyy = next_day_date.strftime('%m/%d/%Y')

                    mmdd_custom = next_day_date.strftime(date_format)
                    mmddyyyy_custom = next_day_date.strftime(date_format_with_year)

                    weight = 90 - i + 1 

                    si = new_airing_next_settings.get('backdrop_image')
                    if si:
                        status_string += get_backdrop_image(si, library_name, f"New Airing Next {mmddyyyy_custom}", weight, "Backdrop Image TMDB Discover", f", date: {mmddyyyy}, status: 0", get_align_offset_overrides(new_airing_next_settings))
                        status_string += f"""    filters:
      first_episode_aired.after: {date_21_days_prior}
"""

                    new_airing_next_section = f"""
# NEW AIRING NEXT BANNER/TEXT DAY {i}
  {library_name} New Airing Next {mmddyyyy_custom}: 
    variables: {{text: {get_with_defaults(new_airing_next_settings, 'text', 'new_airing_text')} {mmdd_custom}, weight: {weight}, font_color: "{get_with_defaults(new_airing_next_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(new_airing_next_settings, 'back_color', 'new_airing_back_color')}"{get_backdrop_overrides(new_airing_next_settings)}{get_text_align_offset_overrides(new_airing_next_settings)}, date: {mmddyyyy}, status: 0}}
    template: {{name: {library_name} Status TMDB Discover}}
    filters:
      first_episode_aired.after: {date_21_days_prior}
"""
                    status_string += new_airing_next_section
            else:
                logger.info(f"{indentlog2}'New Airing Next' set to false. 'New Airing Next' Overlay not created")
                
##########################
####  AIRING SERIES  #####
##########################

            airing_series_settings = use_overlays.get("airing_series", {})
            if get_with_defaults(airing_series_settings, "use", "use"):
                logger.info(f"{indentlog2}'Airing Series' set to true. Creating 'Airing' overlay")

                si = airing_series_settings.get('backdrop_image')
                if si:
                    status_string += get_backdrop_image(si, library_name, "Airing Series", 43, "Backdrop Image Plex All", align_offset_vars=get_align_offset_overrides(airing_series_settings))
                    status_string += f"""    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      last_episode_aired.after: {date_15_days_prior}
"""

                airing_series_section = f"""
# AIRING SERIES BANNER/TEXT
  {library_name} Airing Series:
    variables: {{text: {get_with_defaults(airing_series_settings, 'text', 'airing_text')}, weight: 43, font_color: "{get_with_defaults(airing_series_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(airing_series_settings, 'back_color', 'airing_back_color')}"{get_backdrop_overrides(airing_series_settings)}{get_text_align_offset_overrides(airing_series_settings)}}}
    template: {{name: {library_name} Status Plex All}}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
      last_episode_aired.after: {date_15_days_prior}
    """
                status_string += airing_series_section

            else:
                logger.info(f"{indentlog2}'Airing Series' set to false. 'Airing' Overlay not created.")

##########################
####  AIRING TODAY   #####
##########################

            airing_today_settings = use_overlays.get("airing_today", {})
            if get_with_defaults(airing_today_settings, "use", "use"):
                logger.info(f"{indentlog2}'Airing Today' set to true. Creating 'Airing Today' overlay.")

                si = airing_today_settings.get('backdrop_image')
                if si:
                    status_string += get_backdrop_image(si, library_name, "Airing Today", 75, "Backdrop Image TMDB Discover", f", date: {air_date_today}, status: 0", get_align_offset_overrides(airing_today_settings))

                airing_today_section = f"""
# AIRING TODAY BANNER/TEXT
  {library_name} Airing Today:
    variables: {{text: {get_with_defaults(airing_today_settings, 'text', 'today_text')}, weight: 75, font_color: "{get_with_defaults(airing_today_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(airing_today_settings, 'back_color', 'airing_back_color')}"{get_backdrop_overrides(airing_today_settings)}{get_text_align_offset_overrides(airing_today_settings)}, date: {air_date_today}, status: 0}}
    template: {{name: {library_name} Status TMDB Discover}}
"""
                status_string += airing_today_section

            else:
                logger.info(f"{indentlog2}Airing Today set to false. 'Airing Today' overlay not created")

##########################
####   AIRING NEXT   #####
##########################

            airing_next_settings = use_overlays.get('airing_next', {})

            days_ahead = min(get_with_defaults(overlay_settings, 'days_ahead', 'days_ahead'), 30)
            airing_next_dates = [(current_date + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(1, days_ahead + 1)]

            if get_with_defaults(airing_next_settings, "use", "use"):
                logger.info(f"{indentlog2}'Airing Next' set to true. 'days_ahead:' set to {days_ahead}. Creating {days_ahead} 'Airing Next' overlay/s")
                
                for i, next_day_date_str in enumerate(airing_next_dates, start=1):
                    next_day_date = datetime.strptime(next_day_date_str, '%m/%d/%Y')
                    mmddyyyy = next_day_date.strftime('%m/%d/%Y')

                    mmdd_custom = next_day_date.strftime(date_format)
                    mmddyyyy_custom = next_day_date.strftime(date_format_with_year)

                    weight = 74 - i + 1

                    si = airing_next_settings.get('backdrop_image')
                    if si:
                        status_string += get_backdrop_image(si, library_name, f"Airing Next {mmddyyyy_custom}", weight, "Backdrop Image TMDB Discover", f", date: {mmddyyyy}, status: 0", get_align_offset_overrides(airing_next_settings))
                        status_string += f"""    filters:
      last_episode_aired.after: {date_15_days_prior}
"""

                    airing_next_section = f"""
# AIRING NEXT BANNER/TEXT DAY {i}
  {library_name} Airing Next {mmddyyyy_custom}:
    variables: {{text: {get_with_defaults(airing_next_settings, 'text', 'next_text')} {mmdd_custom}, weight: {weight}, font_color: "{get_with_defaults(airing_next_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(airing_next_settings, 'back_color', 'airing_back_color')}"{get_backdrop_overrides(airing_next_settings)}{get_text_align_offset_overrides(airing_next_settings)}, date: {mmddyyyy}, status: 0}}
    template: {{name: {library_name} Status TMDB Discover}}
    filters:
      last_episode_aired.after: {date_15_days_prior}
"""
                    status_string += airing_next_section

            else:
                logger.info(f"{indentlog2}'Airing Next' set to false. 'Airing Next' overlay not created.")

##########################
####   ENDED SERIES   ####
##########################

            ended_series_settings = use_overlays.get("ended_series", {})

            if get_with_defaults(ended_series_settings, "use", "use"):
                logger.info(f"{indentlog2}'Ended Series' set to true. Creating 'Ended Series' overlay.")

                si = ended_series_settings.get('backdrop_image')
                if si:
                    status_string += get_backdrop_image(si, library_name, "Ended Series", 9, "Backdrop Image Plex All", align_offset_vars=get_align_offset_overrides(ended_series_settings))
                    status_string += f"""    plex_all: true
    filters:
      tmdb_status:
        - ended
"""

                ended_series_section = f"""
# ENDED SERIES BANNER/TEXT
  {library_name} Ended Series:
    variables: {{text: {get_with_defaults(ended_series_settings, 'text', 'ended_text')}, weight: 9, font_color: "{get_with_defaults(ended_series_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(ended_series_settings, 'back_color', 'ended_back_color')}"{get_backdrop_overrides(ended_series_settings)}{get_text_align_offset_overrides(ended_series_settings)}}}
    template: {{name: {library_name} Status Plex All}}
    plex_all: true
    filters:
      tmdb_status:
        - ended
    """
                status_string += ended_series_section
            else:
                logger.info(f"{indentlog2}'Ended Sereies' set to false. 'Ended Series' overlay not created")
            
##########################
#### CANCELED SERIES  ####
##########################

            canceled_series_settings = use_overlays.get("canceled_series", {})

            if get_with_defaults(canceled_series_settings, "use", "use"):
                logger.info(f"{indentlog2}'Canceled Series' set to true. Creating 'Canceled Series' overlay.")

                si = canceled_series_settings.get('backdrop_image')
                if si:
                    status_string += get_backdrop_image(si, library_name, "Canceled Series", 10, "Backdrop Image Plex All", align_offset_vars=get_align_offset_overrides(canceled_series_settings))
                    status_string += f"""    plex_all: true
    filters:
      tmdb_status:
        - canceled
"""

                canceled_series_section = f"""
# CANCELED SERIES BANNER/TEXT
  {library_name} Canceled Series:
    variables: {{text: {get_with_defaults(canceled_series_settings, 'text', 'canceled_text')}, weight: 10, font_color: "{get_with_defaults(canceled_series_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(canceled_series_settings, 'back_color', 'canceled_back_color')}"{get_backdrop_overrides(canceled_series_settings)}{get_text_align_offset_overrides(canceled_series_settings)}}}
    template: {{name: {library_name} Status Plex All}}
    plex_all: true
    filters:
      tmdb_status:
        - canceled
    """
                status_string += canceled_series_section
            else:
                logger.info(f"{indentlog2}'Canceled Series' set to false. 'Canceled Series' overlay not created.")
            
##########################
#### RETURNING SERIES ####
##########################

            returning_series_settings = use_overlays.get("returning_series", {})

            if get_with_defaults(returning_series_settings, "use", "use"):
                logger.info(f"{indentlog2}'Returning Series' set to true. Creating 'Returning' overlay.")

                si = returning_series_settings.get('backdrop_image')
                if si:
                    status_string += get_backdrop_image(si, library_name, "Returning Series", 12, "Backdrop Image Plex All", align_offset_vars=get_align_offset_overrides(returning_series_settings))
                    status_string += f"""    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
"""

                returning_series_section = f"""
# RETURNING SERIES BANNER/TEXT
  {library_name} Returning Series:
    variables: {{text: {get_with_defaults(returning_series_settings, 'text', 'returning_text')}, weight: 12, font_color: "{get_with_defaults(returning_series_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(returning_series_settings, 'back_color', 'returning_back_color')}"{get_backdrop_overrides(returning_series_settings)}{get_text_align_offset_overrides(returning_series_settings)}}}
    template: {{name: {library_name} Status Plex All}}
    plex_all: true
    filters:
      tmdb_status:
        - returning
        - planned
        - production
    """
                status_string += returning_series_section
            else:
                logger.info(f"{indentlog2}'Returning' set to false. 'Returning' overlay not created")

##########################
####   RETURNS NEXT  #####
##########################

            returns_next_settings = use_overlays.get('returns_next', {})

            days_ahead = min(get_with_defaults(overlay_settings, 'days_ahead', 'days_ahead'), 30)
            returns_next_dates = [(current_date + timedelta(days=i)).strftime('%m/%d/%Y') for i in range(1, days_ahead + 1)]

            if get_with_defaults(returns_next_settings, "use", "use"):
                logger.info(f"{indentlog2}'Returns Next' set to true. 'days_ahead:' set to {days_ahead}. Creating {days_ahead} 'Returns Next' overlay/s")
                
                for i, next_day_date_str in enumerate(returns_next_dates, start=1):
                    next_day_date = datetime.strptime(next_day_date_str, '%m/%d/%Y')
                    mmddyyyy = next_day_date.strftime('%m/%d/%Y')

                    mmdd_custom = next_day_date.strftime(date_format)
                    mmddyyyy_custom = next_day_date.strftime(date_format_with_year)

                    weight = 42 - i + 1

                    si = returns_next_settings.get('backdrop_image')
                    if si:
                        status_string += get_backdrop_image(si, library_name, f"Returns Next {mmddyyyy_custom}", weight, "Backdrop Image TMDB Discover", f", date: {mmddyyyy}, status: 0", get_align_offset_overrides(returns_next_settings))
                        status_string += f"""    filters:
      last_episode_aired.before: {date_14_days_prior}
"""

                    returns_next_section = f"""
# RETURNS NEXT BANNER/TEXT DAY {i}
  {library_name} Returns Next {mmddyyyy_custom}:
    variables: {{text: {get_with_defaults(returns_next_settings, 'text', 'returns_text')} {mmdd_custom}, weight: {weight}, font_color: "{get_with_defaults(returns_next_settings, 'font_color', 'font_color')}", back_color: "{get_with_defaults(returns_next_settings, 'back_color', 'returning_back_color')}"{get_backdrop_overrides(returns_next_settings)}{get_text_align_offset_overrides(returns_next_settings)}, date: {mmddyyyy}, status: 0}}
    template: {{name: {library_name} Status TMDB Discover}}
    filters:
      last_episode_aired.before: {date_14_days_prior}
"""
                    status_string += returns_next_section
            else:
                logger.info(f"{indentlog2}'Returns Next' set to false. 'Returns Next' overlay/s not created")

############################
#  WRITE STATUS YAML   #
############################

            overlay_save_folder = overlay_settings.get('overlay_save_folder')
            save_folder = overlay_save_folder
            normalized_library_name = library_name.lower().replace(' ', '-')
            file_name = f"overlay-status-{normalized_library_name}.yml"
            name = 'Show Status Overlay'

            write_yaml_file(config_directory, save_folder, name, file_name, status_string)

    except Exception as e:
        logger.error(f"An error occurred while generating 'Show Status Overlay' files: {e}")

#############################
# NEW MOVIE RELEASE OVERLAY #
#############################

def create_new_movie_yaml(config_directory):
    try:
        settings = load_settings(config_directory, log_message=False)
        
        overlay_settings = settings.get('status_overlay', {}).get('overlay_settings', {})

        new_release_settings = settings.get('movie_new_release', {})

        use_backdrop = get_with_defaults(new_release_settings, 'use_backdrop', 'use_backdrop')

        if get_with_defaults(new_release_settings, "use", "new_movie_use"):
            logger.info(f"{indentlog}'movie_new_release' 'use:' set to true. Creating 'movie_new_release' overlay.")

            si = new_release_settings.get('backdrop_image')

            new_movie_string = "# New Release Overlay\noverlays:\n"

            if si:
                new_movie_string += f"""  Movie New Release Image:
    sync_mode: sync
    builder_level: movie
    overlay:
      group: status_bg
      weight: 100
      name: status-image
      file: {si}
      horizontal_align: {new_release_settings.get('bd_horizontal_align', get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align'))}
      vertical_align: {new_release_settings.get('bd_vertical_align', get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align'))}
      horizontal_offset: {new_release_settings.get('bd_horizontal_offset', get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset'))}
      vertical_offset: {new_release_settings.get('bd_vertical_offset', get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset'))}
    ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results').lower()}
    plex_search:
      all:
        release: {get_with_defaults(new_release_settings, 'days_to_consider_new', 'days_new')}
"""

            new_movie_string += f"""  Movie New Release:
    sync_mode: sync
    builder_level: movie
    overlay:
"""
            if si:
                new_movie_string += f"{indent3}group: status\n"
                new_movie_string += f"{indent3}weight: 100\n"
            new_movie_string += f"""{indent3}name: text({get_with_defaults(new_release_settings, 'text', 'new_movie_text')})
      font: "{get_with_defaults(overlay_settings, 'font', 'font', config_directory)}"
      font_size: {get_with_defaults(overlay_settings, 'font_size', 'font_size')}
      font_color: "{get_with_defaults(new_release_settings, 'font_color', 'font_color')}"
      horizontal_align: {new_release_settings.get('text_horizontal_align', get_with_defaults(overlay_settings, 'horizontal_align', 'horizontal_align'))}
      vertical_align: {new_release_settings.get('text_vertical_align', get_with_defaults(overlay_settings, 'vertical_align', 'vertical_align'))}
      horizontal_offset: {new_release_settings.get('text_horizontal_offset', get_with_defaults(overlay_settings, 'horizontal_offset', 'horizontal_offset'))}
      vertical_offset: {new_release_settings.get('text_vertical_offset', get_with_defaults(overlay_settings, 'vertical_offset', 'vertical_offset'))}
"""
            if use_backdrop:
                logger.info(f"{indentlog2}'use_backdrop' set to 'true'")
                logger.info(f"{indentlog3}Adding backdrop settings to yaml")
                new_movie_string += f"{indent3}back_color: \"{get_with_defaults(new_release_settings, 'back_color', 'back_color')}\"\n"
                new_movie_string += f"{indent3}back_width: {new_release_settings.get('back_width', get_with_defaults(overlay_settings, 'back_width', 'back_width'))}\n"
                new_movie_string += f"{indent3}back_height: {new_release_settings.get('back_height', get_with_defaults(overlay_settings, 'back_height', 'back_height'))}\n"
                new_movie_string += f"{indent3}back_radius: {new_release_settings.get('back_radius', get_with_defaults(overlay_settings, 'back_radius', 'back_radius'))}\n"

            else:
                logger.info(f"{indentlog2}'use_backdrop' set to 'false'")
                logger.info(f"{indentlog3}Removing backdrop settings from 'Movie New Release' yaml.")

            new_movie_string += f"""{indent2}ignore_blank_results: {get_with_defaults(overlay_settings, 'ignore_blank_results', 'ignore_blank_results').lower()}
    plex_search:
      all:
        release: {get_with_defaults(new_release_settings, 'days_to_consider_new', 'days_new')}
"""

################################
# WRITE MOVIE NEW RELEASE YAML #
################################

            new_movie_save_folder = new_release_settings.get('new_movie_save_folder')
            save_folder = new_movie_save_folder
            file_name = f"overlay-movie-new-release.yml"
            name = 'New Release Overlay'

            write_yaml_file(config_directory, save_folder, name, file_name, new_movie_string)

        else:
            logger.info(f"{indentlog2}'movie_new_release' set to false. 'new_movie_relase_date' overlay not created")
            logger.info("")
            
    except Exception as e:
        logger.error(f"An error occurred while 'movie_new_release' overlay file: {e}")

#############################
# RETURNING SOON COLLECTION #
#############################

def create_collection_yaml(config_directory):
    try:
        settings = load_settings(config_directory, log_message=False)
        
        libraries = settings.get('libraries', {})

        overlay_settings = settings.get('status_overlay', {}).get('overlay_settings', {})

        collection_settings = settings.get('returning_soon_collection', {})

        current_date = datetime.now()

        days_last_aired = get_with_defaults(collection_settings, 'days_last_aired', 'days_last_aired')

        date_last_aired = (current_date - timedelta(days=days_last_aired)).strftime('%m/%d/%Y')

        air_date = (current_date).strftime('%m/%d/%Y')

        collection_days_ahead = get_with_defaults(collection_settings, 'collection_days_ahead', 'collection_days_ahead')

        collection_days_past = (current_date + timedelta(days=collection_days_ahead)).strftime('%m/%d/%Y')

        for library_name, library_settings in libraries.items():
            if library_settings.get('library_type') != 'show':
                continue
            is_anime = get_with_defaults(library_settings, 'is_anime', 'is_anime')
            use_watch_region = get_with_defaults(library_settings, 'use_watch_region', 'use_watch_region')
            
            if get_with_defaults(collection_settings, "use", "collection_use"):
                logger.info(f"{indentlog}Returning Soon Collection 'use:' set to true. Creating Returning Soon Collection yaml for {library_name}.")

                use_poster = get_with_defaults(collection_settings, 'use_poster', 'use_poster')
            
                if not use_poster:
                    logger.info(f"{indentlog2}'use_poster' set to {use_poster}. Excluding poster setting from collection YAML")

                collection_string = f"""# {library_name} Returning Soon Collection
collections:
  {library_name} Returning Soon:
"""
                if use_poster:
                    poster_source = get_with_defaults(collection_settings, 'poster_source', 'poster_source')
                    poster_path = get_with_defaults(collection_settings, 'poster_path', 'poster_path', config_directory)
                    collection_string += f"{indent2}{poster_source}_poster: \"{poster_path}\"\n"

                collection_string += f"""{indent2}collection_order: custom
    visible_home: {get_with_defaults(collection_settings, 'visible_home', 'visible_home').lower()}
    visible_shared: {get_with_defaults(collection_settings, 'visible_shared', 'visible_shared').lower()}
    visible_library: {get_with_defaults(collection_settings, 'visible_library', 'visible_library').lower()}
    sync_mode: sync
    summary: "{get_with_defaults(collection_settings, 'summary', 'summary')}"
    minimum_items: {get_with_defaults(collection_settings, 'minimum_items', 'minimum_items')}
    delete_below_minimum: {get_with_defaults(collection_settings, 'delete_below_minimum', 'delete_below_minimum').lower()}
    sort_title: "{get_with_defaults(collection_settings, 'sort_title', 'sort_title')}"
    tmdb_discover:
      air_date.gte: {air_date}
      air_date.lte: {collection_days_past}
      with_status: 0
"""
                if use_watch_region:
                    logger.info(f"{indentlog2}'watch_region' set to 'true'")
                    logger.info(f"{indentlog3}Adding 'watch_region: {get_with_defaults(overlay_settings, 'watch_region', 'watch_region')}'.")
                    logger.info(f"{indentlog3}Adding 'with_watch_monetization_type: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}'.")
                    collection_string += f"{indent3}watch_region: {get_with_defaults(overlay_settings, 'watch_region', 'watch_region')}\n"
                    collection_string += f"{indent3}with_watch_monetization_types: {get_with_defaults(overlay_settings, 'with_watch_monetization_types', 'with_watch_monetization_types')}\n"

                else:
                    logger.info(f"{indentlog2}'watch_region' set to 'false'")
                    logger.info(f"{indentlog3}Removing 'watch_region'.")
                    logger.info(f"{indentlog3}Removing 'with_watch_monetizaion_types'.")

                if not is_anime:
                    logger.info(f"{indentlog2}'is_anime' set to 'false'")
                    logger.info(f"{indentlog3}Adding 'with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}'.")
                    collection_string += f"{indent3}with_original_language: {get_with_defaults(overlay_settings, 'with_original_language', 'with_original_language')}\n"

                else:
                    logger.info(f"{indentlog2}'is_anime' set to 'true'")
                    logger.info(f"{indentlog3}Removing 'with_original_language'.")

                collection_string += f"{indent3}limit: {get_with_defaults(overlay_settings, 'limit', 'limit')}\n"
                
                collection_string += f"{indent2}filters:\n"
                collection_string += f"{indent3}last_episode_aired.before: {date_last_aired}\n"

############################
#  WRITE COLLECTION YAML   #
############################

                collection_save_folder = collection_settings.get('collection_save_folder')
                save_folder = collection_save_folder
                normalized_library_name = library_name.lower().replace(' ', '-')
                file_name = f"collection-returning-soon-{normalized_library_name}.yml"
                name = 'Returning Soon Collection'

                write_yaml_file(config_directory, save_folder, name, file_name, collection_string)

            else:
                logger.info(f"{indentlog2}Returning Soon Collection 'use:' set to false. Returning Soon Collection not created")
                logger.info("")

    except Exception as e:
        logger.error(f"An error occurred while generating 'Returning Soon Collection' files: {e}")

#########################
# IN HISTORY COLLECTION #
#########################

def create_in_history_yaml(config_directory):
    try:
        settings = load_settings(config_directory, log_message=False)
        
        in_history_settings = settings.get('in_history_collection', {})
        starting_year = get_with_defaults(in_history_settings, 'starting_year', 'start_year' )
        ending_year = in_history_settings.get('ending_year', datetime.now().year)
        in_history_range = get_with_defaults(in_history_settings, 'in_history_range', 'range')

        current_date = datetime.now()   
        current_week_monday = current_date - timedelta(days=current_date.weekday())
        first_day_of_month = datetime(current_date.year, current_date.month, 1)

        def generate_date_ranges(range_type):
            date_ranges = []
            for year in range(starting_year, ending_year + 1):
                if range_type == 'days':
                    date_before = (datetime(year, current_date.month, current_date.day) - timedelta(days=1)).strftime('%m/%d/%Y')
                    date_after = (datetime(year, current_date.month, current_date.day) + timedelta(days=1)).strftime('%m/%d/%Y')
                    date_ranges.append({
                        'release.after': date_before,
                        'release.before': date_after
                    })
                elif range_type == 'months':
                    days_in_month = (datetime(year, current_date.month % 12 + 1, 1) - timedelta(days=1)).day
                    date_before = (datetime(year, first_day_of_month.month, 1) - timedelta(days=1)).strftime('%m/%d/%Y')
                    date_after = (datetime(year, first_day_of_month.month, days_in_month) + timedelta(days=1)).strftime('%m/%d/%Y')
                    date_ranges.append({
                        'release.after': date_before,
                        'release.before': date_after
                    })
                elif range_type == 'weeks':
                    start_of_week = datetime(year, current_week_monday.month, current_week_monday.day) - timedelta(days=datetime(year, current_week_monday.month, current_week_monday.day).weekday())  # Monday
                    end_of_week = start_of_week + timedelta(days=6)  # Sunday
                    date_before = (start_of_week - timedelta(days=1)).strftime('%m/%d/%Y')
                    date_after = (end_of_week + timedelta(days=1)).strftime('%m/%d/%Y')
                    date_ranges.append({
                        'release.after': date_before,
                        'release.before': date_after
                    })
            return date_ranges

        date_ranges = generate_date_ranges(in_history_range)

        if get_with_defaults(in_history_settings, "use", "in_history_use"):
            logger.info(f"{indentlog}'in_history' 'use:' set to true. Creating 'in_history' collection.")

            use_poster = get_with_defaults(in_history_settings, 'use_poster', 'IH_use_poster')
        
            if not use_poster:
                logger.info(f"{indentlog2}'use_poster' set to {use_poster}. Excluding poster setting from collection YAML")

            if in_history_range == 'days':
                summary_range = 'day'
                title_range = 'Day'
            elif in_history_range == 'months':
                summary_range = 'month'
                title_range = 'Month'
            elif in_history_range == 'weeks':
                summary_range = 'week'
                title_range = 'Week'

            in_history_string = f"""# This {title_range} in History
collections:
  This {title_range} in History:
"""
            if use_poster:
                poster_source = get_with_defaults(in_history_settings, 'poster_source', 'IH_poster_source')
                poster_path = get_with_defaults(in_history_settings, 'poster_path', 'IH_poster_path', config_directory)
                in_history_string += f"{indent2}{poster_source}_poster: \"{poster_path}\"\n"

            in_history_string += f"""{indent2}collection_order: release
    visible_home: {get_with_defaults(in_history_settings, 'visible_home', 'IH_visible_home').lower()}
    visible_shared: {get_with_defaults(in_history_settings, 'visible_shared', 'IH_visible_shared').lower()}
    visible_library: {get_with_defaults(in_history_settings, 'visible_library', 'IH_visible_library').lower()}
    sync_mode: sync
    summary: "Released this {summary_range} in history."
    minimum_items: {get_with_defaults(in_history_settings, 'minimum_items', 'IH_minimum_items')}
    delete_below_minimum: {get_with_defaults(in_history_settings, 'delete_below_minimum', 'IH_delete_below_minimum').lower()}
    sort_title: "{get_with_defaults(in_history_settings, 'sort_title', 'IH_sort_title')}"
    plex_search:
      any:
        all:
"""
            for date_range in date_ranges:
                in_history_string += f"{indent4}  - release.after: {date_range['release.after']}\n"
                in_history_string += f"{indent4}    release.before: {date_range['release.before']}\n"

###############################
# WRITE IN HISTORY COLLECTION #
###############################

            in_history_save_folder = in_history_settings.get('in_history_save_folder')
            save_folder = in_history_save_folder
            file_name = "collection-in-history.yml"
            name = f'This {title_range} in History Collection'

            write_yaml_file(config_directory, save_folder, name, file_name, in_history_string)

        else:
            logger.info(f"{indentlog2}'in-history' set to false. 'In History Collection' not created")
            logger.info("")
            
    except Exception as e:
        logger.error(f"An error occurred while creating 'In History Collection' file: {e}")

##################
# Top 10 Overlay #
##################

def create_top10_overlay_yaml(config_directory):
    try:
        settings = load_settings(config_directory, log_message=False)
        
        top_overlay_settings = settings.get('top_10', {}).get('top_10_overlay', {})

        if get_with_defaults(top_overlay_settings, "use", "top_overlay_use"):
            logger.info(f"{indentlog}'top_10' overlay 'use:' set to true. Creating 'top_10' overlay.")

            top_overlay_string = f"""# Top 10 Overlay
templates:
  Top 10 Overlay:
    overlay:
      name: text(TOP 10)
      group: top10
      weight: <<weight>>
      font: "{get_with_defaults(top_overlay_settings, 'font', 'font', config_directory)}"
      font_size: {get_with_defaults(top_overlay_settings, 'font_size', 'top_font_size')}
      font_color: "{get_with_defaults(top_overlay_settings, 'font_color', 'top_font_color')}"
      horizontal_align: {get_with_defaults(top_overlay_settings, 'horizontal_align', 'top_horizontal_align')}
      vertical_align: {get_with_defaults(top_overlay_settings, 'vertical_align', 'top_vertical_align')}
      horizontal_offset: {get_with_defaults(top_overlay_settings, 'horizontal_offset', 'top_horizontal_offset')}
      vertical_offset: {get_with_defaults(top_overlay_settings, 'vertical_offset', 'top_vertical_offset')}
"""
            use_backdrop = get_with_defaults(top_overlay_settings, 'use_backdrop', 'use_backdrop')
            if use_backdrop:
                logger.info(f"{indentlog2}'use_backdrop' set to 'true'")
                logger.info(f"{indentlog3}Adding backdrop settings to yaml")
                top_overlay_string += f"{indent3}back_color: \"{get_with_defaults(top_overlay_settings, 'back_color', 'back_color')}\"\n"
                top_overlay_string += f"{indent3}back_width: {get_with_defaults(top_overlay_settings, 'back_width', 'back_width')}\n"
                top_overlay_string += f"{indent3}back_height: {get_with_defaults(top_overlay_settings, 'back_height', 'back_height')}\n"
                top_overlay_string += f"{indent3}back_radius: {get_with_defaults(top_overlay_settings, 'back_radius', 'back_radius')}\n"

            else:
                logger.info(f"{indentlog2}'use_backdrop' set to 'false'")
                logger.info(f"{indentlog3}Removing backdrop settings from 'Movie New Release' yaml.")
            
            top_overlay_string += f"""
overlays:
  
  Netflix Top 10:
    variables: {{key: netflix, weight: 60}}
    template: [name: Top 10 Overlay]
    trakt_list:
      - https://trakt.tv/users/navino16/lists/netflix-united-states-top10-with-united-kingdom-fallback

  Disney Top 10:
    variables: {{key: disney, weight: 50}}
    template: [name: Top 10 Overlay]
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/disney-world-top10-without-fallback

  HBO Max Top 10:
    variables: {{key: hbomax, weight: 40}}
    template: [name: Top 10 Overlay]
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/hbo-max-united-states-top10-with-united-kingdom-fallback

  Hulu Top 10:
    variables: {{key: hulu, weight: 30}}
    template: [name: Top 10 Overlay]
    trakt_list: 
      -  https://trakt.tv/users/navino16/lists/hulu-united-states-top10-with-world-fallback 

  Paramount Top 10:
    variables: {{key: paramount, weight: 20}}
    template: [name: Top 10 Overlay]
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/paramount-plus-united-states-top10-with-united-kingdom-fallback
    
  Prime Top 10:
    variables: {{key: prime, weight: 10}}
    template: [name: Top 10 Overlay]
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/amazon-prime-united-states-top10-with-united-kingdom-fallback
    
  Apple Top 10:
    variables: {{key: apple, weight: 9}}
    template: [name: Top 10 Overlay]
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/apple-tv-united-states-top10-with-united-kingdom-fallback

  Starz Top 10:
    variables: {{key: starz, weight: 8}}
    template: [name: Top 10 Overlay]
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/starz-united-states-top10-with-united-kingdom-fallback
"""
            
########################
# Top 10 Overlay Write #
########################

            top_10_save_folder = top_overlay_settings.get('overlay_save_folder')
            save_folder = top_10_save_folder
            file_name = 'overlay-top10.yml'
            name = 'Top 10 Overlay'

            write_yaml_file(config_directory, save_folder, name, file_name, top_overlay_string)

        else:
            logger.info(f"{indentlog2}'top_10_overlay' set to false. 'top_10' overlay not created")
            logger.info("")
            
    except Exception as e:
        logger.error(f"An error occurred while creating 'Top 10 Overlay' file: {e}")

#####################
# Top 10 Collection #
#####################

def create_top10_collection_yaml(config_directory):
    try:
        settings = load_settings(config_directory, log_message=False)
        
        top_collection_settings = settings.get('top_10', {}).get('top_10_collection', {})

        if get_with_defaults(top_collection_settings, "use", "top_collection_use"):
            logger.info(f"{indentlog}'top_10_collection' 'use:' set to true. Creating 'top_10' collection.")

            top_collection_string = f"""# Top 10 Collection
templates:
  Top 10:
    collection_order: custom
    collection_mode: default
    sort_title: "{get_with_defaults(top_collection_settings, 'sort_title_prefix', 'top_sort_title')}_<<collection_name>>"
    sync_mode: sync
    url_poster: <<poster>>
    visible_home: {get_with_defaults(top_collection_settings, 'visible_home', 'top_visible_home').lower()}
    visible_shared: {get_with_defaults(top_collection_settings, 'visible_shared', 'top_visible_shared').lower()}
    visible_library: {get_with_defaults(top_collection_settings, 'visible_library', 'top_visible_library').lower()}
    summary: "Movies/shows currently in the <<collection_name>>."
    minimum_items: {get_with_defaults(top_collection_settings, 'minimum_items', 'top_minimum_items')}
    delete_below_minimum: {get_with_defaults(top_collection_settings, 'delete_below_minimum', 'top_delete_below_minimum').lower()}
    ignore_blank_results: true
    
collections:
  Netflix Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/netflix_top.jpg}}
    trakt_list:
      - https://trakt.tv/users/navino16/lists/netflix-united-states-top10-with-united-kingdom-fallback

  HBO Max Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/max_top.jpg}}
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/hbo-max-united-states-top10-with-united-kingdom-fallback

  Prime Video Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/prime_top.jpg}}
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/amazon-prime-united-states-top10-with-united-kingdom-fallback

  Paramount+ Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/paramount_top.jpg}}
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/paramount-plus-united-states-top10-with-united-kingdom-fallback

  Hulu Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/hulu_top.jpg}}
    trakt_list: 
      -  https://trakt.tv/users/navino16/lists/hulu-united-states-top10-with-world-fallback

  Disney+ Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/disney_top.jpg}}
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/disney-world-top10-without-fallback

  Starz Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/starz_top_10.jpg}}
    trakt_list:
      - https://trakt.tv/users/navino16/lists/starz-united-states-top10-with-united-kingdom-fallback

  Apple TV+ Top 10:
    template: {{name: Top 10, poster: https://raw.githubusercontent.com/kometa-team/Default-Images/master/chart/color/apple_top.jpg}}
    trakt_list: 
      - https://trakt.tv/users/navino16/lists/apple-tv-united-states-top10-with-united-kingdom-fallback

"""

###########################
# Top 10 Collection Write #
###########################

            collection_save_folder = top_collection_settings.get('collection_save_folder')
            save_folder = collection_save_folder
            file_name = 'collection-top10.yml'
            name = 'Top 10 Collection'

            write_yaml_file(config_directory, save_folder, name, file_name, top_collection_string)

        else:
            logger.info(f"{indentlog2}'top_10_collection' set to false. 'top_10_collection' not created")
            logger.info("")
            
    except Exception as e:
        logger.error(f"An error occurred while creating 'Top 10 Collection' file: {e}")

############################
# Create Streaming Overlay #
############################

def create_streaming_yaml(config_directory):
    try:
        settings = load_settings(config_directory, log_message=False)

        libraries = settings.get('libraries', {})

        streaming_settings = settings.get('streaming_overlay', {})
        use_streaming = streaming_settings.get('use', 'streaming_overlay_use')

        image_size = streaming_settings.get("streaming_image_size", "default")  # "default" or "small"
        gradient = streaming_settings.get("logo_with_gradient", False)
        black_backing = streaming_settings.get("logo_with_black_backing", False)
        if gradient and black_backing:
            raise ValueError("Only one of 'logo_with_gradient' or 'logo_with_black_backing' can be True.")
        
        suffix = ""

        if gradient:
            suffix = "-gradient"
        elif black_backing:
            suffix = "-black"

        if image_size == "small":
            suffix = f"{suffix}-small" if suffix else "-small"
                
        use_extra_streaming = streaming_settings.get('use_extra_streaming', False)
        default_streaming_services = streaming_settings.get('streaming_services', {}).get('default_streaming', {})
        extra_streaming_services = streaming_settings.get('streaming_services', {}).get('extra_streaming', {})

        tmdb_keys = {
            'Netflix': '8', 'AppleTV': '350', 'Disney': '337', 'HBO Max': '1899|1825', 'Prime': '9',
            'Crunchyroll': '283|1968', 'YouTube': '188', 'Hulu': '15', 'Paramount': '531|2303|1770|1853|582|633',
            'Peacock': '386|387', 'Crave': '230', 'Discovery+': '510|520|1708|524|584', 'NOW': '39', 'All 4': '103',
            'BritBox': '151', 'BET+': '1759', 'AMC+': '80|526|1854|528|635', 'Freevee': '613',
            'FuboTV': '257', 'FXNOW': '123', 'Hoopla': '212', 'MGM+': '34|636', 'Starz': '43|1855|634|1794',
            'TBS': '506', 'TNT': '363', 'truTV': '507', 'tubiTV': '73', 'USA': '322'
}
        if use_streaming:
            for library_name, library_settings in libraries.items():
                is_anime = get_with_defaults(library_settings, 'is_anime', 'is_anime')
                use_watch_region = get_with_defaults(library_settings, 'use_watch_region', 'use_watch_region')
                use_vote_count = get_with_defaults(streaming_settings, 'use_vote_count', 'use_vote_count')
                logger.info(f"{indentlog}Creating Streaming template YAML for {library_name}.")

                streaming_string = f"""# {library_name} Streaming Overlay
templates:
  streaming:
    overlay:
      name: <<overlay_name>>
      file: "{get_with_defaults(streaming_settings, 'streaming_image_folder', 'streaming_image_folder', config_directory)}/<<key>>{suffix}.png"
      group: ICONS
      weight: <<weight>>
      horizontal_align: {get_with_defaults(streaming_settings, 'horizontal_align', 'streaming_horizontal_align')}
      vertical_align: {get_with_defaults(streaming_settings, 'vertical_align', 'streaming_veritcal_align')}
      horizontal_offset: {get_with_defaults(streaming_settings, 'horizontal_offset', 'streaming_horizontal_offset')}
      vertical_offset: {get_with_defaults(streaming_settings, 'vertical_offset', 'streaming_vertical_offset')}
"""
                use_backdrop = get_with_defaults(streaming_settings, 'use_backdrop', 'use_backdrop')
                if use_backdrop:
                    logger.info(f"{indentlog2}'use_backdrop' set to 'true'")
                    logger.info(f"{indentlog3}Adding backdrop settings to yaml")
                    streaming_string += f"{indent3}back_color: \"{get_with_defaults(streaming_settings, 'back_color', 'streaming_back_color')}\"\n"
                    streaming_string += f"{indent3}back_width: {get_with_defaults(streaming_settings, 'back_width', 'streaming_back_width')}\n"
                    streaming_string += f"{indent3}back_height: {get_with_defaults(streaming_settings, 'back_height', 'streaming_back_height')}\n"
                    streaming_string += f"{indent3}back_radius: {get_with_defaults(streaming_settings, 'back_radius', 'streaming_back_radius')}\n"

                else:
                    logger.info(f"{indentlog2}'use_backdrop' set to 'false'")
                    logger.info(f"{indentlog3}Removing backdrop settings from 'Streaming' yaml.")
            
                streaming_string += f"""{indent2}ignore_blank_results: {get_with_defaults(streaming_settings, 'ignore_blank_results', 'streaming_ignore_blank_results').lower()}
    tmdb_discover:
      with_watch_providers: <<tmdb_key>>
"""
                if use_watch_region:
                    logger.info(f"{indentlog2}'watch_region' set to 'true'")
                    logger.info(f"{indentlog3}Adding 'watch_region: {get_with_defaults(streaming_settings, 'watch_region', 'streaming_watch_region')}'.")
                    logger.info(f"{indentlog3}Adding 'with_watch_monetization_type: {get_with_defaults(streaming_settings, 'with_watch_monetization_types', 'streaming_with_watch_monetization_types')}'.")
                    streaming_string += f"{indent3}watch_region: {get_with_defaults(streaming_settings, 'watch_region', 'streaming_watch_region')}\n"
                    streaming_string += f"{indent3}with_watch_monetization_types: {get_with_defaults(streaming_settings, 'with_watch_monetization_types', 'streaming_with_watch_monetization_types')}\n"

                else:
                    logger.info(f"{indentlog2}'watch_region' set to 'false'")
                    logger.info(f"{indentlog3}Removing 'watch_region'.")
                    logger.info(f"{indentlog3}Removing 'with_watch_monetizaion_types'.")
            
                if not is_anime:
                    logger.info(f"{indentlog2}'is_anime' set to 'false'")
                    logger.info(f"{indentlog3}Adding 'with_original_language: {get_with_defaults(streaming_settings, 'with_original_language', 'streaming_with_original_language')}'.")
                    streaming_string += f"{indent3}with_original_language: {get_with_defaults(streaming_settings, 'with_original_language', 'streaming_with_original_language')}\n"

                else:
                    logger.info(f"{indentlog2}'is_anime' set to 'true'")
                    logger.info(f"{indentlog3}Removing 'with_original_language'.")

                streaming_string += f"{indent3}limit: <<limit>>\n"

                if use_vote_count:
                    logger.info(f"{indentlog2}'use_vote_count' set to 'true'")
                    logger.info(f"{indentlog3}Adding 'vote_count.gte: {get_with_defaults(streaming_settings, 'vote_count', 'vote_count')}'.")
                    streaming_string += f"{indent3}vote_count.gte: {get_with_defaults(streaming_settings, 'vote_count', 'vote_count')}\n"

                streaming_string += f"{indent3}sort_by: popularity.desc\n"

                logger.info(f"{indentlog}Streaming template created")
                logger.info(f"{indentlog}Creating streaming overlays")

                plex_fallback_string = f"""\noverlays:\n
# Plex Fallback #
  Plex Fallback Overlay:
    overlay:
      name: plex
      file: "{get_with_defaults(streaming_settings, 'streaming_image_folder', 'streaming_image_folder', config_directory)}/Plex{suffix}.png"
      group: ICONS
      weight: 15
      horizontal_align: {get_with_defaults(streaming_settings, 'horizontal_align', 'streaming_horizontal_align')}
      vertical_align: {get_with_defaults(streaming_settings, 'vertical_align', 'streaming_veritcal_align')}
      horizontal_offset: {get_with_defaults(streaming_settings, 'horizontal_offset', 'streaming_horizontal_offset')}
      vertical_offset: {get_with_defaults(streaming_settings, 'vertical_offset', 'streaming_vertical_offset')}
"""
                if use_backdrop:
                    logger.info(f"{indentlog2}'use_backdrop' set to 'true'")
                    logger.info(f"{indentlog3}Adding backdrop settings to yaml")
                    plex_fallback_string += f"{indent3}back_color: \"{get_with_defaults(streaming_settings, 'back_color', 'streaming_back_color')}\"\n"
                    plex_fallback_string += f"{indent3}back_width: {get_with_defaults(streaming_settings, 'back_width', 'streaming_back_width')}\n"
                    plex_fallback_string += f"{indent3}back_height: {get_with_defaults(streaming_settings, 'back_height', 'streaming_back_height')}\n"
                    plex_fallback_string += f"{indent3}back_radius: {get_with_defaults(streaming_settings, 'back_radius', 'streaming_back_radius')}\n"

                else:
                    logger.info(f"{indentlog2}'use_backdrop' set to 'false'")
                    logger.info(f"{indentlog3}Removing backdrop settings from 'Streaming' yaml.")
            
                plex_fallback_string += f"""{indent2}ignore_blank_results: {get_with_defaults(streaming_settings, 'ignore_blank_results', 'streaming_ignore_blank_results').lower()}
    plex_all: true
"""
                streaming_string += plex_fallback_string

                streaming_string += f"""
# Streaming #
    # Same as Kometa Default Streaming #
"""
                for service, service_settings in default_streaming_services.items():
                    if service_settings.get('use', True):
                        limit = service_settings.get('limit', 1500)
                        weight = service_settings.get('weight', 100)
                        tmdb_key = tmdb_keys.get(service, '<<tmdb_key>>')
                        streaming_string += f"""
  {service}:
    variables: {{key: {service}, tmdb_key: {tmdb_key}, weight: {weight}, limit: {limit}}}
    template: {{name: streaming}}
"""
                if use_extra_streaming:
                    for service, service_settings in extra_streaming_services.items():
                        if service_settings.get('use', True):
                            limit = service_settings.get('limit', 1500)
                            weight = service_settings.get('weight', 100)
                            tmdb_key = tmdb_keys.get(service, '<<tmdb_key>>')
                            streaming_string += f"""
  {service}:
    variables: {{key: {service}, tmdb_key: {tmdb_key}, weight: {weight}, limit: {limit}}}
    template: {{name: streaming}}
"""
            
############################
#  Write Streaming YAML   #
############################

                streaming_save_folder = streaming_settings.get('streaming_save_folder')
                save_folder = streaming_save_folder
                normalized_library_name = library_name.lower().replace(' ', '-')
                file_name = f"overlay-streaming-{normalized_library_name}.yml"
                name = 'Streaming Overlay'

                write_yaml_file(config_directory, save_folder, name, file_name, streaming_string)

        else:
            logger.info(f"{indentlog}'Streaming Overlay' set to false. 'Streaming Overlay' not created")
            logger.info("")

    except Exception as e:
        logger.error(f"An error occurred while generating 'Streaming Overlay' files: {e}")
