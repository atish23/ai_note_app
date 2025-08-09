#!/bin/bash

# Build macOS App Bundle for AI Notes
# This creates a standalone .app file that can be installed in Applications

APP_DIR="$(pwd)"
VENV_DIR="$APP_DIR/venv_mcp"
APP_NAME="AI Notes"
BUNDLE_NAME="AI Notes.app"

# Check virtual environment
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "❌ Virtual environment not found. Please run setup first:"
        echo "   ./run_macos.sh setup"
        exit 1
    fi
}

# Install py2app if not already installed
install_py2app() {
    echo "📦 Installing py2app..."
    "$VENV_DIR/bin/pip" install py2app
}

# Create setup.py for py2app
create_setup_py() {
    echo "📝 Creating setup.py..."
    cat > setup.py << 'EOF'
from setuptools import setup
import os
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

APP = ['macos_app.py']
DATA_FILES = [
    ('', ['ai_note_app.py']),
    ('core', [str(f) for f in Path('core').glob('*.py')]),
    ('', ['requirements.txt']),
    ('', ['llm_config.json']),
    ('', ['notes.db']),
    ('', ['faiss.index']),
    ('', ['run_macos.sh']),
    ('', ['run.sh']),
]

OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtWebEngineWidgets',
        'streamlit', 'google', 'faiss', 'numpy', 'requests', 'mcp'
    ],
    'includes': [
        'pathlib', 'subprocess', 'threading', 'time', 'signal',
        'sqlite3', 'json', 'asyncio'
    ],
    'excludes': ['tkinter', 'matplotlib', 'scipy'],
    'plist': {
        'CFBundleName': 'AI Notes',
        'CFBundleDisplayName': 'AI Notes/Task Manager',
        'CFBundleIdentifier': 'com.ainotes.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14',
        'NSRequiresAquaSystemAppearance': False,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOF
}

# Build the app
build_app() {
    echo "🔨 Building macOS app bundle..."
    
    # Clean previous builds
    rm -rf build dist
    
    # Build the app
    "$VENV_DIR/bin/python" setup.py py2app
    
    if [ -d "dist/$BUNDLE_NAME" ]; then
        echo "✅ App bundle created successfully!"
        echo "📱 Location: dist/$BUNDLE_NAME"
        echo ""
        echo "🎉 You can now:"
        echo "   1. Drag 'dist/$BUNDLE_NAME' to your Applications folder"
        echo "   2. Double-click to launch from Applications"
        echo "   3. Add to Dock for quick access"
    else
        echo "❌ Failed to create app bundle"
        exit 1
    fi
}

# Create a simple installer script
create_installer() {
    echo "📦 Creating installer script..."
    cat > install_ai_notes.sh << 'EOF'
#!/bin/bash

# AI Notes Installer
# This script installs the AI Notes app to Applications

APP_NAME="AI Notes.app"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="/Applications"

echo "🚀 Installing AI Notes to Applications..."

if [ -d "$SOURCE_DIR/dist/$APP_NAME" ]; then
    # Remove existing installation
    if [ -d "$TARGET_DIR/$APP_NAME" ]; then
        echo "🗑️ Removing existing installation..."
        rm -rf "$TARGET_DIR/$APP_NAME"
    fi
    
    # Copy to Applications
    echo "📱 Installing to Applications..."
    cp -R "$SOURCE_DIR/dist/$APP_NAME" "$TARGET_DIR/"
    
    if [ $? -eq 0 ]; then
        echo "✅ Installation successful!"
        echo "🎉 AI Notes is now installed in Applications"
        echo "   You can launch it from Applications or add it to your Dock"
        
        # Ask if user wants to open Applications folder
        read -p "Open Applications folder? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "$TARGET_DIR"
        fi
    else
        echo "❌ Installation failed"
        exit 1
    fi
else
    echo "❌ App bundle not found. Please run build first:"
    echo "   ./build_app.sh"
    exit 1
fi
EOF

    chmod +x install_ai_notes.sh
    echo "📦 Installer script created: install_ai_notes.sh"
}

# Main execution
main() {
    echo "🔨 Building AI Notes macOS App Bundle"
    echo "====================================="
    
    check_venv
    install_py2app
    create_setup_py
    build_app
    create_installer
    
    echo ""
    echo "🎉 Build complete! You can now:"
    echo "   1. Run: ./install_ai_notes.sh (to install to Applications)"
    echo "   2. Or manually drag dist/$BUNDLE_NAME to Applications"
    echo "   3. Or run directly: open dist/$BUNDLE_NAME"
}

# Run main function
main
