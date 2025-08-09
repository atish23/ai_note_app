#!/bin/bash

# AI Notes Backup Launcher
# Double-click this file to create a backup of your AI Notes data

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 AI Notes Backup Manager"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv_mcp" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   ./run_macos.sh setup"
    read -p "Press Enter to continue..."
    exit 1
fi

# Run backup manager
echo "🚀 Starting backup manager..."
"$SCRIPT_DIR/venv_mcp/bin/python" backup_manager.py "$@"

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Backup operation failed. Press Enter to close..."
    read -p ""
fi
