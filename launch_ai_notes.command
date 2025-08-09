#!/bin/bash

# AI Notes Launcher Script
# Double-click this file to launch the AI Notes app

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Launching AI Notes/Task Manager..."
echo "📁 Directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv_mcp" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   ./run_macos.sh setup"
    read -p "Press Enter to continue..."
    exit 1
fi

# Launch the native macOS app
echo "🖥️ Starting native macOS app..."
./run_macos.sh macos

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo "❌ Error launching app. Press Enter to close..."
    read -p ""
fi
