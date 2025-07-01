#!/bin/bash

echo "🧙‍♂️ Starting Credit Card Wizard Assistant..."
echo "Open http://localhost:8502 in your browser"
echo ""
echo "Features:"
echo "- 🧙‍♂️ Guided step-by-step interface"
echo "- 💬 Traditional chat interface" 
echo "- 🔄 Switch between modes anytime"
echo "- 📊 Accurate reward calculations"
echo ""

streamlit run app_wizard.py --server.port 8502 