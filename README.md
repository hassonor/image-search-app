# Image Search Application

A scalable microservices-based application for text-based image search, featuring efficient deduplication, real-time monitoring, and high performance.

## Overview

The Image Search Application enables users to search images using textual descriptions. It employs a pipeline of microservices for reading URLs, downloading images, generating embeddings, indexing in Elasticsearch, and serving search queries. The system includes comprehensive monitoring, caching, and deduplication strategies.

## Architecture

### Backend Services

- **API Service (FastAPI)**
  - Handles user queries
  - Interacts with Elasticsearch for image retrieval

- **File Reader Service**
  - Reads image URLs from files
  - Implements "double protection" deduplication:
    - Bloom filter for quick duplicate detection
    - Redis for definitive state verification

- **Downloader Service**
  - Consumes URLs from RabbitMQ
  - Downloads images
  - Stores metadata in PostgreSQL
  - Publishes embedding tasks

- **Embedding Generator Service**
  - Generates CLIP-based embeddings
  - Stores embeddings in Elasticsearch

### Infrastructure

- **RabbitMQ**
  - Download Queue for new image URLs
  - Embedding Queue for embedding generation tasks

- **Redis**
  - URL processing state cache
  - Deduplication verification

- **Elasticsearch**
  - Stores image embeddings
  - Enables similarity-based search

- **PostgreSQL**
  - Stores image metadata
  - Tracks processing status

- **Prometheus & Grafana**
  - System metrics collection
  - Performance monitoring
  - Health checks

### Frontend

- React-based UI
- Text-based search interface
- Theme toggling (dark/light mode)
- Image browsing capabilities

## Prerequisites

- Docker
- Docker Compose
- Python 3.7+

## Installation and Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd image-search-application
```

2. Run the installation script:
```bash
./run_and_install.sh
```

To reset the environment:
```bash
./reset.sh
```

## Accessing Services

- Frontend (React): http://localhost:3030
- API Service: http://localhost:8080
- Prometheus: http://localhost:9090
  - Username: admin@admin.com
  - Password: admin
- Grafana: http://localhost:3000
  - Username: admin
  - Password: newpassword
- RabbitMQ Management: http://localhost:15672
  - Username: guest
  - Password: guest
- Redis Commander: http://localhost:8081
- PgAdmin:
  - Username: admin@admin.com
  - Password: admin

### PgAdmin Database Configuration

1. Log in to PgAdmin
2. Right-click on Servers
3. Select Register > Server
4. Enter server details:
   - Server Name: Images
   - Host Name: postgres
   - Maintenance database: mydb
   - Username: myuser
   - Password: mypassword

## Testing

1. Navigate to http://localhost:3030
2. Use the search bar to perform text-based image searches

API Test:
```bash
curl "http://localhost:8080/get_image?query_string=beautiful+landscape"
```

## Key Features

- **Real-time Image Search**
  - Fast and accurate text-to-image retrieval

- **Scalable & Asynchronous Processing**
  - RabbitMQ-based distributed task processing
  - Horizontal scaling capability

- **Advanced Deduplication**
  - Two-layer protection using Bloom filter and Redis
  - Prevents duplicate processing

- **Comprehensive Monitoring**
  - Prometheus metrics collection
  - Grafana dashboards
  - Performance and resource usage tracking

## Docker Compose Services

- api
- file_reader
- downloader
- embedding_generator
- rabbitmq
- elasticsearch
- postgres
- redis
- prometheus
- grafana
- frontend

## Metrics and Monitoring

Prometheus scrapes metrics from:
- API Service
- File Reader Service
- Downloader Service
- Embedding Generator Service
- Elasticsearch
- PostgreSQL
- Redis

Custom Grafana dashboards provide visualization for:
- System performance
- Resource usage
- Service health
- Processing rates

## Running Tests

Each microservice provides **unit**, **integration**, and **end-to-end** suites
under its respective `tests` directory. A helper script runs them all with
coverage enforcement:

```bash
./run_all_tests.sh
```
The script invokes `pytest` for each service using the configuration found in
their respective `pytest.ini` files. Coverage is collected via **pytest-cov**
and a minimum threshold of **80%** is enforced across all suites.

If you want to run a single service's tests manually with coverage, use
`pytest` directly. For example, running the API service tests:

```bash
pytest api_service/tests --cov=api_service/src \
       --cov-report=term-missing --cov-fail-under=80
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT License

Copyright (c) 2025 Or Hasson
