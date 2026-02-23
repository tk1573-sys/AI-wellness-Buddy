#!/bin/bash
# Network-accessible launcher script for AI Wellness Buddy Web UI
# This script starts the UI on all network interfaces (0.0.0.0)

echo "=========================================="
echo "AI Wellness Buddy - Network UI Launcher"
echo "=========================================="
echo ""

# Check if streamlit is installed (using python3 explicitly)
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️ Streamlit not found. Installing..."
    pip3 install streamlit>=1.28.0
    echo ""
fi

# Get local IP address using more reliable methods
if command -v hostname &> /dev/null; then
    # Most reliable method across distributions
    LOCAL_IP=$(hostname -I | awk '{print $1}')
elif command -v ip &> /dev/null; then
    # Alternative using ip command with more robust parsing
    LOCAL_IP=$(ip route get 1 2>/dev/null | grep -oP 'src \K[^ ]+' | head -n1)
elif command -v ifconfig &> /dev/null; then
    # Fallback for systems without ip command
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n1)
else
    LOCAL_IP="your-ip-address"
fi

# Fallback if IP detection failed
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="your-ip-address"
fi

# Default port
PORT=${1:-8501}

echo "🚀 Starting Web UI on network..."
echo "📍 Local access: http://localhost:$PORT"
echo "📍 Network access: http://$LOCAL_IP:$PORT"
echo ""
echo "⚠️  SECURITY NOTE:"
echo "   This allows network access to your wellness buddy."
echo "   Only use on trusted networks!"
echo ""
echo "To stop: Press Ctrl+C"
echo "=========================================="
echo ""

# Launch streamlit with network access (using explicit python3)
python3 -m streamlit run ui_app.py --server.address 0.0.0.0 --server.port $PORT --server.headless true
