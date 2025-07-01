# 💳 Credit Card Assistant

A smart AI-powered chatbot for Indian credit cards, specifically designed for **Axis Bank Atlas** and **ICICI Emeralde Private Metal** cards.

## ✨ Features

- 🧠 **Smart Query Enhancement**: Automatically reformats user questions for better understanding
- 💰 **Indian Currency Support**: Handles abbreviations like "2L", "20k", "1cr" naturally
- 🎯 **Accurate Calculations**: Precise reward calculations with exclusion and capping logic
- 💬 **Clean Interface**: Modern chat UI with quick question buttons
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- ⚡ **Fast Responses**: Optimized rule-based engine for quick answers

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Launch the app:**
   ```bash
   ./launch.sh
   ```

4. **Open your browser:**
   Go to [http://localhost:8503](http://localhost:8503)

## 💡 Usage Examples

The assistant understands natural language and Indian currency abbreviations:

- ✅ "What are the annual fees?"
- ✅ "If I spend 2L on flights, which card wins?"
- ✅ "Do I get points on utility payments?"
- ✅ "Compare reward rates for 50k hotel spending"
- ✅ "Which card is better for tax payments?"

## 🏗️ Project Structure

```
cc-features-chatbot/
├── app.py                 # Main Streamlit application
├── launch.sh             # Launch script
├── requirements.txt      # Python dependencies
├── data/
│   ├── axis-atlas.json   # Axis Bank Atlas card data
│   └── icici-epm.json    # ICICI Emeralde Private Metal data
├── utils/
│   └── qa_engine.py      # Core QA engine with reward calculations
└── test_cases.html       # Test cases for validation
```

## 🛠️ Technical Details

- **Framework**: Streamlit for web interface
- **AI Model**: OpenAI GPT-4 for natural language understanding
- **Data Format**: Structured JSON with comprehensive card terms
- **Calculations**: Rule-based engine for accurate reward computations
- **Currency Support**: Regex-based preprocessing for Indian abbreviations

## 🎯 Supported Cards

1. **Axis Bank Atlas Credit Card**
   - Travel rewards, milestone benefits, airport lounges
   - EDGE Miles calculation with category bonuses

2. **ICICI Bank Emeralde Private Metal Credit Card**
   - Premium benefits, comprehensive insurance, concierge
   - Reward Points with category caps and exclusions

## 🧪 Testing

The system includes comprehensive test cases covering:
- ✅ Reward calculations for different spending categories
- ✅ Exclusion logic (tax, government, fuel payments)
- ✅ Capping logic (utility, grocery, education, insurance)
- ✅ Currency abbreviation parsing (2L → ₹200,000)
- ✅ Multi-card comparisons and recommendations

## 📝 License

This project is for educational and research purposes.

---

**Made with ❤️ for Indian credit card users**
