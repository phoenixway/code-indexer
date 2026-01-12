# AI Code Indexer

A local, AI-powered tool for indexing, summarizing, and semantically searching codebases. It uses **Tree-sitter** for robust parsing and **Sentence Transformers** (with **Ollama** integration) for semantic understanding.

## Features

- **Multi-language Support:** Currently supports Python (`.py`), Kotlin (`.kt`), and Go (`.go`).
- **Semantic Search:** Search your code using natural language queries (e.g., "how is authentication handled?").
- **Intent Extraction:** Automatically identifies functions and classes, extracting their responsibilities and side effects.
- **Local Processing:** Runs entirely locally using compiled Tree-sitter grammars and local LLMs.

## Prerequisites

- **Python 3.10+**
- **GCC** (for compiling Tree-sitter languages)
- **Ollama** (running locally for summarization/AI features)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd code-indexer
   ```

2. **Set up a virtual environment:**
   It is recommended to use a virtual environment to manage dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   # .\.venv\Scripts\activate  # On Windows
   ```

3. **Initialize Tree-sitter grammars:**
   The project requires the source code of Tree-sitter grammars in the `vendor/` directory. If they are missing, clone them manually:
   ```bash
   mkdir -p vendor
   git clone https://github.com/tree-sitter/tree-sitter-python vendor/tree-sitter-python
   git clone https://github.com/fwcd/tree-sitter-kotlin vendor/tree-sitter-kotlin
   git clone https://github.com/tree-sitter/tree-sitter-go vendor/tree-sitter-go
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Compile language bindings:**
   This step builds the shared library (`build/my-languages.so`) required for parsing.
   ```bash
   python3 build_langs.py
   ```

## Workflow

Follow this sequence to fully index your codebase:

1.  **Scan (`scan`)**: Parse the codebase to identify functions and classes.
2.  **Analyze (`intents` & `summarize`)**: Use LLM to understand what the code does.
3.  **Embed (`embed`)**: Create vector embeddings for semantic search.
4.  **Search (`search`)**: Query your codebase.

## Usage

The tool is controlled via the `main.py` CLI.

### 1. Scan a Directory
Parses files and extracts code entities (functions, classes).
```bash
python3 main.py scan /path/to/your/project
```

### 2. Extract Intents & Summarize
Uses LLM to analyze the code and generate summaries (requires Ollama running).
```bash
python3 main.py intents
python3 main.py summarize
```

### 3. Generate Embeddings
Creates vector embeddings for the indexed code to enable semantic search.
```bash
python3 main.py embed
```

### 4. Search
Search your codebase using natural language.
```bash
python3 main.py search "How do we handle database connections?"
```

## Model Setup (ONNX)

For running the tool on devices with limited resources (like Android/Termux), you should use the ONNX version of the embedding model.

1.  **Download the pre-converted model:**
    ```bash
    python3 download_onnx.py
    ```
    This script downloads a compatible ONNX version of `all-MiniLM-L6-v2` from Hugging Face and saves it to `models/all-MiniLM-L6-v2-onnx`.

## Lightweight Search (Search Only)

If you only need to search an existing index (e.g., on a mobile device) without the full indexing pipeline, use the lightweight search script. This avoids heavy dependencies like Tree-sitter or PyTorch.

1.  **Install minimal dependencies:**
    ```bash
    pip install -r requirements-search.txt
    ```
2.  **Ensure index and model are present:**
    Copy `.code-index/` and `models/all-MiniLM-L6-v2-onnx/` to your project directory.
3.  **Search:**
    ```bash
    python3 search_index.py "your query"
    ```

### Making it global (Termux & Linux)
To run the tools from any folder, run the installation script. It will generate launchers with hardcoded paths and place them in `~/bin` (Termux) or `~/.local/bin` (Linux).

```bash
./install_tools.sh
```

Ensure your PATH is configured:
```bash
# Bash
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc  # For Termux
# echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc  # For Linux

# Zsh
echo 'export PATH=$HOME/bin:$PATH' >> ~/.zshrc  # For Termux
# echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.zshrc  # For Linux

# Fish
set -gx PATH $HOME/bin $PATH  # For Termux (Universal)
# set -gx PATH $HOME/.local/bin $PATH # For Linux (Universal)
```

## Project Structure

- `src/parser.py`: Handles code parsing using Tree-sitter and custom queries.
- `src/ai.py`: Interacts with embedding models and Ollama.
- `src/storage.py`: Manages the database/storage of indexed code.
- `build_langs.py`: Script to compile Tree-sitter grammars into a shared object.
- `vendor/`: Contains the source code for Tree-sitter language grammars.

## Cross-platform Usage (Desktop & Mobile)

The tool supports different AI backends to run efficiently on various hardware.

### Desktop (Linux)
Uses **PyTorch** and `sentence-transformers` for maximum performance.
- **Requirements:** `pip install sentence-transformers torch`
- **Config (`~/.config/code-indexer/config.yaml`):**
  ```yaml
  models:
    provider: torch
    embedding: all-MiniLM-L6-v2
  ```

### Mobile (Android via Termux) - Search Only
Due to hardware and library limitations, the Android version works in **Search Only** mode. You cannot index code on the phone; you must transfer a pre-built index from your desktop.

**1. Installation:**
Termux requires system-level installation for heavy libraries like ONNX Runtime.

```bash
# Install system dependencies (including ONNX Runtime)
pkg install rust clang binutils python-numpy python-onnxruntime

# Run the automated installer
./install_tools.sh
```

**2. Setup Data:**
Copy these folders from your desktop project to the Termux project folder:
- `.code-index/` (The database)
- `models/all-MiniLM-L6-v2-onnx/` (The model)

**3. Search:**
```bash
search-index "your query"
```

**2. Model Setup:**
- Transfer the `models/all-MiniLM-L6-v2-onnx` folder (generated on desktop) to your phone.
- **Config (`~/.config/code-indexer/config.yaml`):**
  ```yaml
  models:
    provider: onnx
    embedding: /sdcard/path/to/models/all-MiniLM-L6-v2-onnx
  ```

## Troubleshooting

- **"build/my-languages.so not found":** Run `python3 build_langs.py`.
- **Import errors:** Ensure all requirements are installed and you are using the correct Python environment.
