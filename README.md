# Downloader Service

## Overview

A robust and efficient image downloader service that processes millions of URLs, checks deduplication using Redis and Bloom filters, stores metadata in PostgreSQL, and communicates via RabbitMQ. Metrics are exposed to Prometheus for monitoring.

## Features

- Asynchronous image downloading with `aiohttp`
- Deduplication using Bloom filters and Redis
- Metadata storage in PostgreSQL
- Message queuing with RabbitMQ
- Monitoring with Prometheus and Grafana
- Dockerized setup with `docker-compose`

## Setup

### Prerequisites

- Docker
- Docker Compose

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```dotenv
LOG_LEVEL=INFO
DOWNLOAD_TIMEOUT=30
USER_AGENT=MyImageDownloader/1.0
BLOOM_EXPECTED_ITEMS=10000000
BLOOM_ERROR_RATE=0.0001
NUM_CONSUMERS=4
