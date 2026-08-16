import os
import yaml


CONFIG_DIR = os.path.expanduser("~/.config/code-indexer")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")


DEFAULT_CONFIG = {
    "models": {
        "provider": "auto",
        "embedding": "all-MiniLM-L6-v2",
        "ollama": "qwen2.5-coder:7b",
    },

    "storage": {
        "index_dir": ".code-index",
        "docs_intents_dir": "docs/intents",
    },

    "languages": {
        ".py": "python",
        ".kt": "kotlin",
        ".go": "go",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".js": "javascript",
        ".jsx": "javascript",
    },
}


def deep_merge(defaults: dict, overrides: dict | None) -> dict:
    result = defaults.copy()

    if not overrides:
        return result

    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def load_config() -> dict:
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                DEFAULT_CONFIG,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )

        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}

    except Exception as e:
        print(f"Warning: failed to read config {CONFIG_FILE}: {e}")
        print("Using default configuration.")
        return DEFAULT_CONFIG.copy()

    return deep_merge(DEFAULT_CONFIG, user_config)


config_data = load_config()


INDEX_DIR = config_data["storage"]["index_dir"]

ENTITIES_FILE = os.path.join(
    INDEX_DIR,
    "entities.json",
)

INTENTS_FILE = os.path.join(
    INDEX_DIR,
    "intents.json",
)

EMBEDDINGS_FILE = os.path.join(
    INDEX_DIR,
    "embeddings.npy",
)

IDS_FILE = os.path.join(
    INDEX_DIR,
    "ids.json",
)

DOCS_INTENTS_DIR = config_data["storage"]["docs_intents_dir"]


EMBEDDING_MODEL = config_data["models"]["embedding"]
OLLAMA_MODEL = config_data["models"]["ollama"]
PROVIDER = config_data["models"].get("provider", "auto")


LANGUAGE_MAP = config_data["languages"]
