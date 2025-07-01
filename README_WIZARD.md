# 🧙‍♂️ Credit Card Wizard Assistant

## Overview

This is an enhanced version of the Credit Card Assistant that provides **two interaction modes**:

1. **🧙‍♂️ Guided Wizard Mode** - Step-by-step guided interface for accurate results
2. **💬 Chat Mode** - Traditional free-form conversation interface

## Why the Wizard Approach?

The original chat-based system faced challenges with:
- Text variations ("100k" vs "2L", "hotels" vs "hotel")  
- Intent detection conflicts
- Inconsistent results for similar queries
- Complex reward calculations with edge cases

The wizard approach solves these by:
- **Eliminating ambiguity** through structured selections
- **Focused context** with card-specific queries
- **Predictable results** for consistent user experience
- **Easy debugging** with clear decision paths

## Features

### 🧙‍♂️ Guided Wizard Mode
- **Step 1**: Card Selection (ICICI EPM, Axis Atlas, or Compare Both)
- **Step 2**: Query Category (Rewards, Travel, Fees, Spending, General)
- **Step 3**: Specific Topics (Category-specific subcategories)
- **Fallback**: "Ask Anything Else" uses the original chat engine

### 💬 Chat Mode  
- Free-form text input with natural language processing
- Quick action buttons for common queries
- Category buttons for popular topics
- All existing functionality from the original system

### 🔄 Hybrid Integration
- Seamless switching between modes
- Wizard's "Other" category routes to chat engine
- Best of both worlds approach

## Quick Start

### Option 1: Using the Wizard Interface
```bash
./launch_wizard.sh
```
Opens on http://localhost:8502

### Option 2: Using Original Chat Interface  
```bash
./launch_all.sh
```
Opens on http://localhost:8501

## Architecture

```
app_wizard.py (Main Entry Point)
├── utils/qa_wizard_engine.py (Guided Flow)
│   └── Falls back to → utils/qa_engine.py (Chat Engine)
└── utils/qa_engine.py (Original Chat Engine)
```

### Key Components

1. **CreditCardWizard** (`qa_wizard_engine.py`)
   - Manages step-by-step guided flow
   - Handles session state and navigation
   - Integrates with existing QA engine for "Other" queries

2. **RichDataCreditCardBot** (`qa_engine.py`)  
   - Original rule-based intent detection
   - Reward calculation engine
   - Natural language processing

3. **Dual Interface** (`app_wizard.py`)
   - Mode selection and switching
   - Unified UI with consistent styling
   - Session management

## Usage Examples

### Guided Wizard Flow
1. **Select Card**: "🏦 ICICI Emeralde Private Metal"
2. **Choose Category**: "🎯 Spending Categories" 
3. **Pick Topic**: "🏨 Hotels & Travel"
4. **Get Answer**: Structured response with fees, rewards, and calculations

### Chat Flow
- **Input**: "If I spend ₹2 lakhs on hotels, which card gives better rewards?"
- **Output**: Detailed comparison with calculations and winner determination

### Hybrid Flow
1. Start with wizard for card selection
2. Choose "💬 Ask Anything Else"
3. Use free-form text with card context pre-selected

## Configuration

### Data Files
- `data/axis-atlas.json` - Axis Bank Atlas card details
- `data/icici-epm.json` - ICICI Emeralde Private Metal details

### Environment Variables
- OpenAI API key for LLM responses
- Gemini API key (alternative LLM)

## Development

### Adding New Cards
1. Add card data to `/data/` directory
2. Update `self.cards` dictionary in `CreditCardWizard`
3. Add card selection button in `render_card_selection()`

### Adding New Categories
1. Update `self.query_categories` in `CreditCardWizard`
2. Add query mappings in `generate_structured_answer()`
3. Update subcategory rendering logic

### Extending Chat Integration
- Modify `render_free_form_input()` for enhanced free-form handling
- Update `generate_structured_answer()` for better query mapping
- Enhance context passing between wizard and chat engines

## Performance Benefits

### Wizard Mode
- **Faster**: No complex intent detection required
- **Accurate**: Structured selections eliminate ambiguity
- **Scalable**: Easy to add new cards/categories

### Chat Mode
- **Familiar**: Natural conversation flow
- **Flexible**: Handles complex, multi-part queries
- **Intelligent**: Advanced intent detection and entity extraction

## Migration from Original

The wizard interface is **fully backward compatible**:
- All original functionality preserved in chat mode
- Same data sources and calculation engines
- Identical API integrations
- No breaking changes to existing workflows

## Future Enhancements

1. **Smart Defaults**: Remember user preferences
2. **Advanced Calculations**: Multi-card spend optimization
3. **Visual Comparisons**: Charts and graphs for complex comparisons
4. **Export Features**: Save comparison results
5. **API Integration**: Real-time rate updates

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies installed via `requirements.txt`
2. **Port Conflicts**: Use different ports (8501 vs 8502) for parallel testing
3. **Session State**: Use "Reset Session" button to clear any stuck states
4. **API Keys**: Verify OpenAI/Gemini API keys are properly configured

### Debug Mode
Enable Streamlit debug mode:
```bash
streamlit run app_wizard.py --logger.level debug
```

## Contributing

1. Test both wizard and chat modes thoroughly
2. Maintain backward compatibility with original chat interface
3. Follow the hybrid architecture pattern
4. Update documentation for any new features

---

**Note**: This wizard interface complements rather than replaces the original chat system, providing users with choice based on their preference and query complexity. 