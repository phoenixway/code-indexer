import argparse
import os
import json
import numpy as np
import time

# Спрощена конфігурація
INDEX_DIR = ".code-index"
EMBEDDINGS_FILE = os.path.join(INDEX_DIR, "embeddings.npy")
IDS_FILE = os.path.join(INDEX_DIR, "ids.json")
ENTITIES_FILE = os.path.join(INDEX_DIR, "entities.json")

def load_index():
    if not os.path.exists(EMBEDDINGS_FILE):
        print(f"Error: Index not found at {INDEX_DIR}")
        print("Please copy the '.code-index' folder from your desktop to this directory.")
        exit(1)
        
    print("Loading index...", end=" ", flush=True)
    start = time.time()
    matrix = np.load(EMBEDDINGS_FILE)
    with open(IDS_FILE, "r") as f:
        ids = json.load(f)
    print(f"Done ({time.time() - start:.2f}s)")
    return ids, matrix

def load_entities_map():
    if not os.path.exists(ENTITIES_FILE): return {}
    with open(ENTITIES_FILE, "r") as f:
        data = json.load(f)
    # Повертаємо map {id: entity} (спрощено, без Pydantic)
    return {item["id"]: item for item in data}

class OnnxEmbedder:
    def __init__(self, model_dir):
        import onnxruntime as ort
        from transformers import AutoTokenizer
        
        print(f"Loading ONNX model from {model_dir}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.session = ort.InferenceSession(os.path.join(model_dir, "model.onnx"), providers=["CPUExecutionProvider"])

    def encode(self, text):
        inputs = self.tokenizer([text], padding=True, truncation=True, return_tensors="np")
        outputs = self.session.run(None, dict(inputs))
        
        last_hidden_state = outputs[0]
        attention_mask = inputs['attention_mask']
        
        input_mask_expanded = np.expand_dims(attention_mask, -1)
        input_mask_expanded = np.broadcast_to(input_mask_expanded, last_hidden_state.shape)
        
        sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
        sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
        
        embeddings = sum_embeddings / sum_mask
        norm = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return (embeddings / norm)[0]

def main():
    parser = argparse.ArgumentParser(description="Lightweight Code Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--model", default="models/all-MiniLM-L6-v2-onnx", help="Path to ONNX model")
    args = parser.parse_args()

    # 1. Load Data
    ids, matrix = load_index()
    entities = load_entities_map()

    # 2. Load Model
    try:
        embedder = OnnxEmbedder(args.model)
    except Exception as e:
        print(f"\nError loading model: {e}")
        print(f"Make sure the model exists at: {args.model}")
        return

    # 3. Search
    print(f"\nSearching for: '{args.query}'")
    q_vec = embedder.encode(args.query)
    
    # Cosine Similarity
    norm_mat = np.linalg.norm(matrix, axis=1)
    norm_q = np.linalg.norm(q_vec)
    scores = np.dot(matrix, q_vec) / (norm_mat * norm_q)
    
    top_k = scores.argsort()[-5:][::-1]
    
    print("\n--- Results ---")
    for idx in top_k:
        obj_id = ids[idx]
        score = scores[idx]
        entity = entities.get(obj_id, {{}})
        
        path = entity.get('path', 'unknown')
        symbol = entity.get('symbol', obj_id)
        
        # Спробуємо показати опис
        summary = ""
        if 'summary' in entity and entity['summary']:
            summary = entity['summary'].get('text', '')
        elif 'responsibility' in entity:
            summary = entity['responsibility']
            
        print(f"\n[{score:.4f}] {symbol}")
        print(f"  File: {path}")
        if summary:
            print(f"  Desc: {summary}")

if __name__ == "__main__":
    main()
