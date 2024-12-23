import os
import logging
from collections import OrderedDict
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString
from ruamel.yaml.representer import RoundTripRepresenter

# Initialize YAML handler with specific settings
yaml = YAML()
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.allow_unicode = True
yaml.preserve_quotes = True

# Ensure OrderedDict is used without !!omap tags
yaml.Representer = RoundTripRepresenter
yaml.Representer.add_representer(OrderedDict, RoundTripRepresenter.represent_dict)

logger = logging.getLogger(__name__)

settings_filename = "overlay-settings.yml"

# Custom function to add blank lines between sections and their nestings
def add_blank_lines(yaml_output):
    lines = yaml_output.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        # Add a blank line if the next line is a top-level section or nested element
        if i + 1 < len(lines) and lines[i + 1] and lines[i + 1][0].isalnum() and line and lines[i + 1][0] != '-':
            new_lines.append('')
    return '\n'.join(new_lines)

# Create default settings
settings = OrderedDict({
    "libraries": OrderedDict({
        "TV Shows": {
            "is_anime": False,
            "use_watch_region": True
        },
        "4k TV Shows": {
            "is_anime": False,
            "use_watch_region": True
        },
        "Anime": {
            "is_anime": True,
            "use_watch_region": True
        }
    }),

    "overlay_settings": OrderedDict({
        "days_ahead": 30,
        "overlay_save_folder": None,
        "date_delimiter": DoubleQuotedScalarString("/"),
        "font": None,
        "font_size": 45,
        "font_color": DoubleQuotedScalarString("#FFFFFF"),
        "horizontal_align": "center",
        "vertical_align": "top",
        "horizontal_offset": 0,
        "vertical_offset": 38,
        "back_width": 475,
        "back_height": 55,
        "back_radius": 30,
        "ignore_blank_results": "true",
        "with_status": 0,
        "watch_region": "US",
        "with_original_language": "en",
        "limit": 500,
        "with_watch_monetization_types": "flatrate|free|ads|rent|buy"
    }),

    "use_overlays": OrderedDict({
        "upcoming_series": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#FC4E03"),
            "text": DoubleQuotedScalarString("U P C O M I N G"),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "new_series": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#008001"),
            "text": DoubleQuotedScalarString("N E W  S E R I E S"),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "new_airing_next": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#008001"),
            "text": DoubleQuotedScalarString("N E W - A I R S "),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "airing_series": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#003880"),
            "text": DoubleQuotedScalarString("A I R I N G"),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "airing_today": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#003880"),
            "text": DoubleQuotedScalarString("A I R S  T O D A Y"),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "airing_next": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#003880"),
            "text": DoubleQuotedScalarString("A I R I N G "),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "ended_series": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#000000"),
            "text": DoubleQuotedScalarString("E N D E D"),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "canceled_series": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#CF142B"),
            "text": DoubleQuotedScalarString("C A N C E L E D"),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "returning_series": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#103197"),
            "text": DoubleQuotedScalarString("R E T U R N I N G"),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        },
        "returns_next": {
            "use": True,
            "back_color": DoubleQuotedScalarString("#103197"),
            "text": DoubleQuotedScalarString("R E T U R N S "),
            "font_color": DoubleQuotedScalarString("#FFFFFF")
        }
    }),

    "returning_soon_collection": OrderedDict({
        "use": True,
        "collection_save_folder": None,
        "poster_source": "url",
        "poster_path": None,
        "visible_home": "true",
        "visible_shared": "true",
        "summary": DoubleQuotedScalarString("TV Shows returning soon!"),
        "minimum_items": 1,
        "delete_below_minimum": "true",
        "sort_title": DoubleQuotedScalarString("!010_Returning")
    })
})

def create_settings_file(main_directory, run_now, run_now_env, in_docker):
    # Create the settings.yaml file in the same directory as the script.
    settings_file_path = os.path.join(main_directory, settings_filename)

    try:
        logger.info(f"Settings file not found at '{settings_file_path}', creating a default settings file.")
        with open(settings_file_path, 'w') as file:
            yaml.dump(settings, file)
        # Reopen the file to add blank lines between sections
        with open(settings_file_path, 'r+') as file:
            yaml_output = file.read()
            formatted_output = add_blank_lines(yaml_output)
            file.seek(0)
            file.write(formatted_output)
            file.truncate()
        logger.info(f"Created settings file at '{settings_file_path}'")
        
        if in_docker and not (run_now or run_now_env):
            logger.info("Please edit the 'overlay-settings.yml' to your liking. Overlays will be created at scheduled run.")
            logger.info("If you would like to create overlays now, set RUN_NOW to True in your compose file and restart the container or complete a manual run.")

        if in_docker and (run_now or run_now_env):
            logger.info("Please edit the 'overlay-settings.yml' to your liking. Restart the container to create overlays now.")

        if not in_docker:
            logger.info("Please edit the 'overlay-settings.yml' to your liking. Run the script again to create overlays.")
                    
    except Exception as e:
        logger.error(f"Error creating settings file: {e}")

def load_settings(main_directory, log_message=True):
    # Load the settings.yaml file. If it doesn't exist, create it.
    settings_file_path = os.path.join(main_directory, settings_filename)

    if not os.path.exists(settings_file_path):
        logger.info(f"Settings file not found at '{settings_file_path}', creating a new one.")
        create_settings_file(main_directory)

    try:
        with open(settings_file_path, 'r') as file:
            if log_message:
                logger.info(f"Loading settings from '{settings_file_path}'")
            return yaml.load(file)
    
    except Exception as e:
        logger.error(f"Error loading settings file: {e}")
        raise  # Re-raise exception after logging

def update_dict(existing, defaults):
    updated = OrderedDict()

    for key, value in defaults.items():
        if key == "libraries":  # Skip updating libraries section
            if key in existing:
                updated[key] = existing[key]
            continue

        if key in existing:
            if isinstance(value, dict):
                updated[key] = update_dict(existing[key], value)
            else:
                updated[key] = existing[key]
        else:
            updated[key] = value

    # Add any leftover keys from existing that are not in defaults
    for key, value in existing.items():
        if key not in updated:
            updated[key] = value

    return updated

def update_settings_file(main_directory):
    settings_file_path = os.path.join(main_directory, settings_filename)
    
    try:
        logger.info("Checking settings file for missing or new updated sections...")
        existing_settings = load_settings(main_directory, log_message=False)
        
        # Update existing settings with default settings, but skip libraries section
        updated_settings = update_dict(existing_settings, settings)
        
        # Check if there are any updates to the settings
        if existing_settings != updated_settings:
            # Save the updated settings back to the file
            with open(settings_file_path, 'w') as file:
                yaml.dump(updated_settings, file)
            # Reopen the file to add blank lines between sections
            with open(settings_file_path, 'r+') as file:
                yaml_output = file.read()
                formatted_output = add_blank_lines(yaml_output)
                file.seek(0)
                file.write(formatted_output)
                file.truncate()
                
            logger.info(f"Updated settings file at '{settings_file_path}' with missing sections")
        else:
            logger.info(f"No updates were made to the settings file at '{settings_file_path}'")
            
    except Exception as e:
        logger.error(f"Error updating settings file: {e}")
