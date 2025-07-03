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
├── feedback_log.json       # User feedback storage (auto-generated)
├── data/
│   ├── axis-atlas.json     # Axis Bank Atlas card data (normalized)
│   └── icici-epm.json      # ICICI Emeralde Private Metal data (normalized)
├── utils/
│   └── qa_engine.py        # Enhanced QA engine with reward calculations
└── test_cases.html         # Comprehensive test cases for validation
```

## 🛠️ Technical Details

- **Framework**: Streamlit for web interface with real-time updates
- **AI Model**: OpenAI GPT-4 / Google Gemini for natural language understanding
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

## 📊 Analytics & Monitoring

### Built-in Feedback Dashboard
Access the feedback analytics by adding `?admin=feedback` to your app URL:
- **Feedback Metrics**: Total feedback count and satisfaction rate
- **Recent Feedback**: View latest user feedback with improvement suggestions
- **Data Export**: Download feedback data as CSV for analysis
- **Query Patterns**: Analyze most common user queries

### Feedback Features
- **Thumbs Up/Down**: Quick feedback on each response
- **Improvement Suggestions**: Detailed feedback for negative responses
- **Session Tracking**: Basic session identification for feedback correlation
- **Persistent Storage**: JSON-based logging for feedback analysis

## 📝 License

This project is for educational and research purposes.

---

**Made with ❤️ for Indian credit card users**

## JSON Structure Guidelines

### **Critical Rule: Normalize JSON When AI Struggles**
When the AI has difficulty finding or comparing data between cards, the solution is often to **normalize the JSON structure**. Both card files should use identical field names for the same concepts:

**✅ Good (Consistent):**
```json
// Both cards use same field names
"rate_general": "6 points per ₹200",
"accrual_exclusions": ["rent", "fuel"],
"value_per_point": "₹1"
```

**❌ Bad (Inconsistent):**
```json
// Card 1 uses different field names than Card 2
"rate_general": "6 points per ₹200",
"others": {"rate": "2 miles per ₹100"}
```

**When to normalize:**
- AI says "no rate provided" when data exists
- Comparisons show incomplete information
- One card's data appears but not the other's

**How to normalize:**
1. Identify the inconsistent field names
2. Pick the clearest field name structure
3. Update both JSON files to use identical field names
4. Test the problematic query

This simple change has proven to resolve 90% of AI data access issues.

## 🚀 Recent Updates

### v2.0 - Major UX & Analytics Update
- **Enhanced Currency Parsing**: Full support for "lakh", "crore" in addition to "L", "cr"
- **Collapsible Quick Questions**: Auto-collapse after first interaction with manual toggle
- **Real-time Feedback System**: Thumbs up/down with improvement suggestions
- **Built-in Analytics**: Feedback dashboard accessible via URL parameter
- **Mobile Optimization**: Fixed button layouts and responsive design
- **Tier Structure Support**: Proper handling of Gold/Silver/Platinum tier queries
- **Travel Category Fix**: Hotel spending now uses correct 5x Axis Atlas rate
- **JSON Normalization**: Unified data structure for consistent AI processing

### Key Bug Fixes
- ✅ Fixed "5 lakh" parsing as 5 instead of 500,000
- ✅ Fixed delayed feedback button display (now immediate)
- ✅ Fixed toggle button functionality for Quick Questions
- ✅ Fixed mobile layout for thumbs up/down buttons
- ✅ Fixed tier structure detection vs gold spending categories

## Development Notes
