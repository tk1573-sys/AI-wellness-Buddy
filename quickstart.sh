#!/bin/bash
# Quick Start Guide for AI Wellness Buddy

echo "=========================================="
echo "AI Wellness Buddy - Quick Start"
echo "=========================================="
echo ""

# Check if dependencies are installed
if ! python -c "import textblob" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
    echo ""
fi

echo "✅ Ready to start!"
echo ""
echo "To run the AI Wellness Buddy:"
echo "  python wellness_buddy.py"
echo ""
echo "Commands you can use during session:"
echo "  help    - View support resources and hotlines"
echo "  status  - See your emotional patterns"
echo "  profile - Manage trusted contacts"
echo "  quit    - End session and save progress"
echo ""
echo "=========================================="
