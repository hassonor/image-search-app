import os
from transformers import CLIPProcessor, CLIPModel

# Initialize model and processor
MODEL_NAME = "openai/clip-vit-base-patch32"
model = CLIPModel.from_pretrained(MODEL_NAME)
processor = CLIPProcessor.from_pretrained(MODEL_NAME)

# Save model and processor to local folder
OUTPUT_DIR = "./clip_model"
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR)
processor.save_pretrained(OUTPUT_DIR)

print(f"Model and processor saved to {OUTPUT_DIR}")
