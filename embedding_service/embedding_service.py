import os
import json
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm

from embedding_service import config
from embedding_service.logger import get_logger

# Get the logger instance from logger.py
logger = get_logger()

# Use the variables from the config file
IMAGES_DIR = config.IMAGES_DIR
OUTPUT_FILE = config.OUTPUT_FILE

class EmbeddingGenerator:
    def __init__(self, model_path="/app/clip_model"):
        """
        Initialize the embedding generator with a pre-trained model.
        If the model is already downloaded and available locally, we use it directly.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading model from {model_path} on {self.device}")
        self.model = CLIPModel.from_pretrained(model_path).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_path)

    def generate_embeddings_for_image(self, image_path):
        """
        Generate embeddings for a single image.
        This method is directly tested and also used by generate_all_embeddings.
        """
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                embeddings = self.model.get_image_features(**inputs)
            return embeddings.squeeze().cpu().tolist()
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            return None

    def generate_all_embeddings(self):
        """
        Generate embeddings for all images found in the images directory.
        """
        image_files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not image_files:
            logger.info("No images found. Nothing to embed.")
            return {}

        embeddings = {}
        logger.info(f"Found {len(image_files)} images. Generating embeddings individually...")
        for img_file in tqdm(image_files, desc="Generating embeddings"):
            img_path = os.path.join(IMAGES_DIR, img_file)
            emb = self.generate_embeddings_for_image(img_path)
            if emb is not None:
                embeddings[img_file] = emb

        return embeddings


def main():
    """
    Main function to generate all embeddings and save them to a file.
    """
    generator = EmbeddingGenerator()
    embeddings = generator.generate_all_embeddings()

    if embeddings:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(embeddings, f)
        logger.info(f"Saved embeddings for {len(embeddings)} images to {OUTPUT_FILE}")
    else:
        logger.info("No embeddings generated.")


if __name__ == "__main__":
    main()
