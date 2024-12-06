# downloader_service/Dockerfile

# Stage 1: Build
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential gcc

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final Image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Create necessary directories as root
RUN mkdir -p /app/images /app_input

# Create non-root user
RUN adduser --disabled-password --gecos "" downloader

# Change ownership of the work directory and created directories to 'downloader'
RUN chown -R downloader:downloader /app /app/images /app_input

# Expose metrics port
EXPOSE 8000

# Set the entrypoint command
CMD ["python", "src/main.py"]
