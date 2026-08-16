#!/usr/bin/env python3
import argparse
import os
import sys
import numpy as np
from src import config, storage, parser, intents, ai
from src.schema import CodeEntity, EntitySummary

def cmd_scan(args):
    print(f"🚀 Scanning {args.root}...")
    p = parser.CodeParser()
    new_entities = []
    
    # 1. Scan filesystem
    for root, _, files in os.walk(args.root):
        if any(x in root for x in [".git", "node_modules", "venv", "__pycache__"]): continue
        for file in files:
            path = os.path.join(root, file)
            found = p.parse_file(path)
            new_entities.extend(found)

    # 2. Merge with existing (preserve manual edits if needed, logic simplified here)
    # В канонічному flow ми перезаписуємо scan, бо human-edits повинні бути в коді
    storage.save_entities(new_entities)
    print(f"✅ Scanned {len(new_entities)} entities. Saved to entities.json")
    print("\n--- Next Recommended Step ---")
    print("1. Run 'code-indexer intents' if you have documentation in docs/intents/.")
    print("2. Run 'code-indexer summarize' to generate AI descriptions.")
    print("3. Run 'code-indexer embed' to create search vectors.")

def cmd_intents(args):
    print("📘 Parsing intents from docs/intents/...")
    p = intents.IntentParser()
    items = p.parse_all()
    
    # Validation: check if mapped entities exist
    entities_map = storage.load_entities()
    valid_intents = []
    
    for intent in items:
        missing = [e for e in intent.mapped_entities if e not in entities_map]
        if missing:
            print(f"⚠️  Intent '{intent.id}' maps to unknown entities: {missing}")
        valid_intents.append(intent)
        
    storage.save_intents(valid_intents)
    print(f"✅ Saved {len(valid_intents)} intents.")

def cmd_summarize(args):
    # Тільки для low confidence
    entities_map = storage.load_entities()
    entities = list(entities_map.values())
    
    to_process = [e for e in entities if e.confidence == "low"]
    if not to_process:
        print("Nothing to summarize (all entities have medium/high confidence).")
        return

    print(f"🧠 Generating AI summaries for {len(to_process)} entities...")
    engine = ai.AIEngine(load_embedder=False)
    
    processed_count = 0
    try:
        # Тут треба читати сирий файл, щоб дати код LLM. 
        # В entities.json коду немає (економія місця).
        for e in to_process:
            try:
                with open(e.path, "r", encoding="utf-8") as f:
                    code = f.read() # Спрощено, треба шукати по рядках
                
                summary_text = engine.generate_summary(code)
                e.summary = EntitySummary(text=summary_text, source="llm")
                e.update_confidence() # Стане medium
                print(f"Processed {e.symbol}")
                processed_count += 1
                
                if processed_count % 10 == 0:
                    storage.save_entities(entities)
                    print(f"Saved progress ({processed_count}/{len(to_process)}).")

            except Exception as ex:
                print(f"Error reading {e.path}: {ex}")
    except KeyboardInterrupt:
        print("\nInterrupted. Saving progress...")
        storage.save_entities(entities)
        sys.exit(0)

    storage.save_entities(entities)
    print("✅ Summarization complete.")
    print("\n--- Next Recommended Step ---")
    print("Run 'code-indexer embed' to update the search index with these new descriptions.")

def cmd_embed(args):
    print("Geometry is everything. Embedding data...")
    entities_map = storage.load_entities()
    intent_list = storage.load_intents()
    
    engine = ai.AIEngine(load_embedder=True)
    
    ids = []
    texts = []
    
    # 1. Embed Intents
    for i in intent_list:
        ids.append(i.id)
        # Векторизуємо опис інтентa
        texts.append(f"Intent: {i.description}")
        
    # 2. Embed Entities (тільки важливе)
    for e in entities_map.values():
        if e.summary:
            ids.append(e.id)
            # Векторизуємо Responsibility або Summary
            txt = e.responsibility if e.responsibility else e.summary.text
            texts.append(f"Entity {e.symbol}: {txt}")

    if not texts:
        print("Nothing to embed.")
        return

    matrix = engine.embed_texts(texts)
    storage.save_embeddings(ids, matrix)
    print(f"✅ Embedded {len(texts)} items.")

def cmd_search(args):
    ids, matrix = storage.load_embeddings()
    if matrix is None:
        print("Index empty. Run 'embed'.")
        return
        
    engine = ai.AIEngine(load_embedder=True)
    q_vec = engine.embed_texts([args.query])[0]
    
    # Cosine sim
    norm_mat = np.linalg.norm(matrix, axis=1)
    norm_q = np.linalg.norm(q_vec)
    scores = np.dot(matrix, q_vec) / (norm_mat * norm_q)
    
    top_k = scores.argsort()[-5:][::-1]
    
    print(f"\n🔍 Results for: '{args.query}'")
    for idx in top_k:
        obj_id = ids[idx]
        score = scores[idx]
        print(f"[{score:.4f}] {obj_id}")

def cmd_status(args):
    entities = storage.load_entities().values()
    intents_list = storage.load_intents()
    
    counts = {"low": 0, "medium": 0, "high": 0}
    for e in entities:
        counts[e.confidence] += 1
        
    print("--- Code Index Status ---")
    print(f"Intents: {len(intents_list)}")
    print(f"Entities: {len(entities)}")
    print(f"  High (Human):   {counts['high']}")
    print(f"  Medium (LLM):   {counts['medium']}")
    print(f"  Low (Raw):      {counts['low']}")
    
    print("\n--- Recommended Next Step ---")
    if len(entities) == 0:
        print("Run 'scan <path>' to index your codebase.")
    elif counts['low'] > 0:
        print(f"Run 'summarize' to analyze {counts['low']} new entities.")
        print("Or run 'embed' if you want to skip AI analysis for now.")
    elif not os.path.exists(os.path.join(storage.INDEX_DIR, "embeddings.npy")):
        print("Run 'embed' to build the search index.")
    else:
        print("Index is up to date! Try 'search \"your query\"'.")

def main():
    parser = argparse.ArgumentParser(prog="code-indexer")
    sub = parser.add_subparsers(dest="cmd", required=True)
    
    sub.add_parser("scan").add_argument("root")
    sub.add_parser("intents")
    sub.add_parser("summarize") # --llm assumed
    sub.add_parser("embed")
    sub.add_parser("search").add_argument("query")
    sub.add_parser("status")
    
    args = parser.parse_args()
    
    if args.cmd == "scan": cmd_scan(args)
    elif args.cmd == "intents": cmd_intents(args)
    elif args.cmd == "summarize": cmd_summarize(args)
    elif args.cmd == "embed": cmd_embed(args)
    elif args.cmd == "search": cmd_search(args)
    elif args.cmd == "status": cmd_status(args)

if __name__ == "__main__":
    main()
