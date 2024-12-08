#!/bin/bash
set -e

# Step 1: Start core infrastructure services
echo "Starting core infrastructure services..."
docker-compose up --build -d postgres redis rabbitmq elasticsearch prometheus
echo "Core infrastructure services started."

# Step 2: Start monitoring and admin tools
echo "Starting monitoring and admin tools..."
docker-compose up --no-recreate -d grafana redis_exporter redis-commander rabbitmq_exporter postgres_exporter pgadmin
echo "Monitoring and admin tools started."

# Step 3: Start application services
echo "Starting application services..."
docker-compose up --no-recreate -d downloader embedding_generator api frontend
echo "Application services started."

# Step 4: Start frontend
echo "Starting frontend..."
docker-compose up --no-recreate -d frontend
echo "Application frontend started."

# Final message
echo "All services started successfully!"
