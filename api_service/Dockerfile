# This Dockerfile builds the API service container.
# It starts from a PyTorch runtime image, installs dependencies,
# sets PYTHONPATH for module discovery, and runs the API with Uvicorn.

FROM pytorch/pytorch:2.5.1-cuda11.8-cudnn9-runtime

# Set environment variables to avoid bytecode and ensure unbuffered output.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Ensure Python can find modules under /app/src by setting PYTHONPATH.
ENV PYTHONPATH=/app/src

# Set the working directory inside the container.
WORKDIR /app

# Install required system dependencies for building and image processing.
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application source code into /app/src.
# IMPORTANT: Ensure that __init__.py files exist in each directory inside src
# (domain, infrastructure, application, interface) so Python treats them as packages.
COPY src/ ./src/

# Expose metrics and API ports.
EXPOSE 8002
EXPOSE 8080

# Run the application using Uvicorn.
# 'interface.api:app' should point to the FastAPI app object in interface/api.py.
CMD ["uvicorn", "interface.api:app", "--host", "0.0.0.0", "--port", "8080"]
