# Stage 1: Build Stage
FROM python:3.11.9-slim as build-stage

WORKDIR /app

# Copy requirements first, so installing dependencies can be cached
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download and save the model here to avoid re-downloading at runtime
# This step ensures the model weights are cached in an image layer.
RUN python -c "\
from transformers import CLIPModel, CLIPProcessor; \
model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32'); \
processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32'); \
model.save_pretrained('./clip_model'); \
processor.save_pretrained('./clip_model'); \
print('Model and processor saved to ./clip_model')"

# Stage 2: Final Image
FROM python:3.11.9-slim

WORKDIR /app

# Copy requirements again (if needed) and install.
# This will be cached if requirements.txt hasn't changed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the pre-downloaded model from the build stage
COPY --from=build-stage /app/clip_model /app/clip_model

# Copy your code
COPY embedding_service.py ./

ENV HF_HOME="/app/clip_model"

CMD ["python", "embedding_service.py"]
