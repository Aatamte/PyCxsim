import os
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_asset_path():
    """
    Get the directory path of the current script.

    Returns:
        str: The directory path of the current script.
    """
    try:
        # Absolute path of the current script
        script_path = os.path.abspath(__file__)
        # Directory containing the script
        return os.path.dirname(script_path)
    except NameError:
        logging.error("Could not determine the script's directory (NameError: __file__ is not defined).")
        sys.exit(1)


ASSET_PATH = get_asset_path()
