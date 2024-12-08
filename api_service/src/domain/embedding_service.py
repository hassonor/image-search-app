"""
domain/embedding_service.py

Defines the EmbeddingService class for generating text embeddings using CLIP.
"""

import logging
import torch
import clip

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service to generate embeddings for textual queries."""

    def __init__(self, model_name: str = "ViT-B/32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        # Determine embedding dimension by encoding a dummy text
        self.dimension = self.model.encode_text(clip.tokenize(["test"]).to(self.device)).shape[1]
        logger.info(
            "Loaded CLIP model '%s' on %s with dimension %d.",
            model_name, self.device, self.dimension
        )

    def generate_embedding_from_text(self, text: str) -> list:
        """
        Generate an embedding vector for the given text.

        Args:
            text (str): The input text.

        Returns:
            list: The embedding vector as a list of floats.
        """
        try:
            text_tokens = clip.tokenize([text]).to(self.device)
            with torch.no_grad():
                embedding = self.model.encode_text(text_tokens)
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            embedding_np = embedding.cpu().numpy().tolist()[0]
            logger.debug("Generated embedding for text: '%s'", text)
            return embedding_np
        except Exception as e:
            logger.exception("Failed to generate embedding for text '%s': %s", text, e)
            return []
