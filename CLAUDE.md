# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an Indian credit card comparison chatbot that helps users compare features between Axis Bank Atlas and ICICI Bank Emeralde Private Metal credit cards. The system uses a rule-based QA engine enhanced with AI (Gemini preferred, OpenAI fallback) for intelligent responses.

## 🚨 DEVELOPMENT WORKFLOW - ALWAYS FOLLOW THIS!

### Research → Plan → Implement
**NEVER JUMP STRAIGHT TO CODING!** Always follow this sequence:
1. **Research**: Explore the codebase, understand existing patterns, review test cases
2. **Plan**: Create detailed implementation plan with validation checkpoints
3. **Implement**: Execute the plan with testing and validation

When asked to implement any feature, always say: "Let me research the codebase and create a plan before implementing."

### Quality Gates - ALL MUST PASS ✅
**MANDATORY CHECKS BEFORE ANY COMMIT:**
```bash
# Run all quality checks
python -m pytest tests/ -v                # All tests must pass
python -m black --check .                 # Code formatting
python -m flake8 .                        # Linting
python test_runner.py                     # Project-specific tests (21 comprehensive test cases)
```

**ZERO TOLERANCE POLICY**: Fix ALL issues before continuing. No exceptions.

## Development Commands

### Running the Application
```bash
# Launch application (preferred method)
./launch.sh

# Alternative direct launch
streamlit run app.py --server.port=8501
```

### Testing
```bash
# Run automated test suite (21 comprehensive test cases)
python test_runner.py

# View test dashboard
# Open test_cases.html in browser

# Run specific test validation
python -c "from utils.qa_engine import process_query; print(process_query('your test query', []))"
```

### Code Quality
```bash
# Format code
python -m black .

# Check linting
python -m flake8 .

# Combined quality check
python -m black . && python -m flake8 . && python test_runner.py
```

## Architecture Overview

### Core Components

**`app.py`** (843 lines) - Main Streamlit web application
- Mobile-first responsive design with extensive custom CSS
- Real-time feedback system with thumbs up/down
- Collapsible quick questions interface  
- Admin dashboard accessible via `?admin=true` URL parameter
- Session management and chat history

**`utils/qa_engine.py`** (1,247 lines) - Core QA engine
- Sophisticated intent detection using regex patterns
- Currency preprocessing for Indian notation (lakh, crore, k)
- Complex reward calculation engine with category-specific logic
- Dual API support (Gemini preferred, OpenAI fallback)
- Comprehensive exclusion and capping logic

**Data Files:**
- `data/axis-atlas.json` - Structured Axis Bank Atlas card data
- `data/icici-epm.json` - Structured ICICI Emeralde Private Metal data
- Normalized JSON structure with consistent field mappings

### Technical Stack
- **Backend**: Python 3.x with Streamlit framework
- **AI Engine**: Primary support for Google Gemini, fallback to OpenAI GPT-4/3.5-turbo
- **Frontend**: Streamlit with extensive custom CSS for mobile-responsive design
- **Data Format**: Structured JSON files for card features and policies
- **Testing**: Custom automated test framework with HTML dashboard

### Key Data Flow

1. **User Query** → Intent Detection → Currency Preprocessing
2. **Context Building** → Card Data Extraction → Unified Rate Field Creation
3. **AI Processing** → Response Generation → Financial Calculation Validation
4. **Feedback Collection** → Analytics Storage → Improvement Tracking

## Code Quality Standards

### FORBIDDEN - NEVER DO THESE:
- **NO hardcoded API keys** - use environment variables
- **NO time.sleep()** in production code - use proper async patterns
- **NO** keeping old and new code together
- **NO** migration functions or compatibility layers
- **NO** versioned function names (processV2, handleNew)
- **NO** TODOs in final code
- **NO** print() statements in production - use proper logging

### Required Standards:
- **Delete** old code when replacing it
- **Meaningful names**: `user_query` not `query`, `card_data` not `data`
- **Early returns** to reduce nesting
- **Type hints** everywhere: `def process_query(query: str) -> dict:`
- **Proper error handling**: Use try/except with specific exceptions
- **Docstrings** for all functions and classes
- **Consistent formatting**: Use Black for code formatting

### Python-Specific Rules:
- **Use f-strings** for string formatting, not .format() or %
- **List comprehensions** over loops when appropriate
- **Context managers** for file operations and API calls
- **Proper exception handling** with specific exception types
- **Logging** instead of print statements
- **Environment variables** for configuration (never hardcode)

## Financial Calculation Logic

### Intent Categories
- `reward_calculation` - "What points for ₹50k spend on dining?"
- `redemption_query` - "What can I do with 5000 points?"
- `feature_comparison` - "Compare lounge access between cards"
- `general_query` - Basic card information requests

### Currency Preprocessing
- "3L" → 300,000
- "2 crore" → 20,000,000  
- "20k" → 20,000
- Handles Indian lakh/crore notation

### Reward Calculation Engine
- Category-specific earning rates with caps
- Tiered earning (e.g., Axis travel: 5x up to ₹2L monthly, then 2x)
- Exclusion handling for restricted categories
- Comparative analysis across cards

