# Image Search Application

## Setup and Installation (Tested On Win11)
### Prerequisites
Ensure the following dependencies are installed on your machine:

* **Docker**
* **Docker Compose**
* **Python 3.7+**
* **RabbitMQ, Redis, Elasticsearch, Postgres, Prometheus, Grafana (via Docker Compose)**


1. Build and Start the Services
Using Docker Compose, you can build and start all the necessary services (**PLEASE NOTE: First run will take about 10 minutes + Run One by One the order matters.**) 
* Run the following script: `run_and_install.sh` On the sub folder: `./scripts/run_and_install.sh`.
* If you want to clean all docker and downloaded images environment first run: `reset.sh` on the sub folder: `./scripts/reset.sh`
   
2. Access the Services
* API Service: `http://localhost:8080`
* Prometheus: `http://localhost:9090` (Username: `admin@admin.com`, Password: `admin`)
* Grafana: `http://localhost:3000` (Username: `admin`, Password: `newpassword`)
* RabbitMQ UI Management: `http://localhost:15672` (Username: `guest`, Password: `guest`)
* RedisCommander (View Redis): `http://localhost:8081/`
* PgAdmin (View PostgreSQL): `` (Username: `admin@admin.com`, password: `admin`) 
  * First Login need to add the db: 
    * Right click on mouse when focus `Servers`
    * Register
    * Server
    * Add Server Name: e.g. `Images`
    * Go to `Connection` Tab
    * Host Name: `postgres`, Maintenance database: `mydb`, Username: `myuser`, Password: `mypassword`

3. Test the Application 
Use the API to test the image search functionality by sending queries to the `GET /get_image` endpoint.
Example:
```bash
curl "http://localhost:8080/get_image?query_string=beautiful+landscape" 
```


## Overview
**The Image Search Application** is a powerful solution that provides users the
ability to search for images based on text queries.
The application utilizes advanced embedding generation techniques, 
integrates multiple services for efficient image retrieval, 
and supports real-time data processing with asynchronous services. 
It includes robust monitoring with **Prometheus** and **Grafana** 
for system performance and metrics visualization.

## Architecture
The application leverages several microservices, including:

* **API Service (FastAPI)**: 
Handles user queries, metrics collection, and Elasticsearch search for similar images.
* **Downloader Service:** Manages the downloading and storage of images, utilizing a RabbitMQ
queue for task distribution.
* **Embedding Generator Service:** Generates and indexes image embeddings using CLIP-based models.
* **RabbitMQ:** Facilitates communication between services with two primary queues - one for image downloads and one for embedding generation.
* **Redis:** Caches previously seen URLs for deduplication purposes.
* **Elasticsearch:** Stores image embeddings and allows efficient querying based on cosine similarity for image search.
* **Postgres:** Stores image metadata, including URL and download information.
* **Prometheus** and Grafana: Collect and visualize system metrics for monitoring.


## Features
* **Real-time Image Search:** Search for images based on text descriptions with the ability to retrieve the most relevant images based on embeddings.
* **Metrics and Monitoring:** Exposes Prometheus metrics and integrates with Grafana for real-time monitoring and visualization of system health.
* **Scalable and Asynchronous Processing:** Uses RabbitMQ for distributed task processing, making the image downloading and embedding generation scalable and efficient.
* **Caching:** Redis-based Bloom Filter to prevent redundant downloads and ensure optimal performance.
* **Dockerized Services:** All services are containerized using Docker, making it easy to deploy and manage the application.

## Metrics
Prometheus will scrape metrics from the services, including:

* **API Service metrics**
* **Downloader Service metrics**
* **Embedding Generator metrics**
* **Elasticsearch metrics**
* **Postgres metrics**
* **Redis metrics**

These metrics can be visualized in **Grafana**, where you can create dashboards to monitor system health, performance, and resource usage.

## Docker Compose Services
The following services are defined in `docker-compose.yml`:

* **api**: FastAPI service that serves the main application.
* **downloader**: Asynchronous image downloader service.
* **embedding_generator**: Embedding generation service based on the CLIP model.
* **rabbitmq**: Message queue service for inter-service communication.
* **elasticsearch**: Stores image embeddings.
* **postgres**: Stores image metadata.
* **redis**: Cache service for deduplication.
* **prometheus**: Collects metrics from services.
* **grafana**: Visualizes system metrics.

