# downloader_service/Dockerfile

# Stage 1: Build
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential gcc git

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

# Create directories and non-root user
RUN mkdir -p /app/images /app_input
RUN adduser --disabled-password --gecos "" downloader
RUN chown -R downloader:downloader /app /app/images /app_input

USER downloader

EXPOSE 8000 8003

CMD ["python", "src/main.py"]