## Data Structure Standards

### Unified JSON Field Mapping
Both cards normalized to have consistent fields:
- `rate_general` - Base earning rate for general spends
- `value_per_point` - Redemption value per point/mile
- `accrual_exclusions` - Array of excluded categories
- `earning_rate` - Dynamically created unified rate field

### Key Card Data Points
**Axis Atlas:**
- 2 EDGE Miles per ₹100 general spend
- 5x miles for travel (up to ₹2L monthly cap, then 2x)
- Education NOT excluded
- ₹1 per EDGE Mile redemption value

**ICICI Emeralde Private Metal:**
- 6 points per ₹200 spend (effectively 3 points per ₹100)
- Education capped at 1000 points per cycle
- Multiple exclusions for government, rent, fuel
- Up to ₹1 per point redemption value

## Testing Strategy

### Test Coverage (21 Test Cases)
Current metrics: 83% pass rate with comprehensive coverage:
- Hotel/travel spending calculations
- Utility payment restrictions
- Reward rate comparisons
- Insurance premium handling
- Government spending exclusions
- Education fee calculations
- Category-specific caps and limits

### Testing Philosophy
- **Financial calculations** → Write tests first (accuracy is critical)
- **API endpoints** → Write tests after implementation
- **Edge cases** → Comprehensive coverage for Indian currency, card variations
- **User experience** → Test mobile interface and feedback system

### Code Completion Standards
- ✅ All linters pass with zero issues
- ✅ All tests pass (both automated and manual)
- ✅ Feature works end-to-end
- ✅ Old code is deleted
- ✅ Proper documentation on all functions

## Problem-Solving Framework

### When stuck or confused:
1. **Stop** - Don't spiral into complex solutions
2. **Step back** - Re-read the test cases and requirements
3. **Simplify** - The simple solution is usually correct
4. **Test** - Validate assumptions with `test_runner.py`
5. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"

### Common Issues & Solutions

**Currency Parsing Issues**: Check `preprocess_currency_abbreviations()` method
**Intent Detection Problems**: Review regex patterns in `qa_engine.py`
**Data Access Issues**: Normalize JSON field names rather than updating prompts
**Test Failures**: Run `python test_runner.py` for detailed failure analysis

## AI Integration

### Dual API Support
- **Primary**: Google Gemini (gemini-1.5-pro)
- **Fallback**: OpenAI GPT-4/3.5-turbo
- Environment variables: `GEMINI_API_KEY`, `OPENAI_API_KEY`

### System Prompt Engineering
- Include explicit instructions for finding rates in different JSON structures
- Provide concrete examples of rate extraction
- Never allow "no rate provided" responses when data exists
- Include conversation context for follow-up questions

## User Experience Features

### Mobile-First Design
- Responsive CSS with extensive customization
- Touch-friendly interface elements
- Collapsible quick questions (auto-hide after first interaction)
- Dark mode compatibility

### Real-Time Feedback System
- Thumbs up/down buttons on each response
- Improvement suggestions for negative feedback
- Session tracking with persistent JSON storage
- Admin analytics dashboard with CSV export

## Key Learnings

1. **Data Structure Consistency**: When AI can't find card data, normalize JSON field names between cards rather than updating AI prompts
2. **Intent Detection**: Use broad pattern matching for user query variations and handle Indian currency notation
3. **Reward Calculation**: Always check for category caps and exclusions, handle tiered earning rates
4. **System Prompts**: Include explicit instructions and concrete examples for rate extraction

## Performance & Security

### Performance Standards
- Response time target: < 3 seconds
- API rate limiting considerations
- Efficient JSON data structure loading
- Streamlit session state management

### Security Measures
- Environment variable management for API keys
- Input validation and sanitization
- No sensitive information logging
- Secure session handling

## Scaling Considerations

### Adding New Cards
1. Create similar JSON structure in `data/` directory
2. Update data mapping in `qa_engine.py`
3. Add test cases for new card scenarios
4. Update unified field extraction logic

### Enhancing AI Features
- Consider RAG implementation for complex queries
- Fine-tuning opportunities for domain-specific responses
- Multi-language support for Hindi/regional languages
- Web search fallback for low-confidence responses

## Quick Reference

```bash
# Environment Setup
pip install -r requirements.txt

# Development Workflow
./launch.sh                    # Launch app
python test_runner.py         # Run tests
python -m black .             # Format code
python -m flake8 .            # Lint code

# Access Points
http://localhost:8501         # Main app
http://localhost:8501?admin=true  # Admin dashboard
```

## Final Notes

This system demonstrates effective rule-based AI for financial domain applications where accuracy is paramount. The codebase prioritizes:
- **Accuracy over flexibility** in financial calculations
- **Mobile-first user experience** with real-time feedback
- **Comprehensive testing** with automated validation
- **Clean architecture** with clear separation of concerns

Remember: Simple code is easier to maintain and debug. In financial applications, being correct is more important than being clever. 