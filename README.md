# 💳 Credit Card Assistant

A smart AI-powered chatbot for Indian credit cards, specifically designed for **Axis Bank Atlas** and **ICICI Emeralde Private Metal** cards.

## ✨ Features

- 🧠 **Smart Query Enhancement**: Automatically reformats user questions for better understanding
- 💰 **Enhanced Indian Currency Support**: Handles "lakh", "crore", "2L", "20k", "1cr" naturally
- 🎯 **Accurate Calculations**: Precise reward calculations with exclusion and capping logic
- 💬 **Interactive Chat Interface**: Modern UI with collapsible quick questions
- 📱 **Mobile Optimized**: Responsive design with touch-friendly controls
- ⚡ **Fast Responses**: Optimized rule-based engine for quick answers
- 👍 **User Feedback System**: Thumbs up/down with improvement suggestions
- 📊 **Analytics Dashboard**: Built-in feedback monitoring and analytics
- 🔄 **Real-time Updates**: Immediate feedback button display

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   ```bash
   # For Gemini (recommended)
   export GEMINI_API_KEY="your-gemini-api-key-here"
   
   # For OpenAI (fallback)
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Launch the app:**
   ```bash
   ./launch.sh
   ```

4. **Open your browser:**
   Go to [http://localhost:8501](http://localhost:8501)

## 💡 Usage Examples

The assistant understands natural language and Indian currency abbreviations:

- ✅ "What are the annual fees?"
- ✅ "If I spend 5 lakh on flights, which card wins?"
- ✅ "Do I get points on utility payments?"
- ✅ "Compare reward rates for 50k hotel spending"
- ✅ "Which card is better for tax payments?"
- ✅ "Benefits of gold tier in Axis Atlas?"
- ✅ "5 crore spending on ICICI EPM rewards?"

## 🏗️ Project Structure

```
cc-features-chatbot/
├── app.py                    # Main Streamlit application with feedback system
├── launch.sh                # Launch script
├── requirements.txt         # Python dependencies
├── feedback_dashboard.py    # Standalone feedback analytics dashboard
├── feedback_log.json       # User feedback storage (auto-generated, not tracked)
├── data/
│   ├── axis-atlas.json     # Axis Bank Atlas card data (normalized)
│   └── icici-epm.json      # ICICI Emeralde Private Metal data (normalized)
├── utils/
│   └── qa_engine.py        # Enhanced QA engine with reward calculations
└── test_cases.html         # Comprehensive test cases for validation
```

## 🛠️ Technical Details

- **Framework**: Streamlit for web interface with real-time updates
- **AI Model**: Google Gemini (primary) / OpenAI GPT-4 (fallback) for natural language understanding
- **Data Format**: Normalized JSON structure for consistent processing
- **Calculations**: Enhanced rule-based engine for accurate reward computations
- **Currency Support**: Comprehensive regex patterns for Indian currency terms
- **Feedback System**: JSON-based logging with built-in analytics dashboard
- **Mobile Support**: CSS media queries for responsive design

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
- ✅ Enhanced currency parsing (5 lakh → ₹500,000, 2 crore → ₹20,000,000)
- ✅ Multi-card comparisons and recommendations
- ✅ Tier structure queries (Gold/Silver/Platinum benefits)
- ✅ Hotel spending calculations with travel category rates
- ✅ Feedback system functionality and data logging

## 📊 Advanced Analytics & Monitoring

### 🚀 Enhanced Analytics Dashboard (NEW!)
Run the comprehensive analytics dashboard:
```bash
streamlit run analytics_dashboard.py
```
**Features:**
- **Real-time Performance Metrics**: Response times, API usage, error tracking
- **Query Intelligence**: Intent detection accuracy, query patterns, complexity analysis
- **User Satisfaction Analysis**: Feedback trends, satisfaction by intent, card preferences
- **Interactive Visualizations**: Charts, graphs, and trend analysis
- **Advanced Export**: CSV downloads with rich analytics data

### Built-in Quick Dashboards
Access via URL parameters:
- **Enhanced Analytics**: `?admin=analytics` - Quick stats and dashboard links
- **Basic Feedback**: `?admin=feedback` - Simple feedback viewer
- **Export Options**: Download comprehensive analytics data as CSV

### Feedback Features
- **Thumbs Up/Down**: Quick feedback on each response
- **Improvement Suggestions**: Detailed feedback for negative responses
- **Session Tracking**: Basic session identification for feedback correlation
- **Persistent Storage**: JSON-based logging for feedback analysis

## 📝 License

This project is for educational and research purposes.

---

**Made with ❤️ for Indian credit card users**

## 🚀 Recent Updates

### v2.0 - Major UX & Analytics Update
- **Enhanced Currency Parsing**: Full support for "lakh", "crore" notation
- **Real-time Feedback System**: Thumbs up/down with improvement suggestions
- **Built-in Analytics**: Feedback dashboard accessible via URL parameter
- **Mobile Optimization**: Responsive design for all device sizes
- **Dual AI Support**: Gemini (primary) with OpenAI fallback
- **Improved Calculations**: Enhanced reward calculation accuracy

### Key Improvements
- ✅ Fixed currency parsing for Indian notation (5 lakh → ₹500,000)
- ✅ Enhanced mobile interface with touch-friendly controls
- ✅ Added comprehensive feedback collection system
- ✅ Improved reward calculation accuracy for all spending categories
- ✅ Added support for tier structure queries (Gold/Silver/Platinum)

## 🤝 Contributing

Feel free to submit issues and enhancement requests! This project is designed to help Indian credit card users make informed decisions.
