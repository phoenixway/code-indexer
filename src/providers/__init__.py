import os
import sys
from .base import BaseEmbedder, BaseLLM

# Factory methods

def get_embedder(provider_type: str, model_name_or_path: str) -> BaseEmbedder:
    """
    Factory to create an embedder instance.
    provider_type: 'torch', 'onnx', or 'auto'
    """
    if provider_type == "auto":
        # Check if ONNX model exists first (preferred for speed/portability if available)
        # However, usually we default to torch on desktop unless specifically set.
        # Let's simple check: is it a path to a directory? -> ONNX. Is it a HF string? -> Torch.
        if os.path.isdir(model_name_or_path) and os.path.exists(os.path.join(model_name_or_path, "model.onnx")):
            provider_type = "onnx"
        else:
            provider_type = "torch"

    if provider_type == "onnx":
        from .embed_onnx import OnnxEmbedder
        return OnnxEmbedder(model_name_or_path)
    
    elif provider_type == "torch":
        from .embed_torch import TorchEmbedder
        return TorchEmbedder(model_name_or_path)
    
    else:
        raise ValueError(f"Unknown embedder provider: {provider_type}")

def get_llm(provider_type: str, model_name: str) -> BaseLLM:
    """
    Factory for LLM. Currently only supports 'ollama'.
    """
    if provider_type == "ollama" or provider_type == "auto":
        from .llm_ollama import OllamaLLM
        return OllamaLLM(model_name)
    else:
        raise ValueError(f"Unknown LLM provider: {provider_type}")
