from typing import List
from .config import EMBEDDING_MODEL, OLLAMA_MODEL, PROVIDER
from .providers import get_embedder, get_llm

class AIEngine:
    def __init__(self, load_embedder=False):
        self.embedder = None
        self.llm = get_llm("ollama", OLLAMA_MODEL)
        
        if load_embedder:
            # Визначаємо шлях до моделі для ONNX
            # Якщо PROVIDER="onnx", то EMBEDDING_MODEL має вказувати на папку
            # Або ми можемо хардкодити дефолтний шлях експорту, якщо це "auto" і "torch" назва
            
            model_source = EMBEDDING_MODEL
            
            # Якщо користувач хоче ONNX, але вказав назву з HF, спробуємо знайти локальну папку
            if PROVIDER == "onnx" or (PROVIDER == "auto" and "sentence-transformers" in model_source):
                 potential_onnx_path = "models/all-MiniLM-L6-v2-onnx"
                 if os.path.exists(potential_onnx_path):
                     model_source = potential_onnx_path

            self.embedder = get_embedder(PROVIDER, model_source)

    def generate_summary(self, code_snippet: str) -> str:
        return self.llm.generate_summary(code_snippet)

    def embed_texts(self, texts: List[str]):
        if not self.embedder:
            raise ValueError("Embedder not loaded")
        return self.embedder.encode(texts)