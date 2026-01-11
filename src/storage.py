import os
import json
import numpy as np
from typing import List, Dict
from .config import INDEX_DIR, ENTITIES_FILE, INTENTS_FILE, EMBEDDINGS_FILE, IDS_FILE
from .schema import CodeEntity, Intent

def ensure_index_dir():
    os.makedirs(INDEX_DIR, exist_ok=True)

# --- Entities ---
def save_entities(entities: List[CodeEntity]):
    ensure_index_dir()
    data = [e.model_dump(exclude_none=True) for e in entities]
    with open(ENTITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_entities() -> Dict[str, CodeEntity]:
    if not os.path.exists(ENTITIES_FILE): return {}
    with open(ENTITIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Повертаємо map {id: entity} для швидкого доступу
    return {item["id"]: CodeEntity(**item) for item in data}

# --- Intents ---
def save_intents(intents: List[Intent]):
    ensure_index_dir()
    data = [i.model_dump(exclude_none=True) for i in intents]
    with open(INTENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_intents() -> List[Intent]:
    if not os.path.exists(INTENTS_FILE): return []
    with open(INTENTS_FILE, "r", encoding="utf-8") as f:
        return [Intent(**i) for i in json.load(f)]

# --- Embeddings ---
def save_embeddings(ids: List[str], matrix: np.ndarray):
    ensure_index_dir()
    np.save(EMBEDDINGS_FILE, matrix)
    with open(IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f)

def load_embeddings():
    if not os.path.exists(EMBEDDINGS_FILE) or not os.path.exists(IDS_FILE):
        return [], None
    with open(IDS_FILE, "r") as f:
        ids = json.load(f)
    matrix = np.load(EMBEDDINGS_FILE)
    return ids, matrix
