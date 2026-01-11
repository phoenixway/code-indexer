import ollama
from sentence_transformers import SentenceTransformer
from typing import List
from .config import EMBEDDING_MODEL, OLLAMA_MODEL

class AIEngine:
    def __init__(self, load_embedder=False):
        self.embedder = None
        if load_embedder:
            print(f"Loading embedding model: {EMBEDDING_MODEL}...")
            self.embedder = SentenceTransformer(EMBEDDING_MODEL)

    def generate_summary(self, code_snippet: str) -> str:
        """
        Використовується для команди `summarize`.
        Лише для сутностей з confidence=low.
        """
        prompt = f"""
        Analyze this code.
        Code:
        {code_snippet[:1500]}
        
        Output a single sentence describing the BUSINESS RESPONSIBILITY.
        Do not describe syntax. Start with a verb.
        """
        try:
            res = ollama.chat(model=OLLAMA_MODEL, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return res['message']['content'].strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Analysis failed"

    def embed_texts(self, texts: List[str]):
        """Використовується для команди `embed`"""
        if not self.embedder:
            raise ValueError("Embedder not loaded")
        return self.embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True)
