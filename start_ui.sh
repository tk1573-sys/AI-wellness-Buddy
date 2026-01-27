#!/bin/bash
# Launcher script for AI Wellness Buddy Web UI

echo "=========================================="
echo "AI Wellness Buddy - Web UI Launcher"
echo "=========================================="
echo ""

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "⚠️ Streamlit not found. Installing..."
    pip install streamlit>=1.28.0
    echo ""
fi

echo "🚀 Starting Web UI..."
echo "📍 Opening in browser at: http://localhost:8501"
echo ""
echo "To stop: Press Ctrl+C"
echo "=========================================="
echo ""

# Launch streamlit
streamlit run ui_app.py
