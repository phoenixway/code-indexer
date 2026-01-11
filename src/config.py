iimport os

# Шляхи до даних
INDEX_DIR = ".code-index"
ENTITIES_FILE = os.path.join(INDEX_DIR, "entities.json")
INTENTS_FILE = os.path.join(INDEX_DIR, "intents.json")
EMBEDDINGS_FILE = os.path.join(INDEX_DIR, "embeddings.npy")
IDS_FILE = os.path.join(INDEX_DIR, "ids.json") # Зв'язок векторів з ID

# Шляхи до документації
DOCS_INTENTS_DIR = "docs/intents"

# Моделі
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "qwen2.5-coder:7b"

# Підтримка мов
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust"
}mport os

# Шляхи до даних
INDEX_DIR = ".code-index"
ENTITIES_FILE = os.path.join(INDEX_DIR, "entities.json")
INTENTS_FILE = os.path.join(INDEX_DIR, "intents.json")
EMBEDDINGS_FILE = os.path.join(INDEX_DIR, "embeddings.npy")
IDS_FILE = os.path.join(INDEX_DIR, "ids.json") # Зв'язок векторів з ID

# Шляхи до документації
DOCS_INTENTS_DIR = "docs/intents"

# Моделі
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_MODEL = "qwen2.5-coder:7b"

# Підтримка мов
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust"
}
