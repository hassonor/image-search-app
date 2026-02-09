# Image Search Application

A scalable microservices-based application for text-based image search, featuring efficient deduplication, real-time monitoring, and high performance.

## Overview

The Image Search Application enables users to search images using textual descriptions. It employs a pipeline of microservices for reading URLs, downloading images, generating embeddings, indexing in Elasticsearch, and serving search queries. The system includes comprehensive monitoring, caching, and deduplication strategies.

## Technology Stack

### Backend
- **FastAPI 0.128.6** - Modern, high-performance web framework
- **Pydantic 2.12.5** - Data validation using Python type annotations
- **Elasticsearch 8.19.3** - Vector search and document store
- **Redis 5.2.1** - Caching and deduplication
- **PostgreSQL** - Metadata storage
- **RabbitMQ** - Message queue for async processing
- **Prometheus & Grafana** - Monitoring and metrics
- **PyTorch & CLIP** - Deep learning embeddings
- **pytest 8.3.5** - Testing framework

### Frontend
- **React 18.3.1** - UI framework
- **TypeScript 5.7.3** - Type-safe JavaScript
- **Material-UI (MUI) 6.3.1** - Component library
- **React Testing Library 16.1.0** - Testing utilities

### DevOps
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD pipeline

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

- **React 18.3** with TypeScript 5.7
- **Material-UI (MUI) v6** for modern UI components
- Text-based search interface with real-time results
- Theme toggling (dark/light mode)
- Image browsing with modal view and navigation
- Comprehensive test coverage with React Testing Library

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend development)

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
  - Fast and accurate text-to-image retrieval using CLIP embeddings
  - Semantic search powered by OpenAI's CLIP model

- **Scalable & Asynchronous Processing**
  - RabbitMQ-based distributed task processing
  - Horizontal scaling capability
  - Async/await patterns throughout the stack

- **Advanced Deduplication**
  - Two-layer protection using Bloom filter and Redis
  - Prevents duplicate processing and saves resources

- **Comprehensive Monitoring**
  - Prometheus metrics collection
  - Grafana dashboards
  - Performance and resource usage tracking

- **Modern Technology Stack**
  - FastAPI 0.128+ for high-performance APIs
  - Pydantic v2 for robust data validation
  - Elasticsearch 8.19+ for vector search
  - React 18 with Material-UI v6 for modern UI

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

### Backend Tests

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

### Frontend Tests

The frontend includes comprehensive tests for all major components:

```bash
cd frontend_service
npm test
```

Test coverage includes:
- **App.test.tsx**: Main application flow and state management
- **SearchBar.test.tsx**: Search input, form submission, and validation
- **ImageGrid.test.tsx**: Image display, loading states, and error handling

Run tests with coverage:
```bash
npm test -- --coverage
```

## Development

### Environment Variables

All services use environment-based configuration powered by Pydantic v2 Settings.

Configuration files are located in each service:
- `api_service/src/infrastructure/config.py`
- `downloader_service/src/infrastructure/config.py`
- `embedding_service/src/infrastructure/config.py`
- `file_reader_service/src/infrastructure/config.py`

**Note**: In Pydantic v2, field names automatically map to environment variables. For example, `LOG_LEVEL` field reads from the `LOG_LEVEL` environment variable, with default values used if not set.

Copy `.env.example` to `.env` and customize as needed:
```bash
cp .env.example .env
```

### Local Development Setup

1. **Backend Development**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies for a specific service
   pip install -r api_service/requirements.txt
   ```

2. **Frontend Development**:
   ```bash
   cd frontend_service
   npm install
   npm start  # Runs on http://localhost:3000
   ```

3. **Running with Docker**:
   ```bash
   docker-compose up --build
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass (`./run_all_tests.sh`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Create a new Pull Request

### Code Quality

- Python code follows PEP 8 style guide
- All services maintain 80%+ test coverage
- Type hints are used throughout the codebase
- Frontend uses ESLint and Prettier for code formatting

## License

MIT License

Copyright (c) 2025 Or Hasson
