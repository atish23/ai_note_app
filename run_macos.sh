#!/bin/bash

# Native macOS App Runner for AI Notes/Task Manager

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

# Run native macOS app
macos_app() {
    check_venv
    echo "Starting AI Notes as native macOS app..."
    cd "$APP_DIR"
    "$VENV_DIR/bin/python" macos_app.py
}

# Build macOS app bundle (optional)
build_bundle() {
    check_venv
    echo "Building macOS app bundle..."
    
    # Install py2app if not already installed
    "$VENV_DIR/bin/pip" install py2app
    
    # Create setup.py for py2app
    cat > setup.py << 'EOF'
from setuptools import setup

APP = ['macos_app.py']
DATA_FILES = [
    ('', ['ai_note_app.py']),
    ('core', ['core/*.py']),
    ('', ['requirements.txt']),
    ('', ['llm_config.json']),
    ('', ['notes.db']),
    ('', ['faiss.index']),
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'streamlit', 'google', 'faiss', 'numpy'],
    'iconfile': 'app_icon.icns',  # Optional: add your icon
    'plist': {
        'CFBundleName': 'AI Notes',
        'CFBundleDisplayName': 'AI Notes/Task Manager',
        'CFBundleIdentifier': 'com.ainotes.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOF

    # Build the app
    "$VENV_DIR/bin/python" setup.py py2app
    echo "✅ App bundle created in dist/AI Notes.app"
}

# Show help
help() {
    echo "Usage: ./run_macos.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup         - Install dependencies"
    echo "  macos         - Run native macOS app"
    echo "  build         - Build macOS app bundle (.app)"
    echo "  help          - Show this help"
}

# Main command handler
case "$1" in
    setup)
        setup
        ;;
    macos)
        macos_app
        ;;
    build)
        build_bundle
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
