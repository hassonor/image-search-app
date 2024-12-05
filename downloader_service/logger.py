import logging
import os

# Create logs directory if it doesn't exist
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure the logger
logger = logging.getLogger('downloader')
logger.setLevel(logging.DEBUG)

# File handler to write logs to a file
file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'downloader.log'))
file_handler.setLevel(logging.DEBUG)

# Console handler to print logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
