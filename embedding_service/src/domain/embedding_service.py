"""
embedding_service.py

Provides the EmbeddingService class to generate embeddings for images using CLIP.
"""

import logging
import torch
from PIL import Image
from typing import Optional
import clip

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service to generate embeddings for images using the CLIP model.
    """

    def __init__(self, model_name: str = "ViT-B/32"):
        """
        Load the CLIP model and preprocess function, and determine embedding dimension.

        Args:
            model_name (str): Name of the CLIP model to load.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        # Determine embedding dimension by encoding a dummy image
        dummy_image = Image.new("RGB", (224, 224))
        image_tensor = self.preprocess(dummy_image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model.encode_image(image_tensor)
        self.dimension = embedding.shape[1]
        logger.info(
            f"Loaded CLIP model '{model_name}' on {self.device} with dimension {self.dimension}."
        )

    def generate_embedding_from_image(self, image_path: str) -> Optional[list]:
        """
        Generate an embedding vector for the given image.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Optional[list]: Embedding vector as a list of floats, or None if generation fails.

        Error Handling:
            Logs exception and returns None if embedding generation fails.
        """
        try:
            image = Image.open(image_path).convert("RGB")
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                embedding = self.model.encode_image(image_tensor)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            embedding_np = embedding.cpu().numpy().tolist()[0]
            logger.debug(f"Generated embedding for image: {image_path}")
            return embedding_np
        except Exception as e:
            logger.exception(
                f"Failed to generate embedding for image '{image_path}': {e}"
            )
            return None
