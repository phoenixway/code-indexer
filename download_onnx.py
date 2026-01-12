import os
import requests
from tqdm import tqdm

MODEL_DIR = "models/all-MiniLM-L6-v2-onnx"
BASE_URL = "https://huggingface.co/Xenova/all-MiniLM-L6-v2/resolve/main"

FILES = [
    "onnx/model.onnx",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
    "special_tokens_map.json",
    "config.json"
]

def download_file(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest, 'wb') as f, tqdm(
        desc=os.path.basename(dest),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

def main():
    print(f"Downloading pre-converted ONNX model to {MODEL_DIR}...")
    
    for file_path in FILES:
        url = f"{BASE_URL}/{file_path}"
        # Зберігаємо model.onnx безпосередньо в корінь папки моделі для сумісності з нашим кодом
        local_path = os.path.join(MODEL_DIR, os.path.basename(file_path))
        download_file(url, local_path)
    
    print("\n✅ Success! Model downloaded and ready for use.")

if __name__ == "__main__":
    main()

