import os
import numpy as np
from typing import List
from .base import BaseEmbedder

class OnnxEmbedder(BaseEmbedder):
    def __init__(self, model_dir: str):
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
        except ImportError:
            raise ImportError("onnxruntime or transformers is not installed. Run 'pip install onnxruntime transformers'.")

        onnx_file = os.path.join(model_dir, "model.onnx")
        if not os.path.exists(onnx_file):
             raise FileNotFoundError(f"ONNX model not found at {onnx_file}. Run 'python3 export_to_onnx.py' first.")

        print(f"Loading ONNX Embedder from {model_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        # Assuming CPU execution for broader compatibility (Termux)
        self.session = ort.InferenceSession(onnx_file, providers=["CPUExecutionProvider"])

    def encode(self, texts: List[str]) -> np.ndarray:
        # Tokenize
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="np")
        
        # Inference
        outputs = self.session.run(None, dict(inputs))
        
        # Mean Pooling (attention mask aware) - common logic for sentence-transformers models
        last_hidden_state = outputs[0]
        attention_mask = inputs['attention_mask']
        
        input_mask_expanded = np.expand_dims(attention_mask, -1)
        input_mask_expanded = np.broadcast_to(input_mask_expanded, last_hidden_state.shape)
        
        sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
        sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
        
        embeddings = sum_embeddings / sum_mask
        
        # Normalize
        norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norm
