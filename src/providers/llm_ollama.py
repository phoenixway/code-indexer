import ollama
from .base import BaseLLM

class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_summary(self, code_snippet: str) -> str:
        prompt = f"""
        Analyze this code.
        Code:
        {code_snippet[:1500]}
        
        Output a single sentence describing the BUSINESS RESPONSIBILITY.
        Do not describe syntax. Start with a verb.
        """
        try:
            res = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return res['message']['content'].strip()
        except Exception as e:
            print(f"Ollama Error: {e}")
            return "Analysis failed"
