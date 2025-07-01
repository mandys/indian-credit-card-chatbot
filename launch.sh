#!/bin/bash

# Credit Card Assistant Enhanced Launcher
echo "💳 Starting Credit Card Assistant..."
echo "Open http://localhost:8503 in your browser"
echo "Features:"
echo "- 🧠 Smart query enhancement"
echo "- 💬 Clean chat interface"
echo "- 🎯 Optimized for Axis & ICICI cards"
echo "- 📱 Mobile-friendly design"
echo "- 💰 Indian currency support (2L, 20k, etc.)"

# Kill any existing streamlit on port 8503
pkill -f "streamlit.*8503" 2>/dev/null

# Start the enhanced app
streamlit run app.py --server.port 8503

echo "  Stopping..." 