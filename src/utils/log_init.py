import logging
import logging.config
import os

import yaml


def initialize_logs(name):
    """Initialize logging using the configuration file."""

    # Create the 'logs' folder at the project root if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Load logging configuration from YAML file
    stream = open("logging_config.yml", encoding="utf-8")
    config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

    # Log the start of the program
    logging.info("-" * 50)
    logging.info(f"Starting {name}")
    logging.info("-" * 50)
