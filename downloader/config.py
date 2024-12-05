"""
Configuration for the Image Downloader Service.
Adjust constants as needed.
"""

DATASET_FILE = "image_urls.txt"
OUTPUT_DIR = "./shared_volume/images"
TEMP_DIR = "/tmp/images"
CONCURRENT_REQUESTS = 300
RETRIES = 3
TIMEOUT = 10
BATCH_SIZE = 300
CHUNK_SIZE = 8192
CACHE_EXPIRATION = 3600
