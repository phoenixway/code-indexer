from abc import ABC, abstractmethod
from typing import List
import numpy as np

class BaseEmbedder(ABC):
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Takes a list of strings and returns a numpy array of embeddings.
        Shape: (len(texts), embedding_dim)
        """
        pass

class BaseLLM(ABC):
    @abstractmethod
    def generate_summary(self, code_snippet: str) -> str:
        """
        Takes a code snippet and returns a short summary string.
        """
        pass
