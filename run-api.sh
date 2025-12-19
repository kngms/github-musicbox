#!/bin/bash
# Quick start script for Music Track Generator API

set -e

echo "🎵 Music Track Generator API Server"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: Please run this script from the repository root"
    exit 1
fi

# Check if installed
if ! python -c "import music_generator" 2>/dev/null; then
    echo "📦 Installing package..."
    pip install -e . > /dev/null 2>&1
    echo "✅ Package installed"
fi

# Set defaults
export MUSIC_GEN_MODE=${MUSIC_GEN_MODE:-simulate}
export PORT=${PORT:-8080}

echo "🚀 Starting API server..."
echo "   Mode: $MUSIC_GEN_MODE"
echo "   Port: $PORT"
echo "   Docs: http://localhost:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn music_generator.api:app --host 0.0.0.0 --port $PORT
