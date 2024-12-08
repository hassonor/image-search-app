#!/bin/bash
set -e

echo "Starting core infrastructure services..."
docker-compose up --build -d postgres redis rabbitmq elasticsearch prometheus || { echo "Failed to start core infra services."; exit 1; }
echo "Core infrastructure services started."

echo "Starting monitoring and admin tools..."
docker-compose up --no-recreate -d grafana redis_exporter redis-commander rabbitmq_exporter postgres_exporter pgadmin || { echo "Failed to start monitoring tools."; exit 1; }
echo "Monitoring and admin tools started."

echo "Starting application services..."
docker-compose up --no-recreate -d downloader embedding_generator api frontend || { echo "Failed to start application services."; exit 1; }
echo "Application services started."



echo "All services started successfully!"
