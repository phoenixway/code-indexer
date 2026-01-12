#!/bin/bash

# --- Configuration ---
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "📍 Project detected at: $PROJECT_DIR"

# --- Detect Platform ---
if [ -n "$TERMUX_VERSION" ]; then
    PLATFORM="termux"
    TARGET_BIN="$HOME/bin"
    # On Android, we only support search, so we use the search requirements
    REQ_FILE="$PROJECT_DIR/requirements-search.txt"
    echo "📱 Android (Termux) detected. Mode: Search Only."
else
    PLATFORM="linux"
    TARGET_BIN="$HOME/.local/bin"
    REQ_FILE="$PROJECT_DIR/requirements.txt"
    echo "🐧 Linux detected. Mode: Full (Index & Search)."
fi

# --- 1. Setup Virtual Environment ---
echo "📦 Setting up virtual environment..."

if [ -d "$VENV_DIR" ]; then
    echo "   Virtual environment already exists."
else
    if [ "$PLATFORM" == "termux" ]; then
        # Termux needs system site packages for onnxruntime (installed via pkg)
        python3 -m venv --system-site-packages "$VENV_DIR"
    else
        python3 -m venv "$VENV_DIR"
    fi
    echo "   Created new venv."
fi

# Activate venv for installation
source "$VENV_DIR/bin/activate"
PYTHON_EXEC="$VENV_DIR/bin/python"
PIP_EXEC="$VENV_DIR/bin/pip"

# --- 2. Install Dependencies ---
echo "⬇️  Installing dependencies from $(basename "$REQ_FILE")..."

# Upgrade pip first
"$PIP_EXEC" install --upgrade pip

if [ "$PLATFORM" == "termux" ]; then
    # Termux specific handling
    
    # 1. Remove packages that should be installed via pkg to avoid conflicts
    # (We assume user followed README and installed pkg python-onnxruntime)
    if grep -q "onnxruntime" "$REQ_FILE"; then
        echo "   Removing onnxruntime from requirements (using system package)..."
        sed -i '/onnxruntime/d' "$REQ_FILE"
    fi
    
    "$PIP_EXEC" install -r "$REQ_FILE"
else
    # Standard Linux installation
    "$PIP_EXEC" install -r "$REQ_FILE"
    
    # Initialize submodules if needed (for building langs)
    echo "🔄 Initializing git submodules..."
    git submodule update --init --recursive 2>/dev/null || true
    
    # Compile tree-sitter languages
    echo "🏗️  Compiling Tree-sitter languages..."
    "$PYTHON_EXEC" "$PROJECT_DIR/build_langs.py"
fi

# --- 3. Install Launchers ---
echo "🚀 Installing launchers..."
mkdir -p "$TARGET_BIN"

install_wrapper() {
    local SCRIPT_NAME=$1
    local PYTHON_SCRIPT=$2
    local WRAPPER_PATH="$TARGET_BIN/$SCRIPT_NAME"

    echo "   -> $SCRIPT_NAME"

    cat > "$WRAPPER_PATH" <<EOF
#!/bin/bash
# Generated wrapper for $SCRIPT_NAME

PROJECT_DIR="$PROJECT_DIR"
PYTHON_EXEC="\$PROJECT_DIR/.venv/bin/python"
SCRIPT_FILE="\$PROJECT_DIR/$PYTHON_SCRIPT"

if [ ! -f "\$PYTHON_EXEC" ]; then
    echo "Error: Virtual environment not found at \$PROJECT_DIR/.venv"
    exit 1
fi

exec "\$PYTHON_EXEC" "\$SCRIPT_FILE" "\$@"
EOF

    chmod +x "$WRAPPER_PATH"
}

# Install tools
if [ "$PLATFORM" == "termux" ]; then
    # On Termux, only install the search tool
    install_wrapper "search-index" "search_index.py"
else
    # On Linux, install both
    install_wrapper "code-indexer" "main.py"
    install_wrapper "search-index" "search_index.py"
fi

echo ""
echo "🎉 Installation complete!"
echo "Make sure $TARGET_BIN is in your PATH."
if [ "$PLATFORM" == "termux" ]; then
    echo "  Fish:    set -U fish_user_paths $HOME/bin \$fish_user_paths"
    echo "  Bash:    echo 'export PATH=\$HOME/bin:\$PATH' >> ~/.bashrc"
    echo "  Zsh:     echo 'export PATH=\$HOME/bin:\$PATH' >> ~/.zshrc"
else
    echo "  Fish:    set -U fish_user_paths $HOME/.local/bin \$fish_user_paths"
    echo "  Bash:    echo 'export PATH=\$HOME/.local/bin:\$PATH' >> ~/.bashrc"
    echo "  Zsh:     echo 'export PATH=\$HOME/.local/bin:\$PATH' >> ~/.zshrc"
fi
