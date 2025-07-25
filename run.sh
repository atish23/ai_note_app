#!/bin/bash

# Simplified AI Notes App Management Script

APP_DIR="$(pwd)"
VENV_DIR="$APP_DIR/venv_mcp"

# Check virtual environment
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
}

# Install dependencies
setup() {
    check_venv
    echo "Installing dependencies..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r requirements.txt
    echo "✅ Setup complete!"
}

# Setup Ollama
setup_ollama() {
    echo "Setting up Ollama..."
    if ! command -v ollama &> /dev/null; then
        echo "❌ Install Ollama first: https://ollama.ai/"
        exit 1
    fi
    
    echo "Pulling models..."
    ollama pull llama3.2:3b
    ollama pull nomic-embed-text
    echo "✅ Ollama ready!"
}

# Run Streamlit app
streamlit() {
    check_venv
    echo "Starting AI Notes App..."
    cd "$APP_DIR"
    "$VENV_DIR/bin/streamlit" run ai_note_app.py --server.headless true
}

# Show help
help() {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup         - Install dependencies"
    echo "  setup-ollama  - Setup Ollama models"
    echo "  streamlit     - Run Streamlit app"
    echo "  help          - Show this help"
}

# Main command handler
case "$1" in
    setup)
        setup
        ;;
    setup-ollama)
        setup_ollama
        ;;
    streamlit)
        streamlit
        ;;
    help|--help|-h)
        help
        ;;
    *)
        echo "Unknown command: $1"
        help
        exit 1
        ;;
esac
