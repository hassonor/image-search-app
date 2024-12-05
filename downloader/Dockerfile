FROM python:3.11.9-slim

# Set a working directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the downloader code
COPY config.py downloader.py tests/ ./
COPY image_urls.txt ./

# Create output directories
RUN mkdir -p /app/shared_volume/images && mkdir -p /tmp/images

# Set environment variables if needed
# ENV DATASET_FILE="image_urls.txt" ...

CMD ["python", "downloader.py"]
