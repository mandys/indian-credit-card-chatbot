# Credit Card Features Chatbot - Project Summary for Claude Code

## Project Overview
This is an Indian credit card comparison chatbot that helps users compare features between Axis Bank Atlas and ICICI Bank Emeralde Private Metal credit cards. The system uses a rule-based QA engine with GPT-4 for intelligent responses.

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
python test_runner.py                     # Project-specific tests
```

**ZERO TOLERANCE POLICY**: Fix ALL issues before continuing. No exceptions.

### Working Memory Management
Maintain **TODO.md** for active development:
```markdown
## Current Task
- [ ] What we're doing RIGHT NOW

## Completed  
- [x] What's actually done and tested

## Next Steps
- [ ] What comes next

## Blockers
- [ ] Issues requiring attention
```

## Key Files & Architecture

### Core Application Files
- **`app.py`** - Main Flask web application with chatbot interface
- **`utils/qa_engine.py`** - Core QA engine with intent detection and response generation
- **`data/axis-atlas.json`** - Axis Bank Atlas card structured data
- **`data/icici-epm.json`** - ICICI Bank Emeralde Private Metal card structured data
- **`launch.sh`** - Application launcher script
- **`requirements.txt`** - Python dependencies

### Testing & Quality Assurance
- **`test_cases.html`** - Manual test interface with 18 comprehensive test cases
- **`test_runner.py`** - Automated test runner with pass/fail reporting
- **`test_report_*.txt`** - Historical test results (83% pass rate)

## Technical Stack
- **Backend**: Python 3.x, Flask framework
- **AI Engine**: OpenAI GPT-4 via API
- **Frontend**: HTML5, CSS3 (Bootstrap), Vanilla JavaScript
- **Data Format**: Structured JSON for card features
- **Testing**: Custom test framework with automated validation

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

## Core Functionality Flow

### 1. User Query Processing (`qa_engine.py`)
```python
process_query(user_query, conversation_history) → response
```

**Intent Detection Pipeline:**
- Currency preprocessing (3L → 300000, 20k → 20000)
- Pattern matching for reward calculations, redemptions, comparisons
- Spend amount extraction with Indian currency notation support
- Card name detection (axis/atlas vs icici/emeralde)

**Key Intent Categories:**
- `reward_calculation` - "What points for ₹50k spend on dining?"
- `redemption_query` - "What can I do with 5000 points?"
- `feature_comparison` - "Compare lounge access between cards"
- `general_query` - Basic card information requests

### 2. Data Retrieval & Context Building
- Extracts relevant card data based on detected intent
- Creates unified `earning_rate` field from different JSON structures
- Handles category-specific caps and exclusions
- Builds comprehensive context for AI processing

### 3. AI Response Generation
- Uses GPT-4 with structured system prompts
- Includes card data, user query, and conversation history
- Handles complex calculations (reward rates, caps, comparisons)
- Provides actionable recommendations

## Critical JSON Data Structure

### Unified Field Mapping (Important for AI comprehension)
Both cards normalized to have consistent fields:
- `rate_general` - Base earning rate for general spends
- `value_per_point` - Redemption value per point/mile
- `accrual_exclusions` - Array of excluded categories
- `earning_rate` - Dynamically created unified rate field

### Key Data Points
**Axis Atlas:**
- 2 EDGE Miles per ₹100 general spend
- 5x miles for travel (up to ₹2L spend cap, then 2x)
- Education NOT excluded
- ₹1 per EDGE Mile redemption value

**ICICI Emeralde Private Metal:**
- 6 points per ₹200 spend (effectively 3 points per ₹100)
- Education capped at 1000 points per cycle
- Multiple exclusions for government, rent, fuel, etc.
- Up to ₹1 per point redemption value

## Testing Strategy & Implementation Standards

### Our code is complete when:
- ✅ All linters pass with zero issues
- ✅ All tests pass (both automated and manual)
- ✅ Feature works end-to-end
- ✅ Old code is deleted
- ✅ Proper documentation on all functions

### Testing Philosophy
- **Financial calculations** → Write tests first (accuracy is critical)
- **Simple API endpoints** → Write tests after
- **Hot paths** → Add performance tests
- **Edge cases** → Comprehensive coverage for Indian currency, card variations

### Manual Testing (`test_cases.html`)
18 comprehensive test cases covering:
- Basic card information queries
- Reward calculations with various spend amounts
- Category-specific earning rates and caps
- Redemption value calculations
- Complex comparison scenarios
- Edge cases (excluded categories, spending caps)

### Automated Testing (`test_runner.py`)
- Runs all test cases programmatically
- Validates expected vs actual responses
- Generates detailed pass/fail reports
- Current metrics: 18 tests, 83% pass rate

## Problem-Solving Framework

### When stuck or confused:
1. **Stop** - Don't spiral into complex solutions
2. **Step back** - Re-read the requirements and test cases
3. **Simplify** - The simple solution is usually correct
4. **Test** - Validate assumptions with quick tests
5. **Ask** - "I see two approaches: [A] vs [B]. Which do you prefer?"

### Debugging Protocol:
1. **Reproduce** the issue with specific test case
2. **Isolate** the problem (intent detection vs data retrieval vs AI generation)
3. **Verify** the fix with both automated and manual tests
4. **Document** the solution in this file

## Recent Bug Fixes Implemented

### 1. Currency Preprocessing Enhancement
**Problem**: "3L" parsed as "3" instead of "300000"
**Solution**: Added `preprocess_currency_abbreviations()` method

### 2. Intent Detection Improvements  
**Problem**: Reward calculation queries not detected properly
**Solution**: Enhanced pattern matching for spend-based queries

### 3. JSON Structure Normalization
**Problem**: Axis data in `others_rate` while ICICI in `rate_general`
**Solution**: Created unified `earning_rate` field extraction

### 4. Education Spending Logic
**Problem**: AI incorrectly stating "no general rate" for Axis Atlas
**Solution**: Updated system prompts to check multiple rate fields

## Key Learnings & Best Practices

### 1. Data Structure Consistency
**Critical Rule**: When AI can't find card data, normalize JSON field names between cards rather than updating AI prompts. This solves 90% of data access issues.

### 2. Intent Detection Patterns
- Use broad pattern matching for user query variations
- Handle Indian currency notation (L for lakh, Cr for crore)
- Distinguish between earning vs redemption queries
- Account for category-specific language variations

### 3. Reward Calculation Logic
- Always check for category caps and exclusions
- Handle tiered earning rates (e.g., Axis travel: 5x up to cap, then 2x)
- Include comparative analysis when multiple cards mentioned
- Provide concrete examples with spend amounts

### 4. System Prompt Engineering
- Include explicit instructions for finding rates in different JSON structures
- Provide concrete examples of rate extraction
- Never allow "no rate provided" responses when data exists
- Include conversation context for follow-up questions

## Performance & Security Standards

### **Measure First**:
- No premature optimization
- Profile API response times before claiming performance issues
- Use proper logging to identify actual bottlenecks

### **Security Always**:
- Validate all user inputs (sanitize queries, check spend amounts)
- Use environment variables for API keys
- Implement rate limiting for API calls
- Never log sensitive information (API keys, user data)

### **Error Handling**:
- Graceful degradation when GPT-4 API is unavailable
- Meaningful error messages for users
- Comprehensive logging for debugging

## Communication Protocols

### Progress Updates:
```
✅ Implemented currency preprocessing (all tests passing)
✅ Added intent detection for reward calculations
❌ Found issue with education spending logic - investigating
```

### Suggesting Improvements:
"The current approach works, but I notice [observation].
Would you like me to [specific improvement]?"

## Scaling Considerations

### Current Architecture Benefits
- Rule-based engine ensures financial accuracy
- Structured JSON allows easy addition of new cards
- Comprehensive test coverage validates changes
- Clear separation of data and logic

### Future Enhancement Options
1. **Adding New Cards**: Create similar JSON structure, update data mapping
2. **Advanced AI Features**: Consider fine-tuning or RAG for complex queries
3. **Web Search Fallback**: Implement for low-confidence responses
4. **Multi-language Support**: Extend for Hindi/regional languages

## Quick Start Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Launch application
./launch.sh

# Run automated tests
python test_runner.py

# Run full quality check
python -m black . && python -m flake8 . && python test_runner.py

# Access manual test interface
# Navigate to /test in running application
```

## Performance Metrics
- Response time: < 3 seconds average
- Test pass rate: 83% (15/18 tests)
- Supported cards: 2 (Axis Atlas, ICICI EPM)
- Query types handled: 4 major intent categories
- Data coverage: Comprehensive card features, fees, rewards, benefits

## Final Notes

This system demonstrates effective rule-based AI for financial domain applications where accuracy is paramount over flexibility. 

**Remember**: Simple code is easier to maintain and debug. Write code for humans first, computers second. Add complexity only when justified by requirements.

When in doubt, prioritize accuracy over cleverness - in financial applications, being correct is more important than being elegant. 