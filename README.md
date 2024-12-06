# Image Search Application

## Overview

The Image Search Application allows users to search for images based on textual queries. It processes a dataset of image URLs, generates embeddings for each image using a pre-trained model, indexes these embeddings in Elasticsearch, and provides a user interface for searching and displaying relevant images.

## Architecture

![Architecture Diagram](./docs/architecture_diagram.png)

## Components

1. **Image Downloader Service:** Downloads images from provided URLs and stores them in a shared volume. Publishes messages to RabbitMQ indicating new images are ready for embedding generation.

2. **Embedding Generator Service:** Consumes messages from RabbitMQ, generates embeddings using CLIP, and indexes them in Elasticsearch.

3. **Elasticsearch Service:** Acts as the vector database, storing and indexing embedding vectors for efficient similarity searches.

4. **User Interface Service:** Provides an API for users to input search queries, converts them into embeddings, queries Elasticsearch, and returns relevant image URLs.

5. **Monitoring Services:** Prometheus and Grafana are set up for comprehensive monitoring and visualization of metrics.

## Getting Started

### Prerequisites

- **Docker:** Ensure Docker is installed on your machine.
- **Docker Compose:** Install Docker Compose for orchestrating multi-container Docker applications.

### Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/image-search-app.git
   cd image-search-app

2. Environment Configuration:

Create a .env file in the root directory with the following content:
```bash 
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s [%(levelname)s] %(name)s: %(message)s

# Downloader Settings
DOWNLOAD_TIMEOUT=30
USER_AGENT=MyImageDownloader/1.0
BLOOM_EXPECTED_ITEMS=10000000
BLOOM_ERROR_RATE=0.0001
NUM_CONSUMERS=4

# PostgreSQL Settings
PG_USER=myuser
PG_PASSWORD=mypassword
PG_DATABASE=mydb
PG_HOST=postgres
PG_PORT=5432

# Redis Settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# RabbitMQ Settings
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Queue Names
DOWNLOAD_QUEUE=image_downloads
EMBEDDING_QUEUE=image_embeddings

# Storage Paths
IMAGE_STORAGE_PATH=/app/images
```
Note: Adjust the environment variables as needed, especially passwords and host configurations.

3. Prepare Image URLs:

* Place your image URLs in downloader_service/image_urls.txt. Each URL should be on a separate line.

4. Build and Start Services:
`docker-compose up --build`

* Note: This command builds the Docker images and starts all services defined in docker-compose.yml.

5. Access Services:

RabbitMQ Management UI: http://localhost:15672

Username: guest
Password: guest
Prometheus Metrics: http://localhost:9090

Grafana Dashboard: http://localhost:3000

Username: admin
Password: newpassword (as set in docker-compose.yml)
User Interface/API Service: http://localhost:8080

PgAdmin: http://localhost:5050

Email: admin@admin.com
Password: admin

6. Testing the workflow:
7. Testing the Workflow:

Image Downloading:

Ensure that the Downloader Service is consuming URLs from image_urls.txt and downloading images to shared_volume/images/.
Embedding Generation:

After images are downloaded, the Embedding Generator Service consumes messages from RabbitMQ, generates embeddings, and indexes them in Elasticsearch.
Search Queries:

Use the User Interface Service to input search queries and retrieve relevant images.


API Endpoints
1. Get Image by Query
Endpoint: GET /get_image

Parameters:

query_string (string): The textual query to search for images.
Response:

Returns a list of images matching the query with their URLs and similarity scores.
* Example Request:
`curl "http://localhost:8080/get_image?query_string=Bathroom"`


* Example Request:
`[
  {
    "image_id": 1,
    "image_url": "/app/images/cca2fd83a06cee9f3d4c798e5ea9a20a458b837c8a6adba061aca3f5101c1e3c.jpg",
    "score": 1.95
  },
  {
    "image_id": 2,
    "image_url": "/app/images/bb3a4f1d0f3b9f4c7e8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0i1j2.jpg",
    "score": 1.85
  }
]
`
* Example Response:
`[
  {
    "image_id": 1,
    "image_url": "/app/images/cca2fd83a06cee9f3d4c798e5ea9a20a458b837c8a6adba061aca3f5101c1e3c.jpg",
    "score": 1.95
  },
  {
    "image_id": 2,
    "image_url": "/app/images/bb3a4f1d0f3b9f4c7e8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0i1j2.jpg",
    "score": 1.85
  }
]
`
