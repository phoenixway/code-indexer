from typing import List
import numpy as np
from .base import BaseEmbedder

class TorchEmbedder(BaseEmbedder):
    def __init__(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers is not installed. Run 'pip install sentence-transformers'.")
        
        print(f"Loading Torch Embedder: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
