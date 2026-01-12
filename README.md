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

3. **Initialize submodules (for Tree-sitter grammars):**
   ```bash
   git submodule update --init --recursive
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

## Project Structure

- `src/parser.py`: Handles code parsing using Tree-sitter and custom queries.
- `src/ai.py`: Interacts with embedding models and Ollama.
- `src/storage.py`: Manages the database/storage of indexed code.
- `build_langs.py`: Script to compile Tree-sitter grammars into a shared object.
- `vendor/`: Contains the source code for Tree-sitter language grammars.

## Troubleshooting

- **"build/my-languages.so not found":** Run `python3 build_langs.py`.
- **Import errors:** Ensure all requirements are installed and you are using the correct Python environment.
