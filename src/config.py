import os
import yaml

# Шлях до конфігурації в домашній папці
CONFIG_DIR = os.path.expanduser("~/.config/code-indexer")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

# Дефолтні налаштування
DEFAULT_CONFIG = {
    "models": {
        "provider": "auto",  # auto, torch, onnx
        "embedding": "all-MiniLM-L6-v2",
        "ollama": "qwen2.5-coder:7b"
    },
    "storage": {
        "index_dir": ".code-index",
        "docs_intents_dir": "docs/intents"
    },
    "languages": {
        ".py": "python",
        ".kt": "kotlin",
        ".go": "go"
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        return DEFAULT_CONFIG
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        user_config = yaml.safe_load(f)
        # Об'єднуємо з дефолтними, щоб не було помилок при відсутності полів
        return {**DEFAULT_CONFIG, **user_config}

config_data = load_config()

# Експортуємо змінні для використання в коді
INDEX_DIR = config_data["storage"]["index_dir"]
ENTITIES_FILE = os.path.join(INDEX_DIR, "entities.json")
INTENTS_FILE = os.path.join(INDEX_DIR, "intents.json")
EMBEDDINGS_FILE = os.path.join(INDEX_DIR, "embeddings.npy")
IDS_FILE = os.path.join(INDEX_DIR, "ids.json")

DOCS_INTENTS_DIR = config_data["storage"]["docs_intents_dir"]

EMBEDDING_MODEL = config_data["models"]["embedding"]

OLLAMA_MODEL = config_data["models"]["ollama"]

PROVIDER = config_data["models"].get("provider", "auto")



LANGUAGE_MAP = config_data["languages"]
