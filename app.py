import streamlit as st
import re
import os
import json
import time
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Credit Card Assistant",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for mobile-first, dark mode compatible design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Import system fonts for better mobile rendering */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Main container - mobile first */
    .main .block-container {
        padding: 1rem 0.75rem !important;
        max-width: 100% !important;
    }
    
    /* Desktop adjustments */
    @media (min-width: 768px) {
        .main .block-container {
            padding: 2rem 1.5rem !important;
            max-width: 800px !important;
        }
    }
    
    /* Header styling - responsive and theme aware */
    h1 {
        font-size: 1.75rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
        font-weight: 700 !important;
    }
    
    @media (min-width: 768px) {
        h1 {
            font-size: 2.25rem !important;
        }
    }
    
    .subtitle {
        font-size: 0.95rem;
        text-align: center;
        margin-bottom: 1.5rem;
        opacity: 0.8;
        font-weight: 400;
    }
    
    /* Card info styling - adaptive to theme */
    .card-info {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white !important;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
    }
    
    .card-info h4 {
        margin: 0 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: white !important;
    }
    
    @media (min-width: 768px) {
        .card-info h4 {
            font-size: 1.1rem !important;
        }
    }
    
    /* Quick questions section - mobile optimized and collapsible */
    .quick-questions {
        padding: 0.75rem;
        margin-bottom: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        background: rgba(59, 130, 246, 0.05);
        transition: all 0.3s ease;
    }
    
    .quick-questions.collapsed {
        margin-bottom: 0.75rem;
        padding: 0.5rem 0.75rem;
    }
    
    .quick-questions h3 {
        font-size: 0.9rem !important;
        margin: 0.5rem 0 !important;
        text-align: center;
        font-weight: 600 !important;
        color: #3b82f6 !important;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .quick-questions.collapsed h3 {
        margin: 0 !important;
        font-size: 0.8rem !important;
    }
    
    @media (min-width: 768px) {
        .quick-questions h3 {
            font-size: 1rem !important;
        }
        .quick-questions.collapsed h3 {
            font-size: 0.85rem !important;
        }
    }
    
    /* Feedback buttons styling */
    .feedback-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 0.75rem;
        justify-content: flex-end;
        opacity: 0.7;
        transition: opacity 0.2s ease;
    }
    
    .feedback-buttons:hover {
        opacity: 1;
    }
    
    .feedback-btn {
        background: none !important;
        border: 1px solid rgba(107, 114, 128, 0.3) !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        font-size: 0.8rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        min-height: auto !important;
        height: auto !important;
        width: auto !important;
        flex-shrink: 0 !important; /* Prevent buttons from shrinking */
    }
    
    /* Desktop: Keep buttons close together */
    div[data-testid="stHorizontalBlock"]:has(button[key*="thumbs_"]) {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-end !important;
        gap: 12px !important;
        padding: 0 !important;
        margin: 8px 0 0 0 !important;
    }
    
    /* Compact feedback button columns on desktop */
    div[data-testid="column"]:has(button[key*="thumbs_up"]),
    div[data-testid="column"]:has(button[key*="thumbs_down"]) {
        flex: 0 0 60px !important;
        min-width: 60px !important;
        max-width: 60px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Style buttons for all screens */
    button[key*="thumbs_up"],
    button[key*="thumbs_down"] {
        width: 56px !important;
        height: 42px !important;
        padding: 0 !important;
        font-size: 1.2rem !important;
        border-radius: 8px !important;
        border: 1px solid rgba(107, 114, 128, 0.3) !important;
        background: rgba(249, 250, 251, 0.8) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Hover effects */
    button[key*="thumbs_up"]:hover {
        background: rgba(34, 197, 94, 0.1) !important;
        border-color: rgba(34, 197, 94, 0.3) !important;
        transform: scale(1.05) !important;
    }
    
    button[key*="thumbs_down"]:hover {
        background: rgba(239, 68, 68, 0.1) !important;
        border-color: rgba(239, 68, 68, 0.3) !important;
        transform: scale(1.05) !important;
    }
    
    /* Mobile: Even more compact */
    @media (max-width: 768px) {
        /* Target feedback button containers specifically */
        div[data-testid="stHorizontalBlock"]:has(button[key*="thumbs_"]) {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 8px !important;
            padding: 0 !important;
            margin: 8px 0 0 0 !important;
        }
        
        /* Make the spacer column compress on mobile */
        div[data-testid="column"]:first-child:has(~ div[data-testid="column"] button[key*="thumbs_"]) {
            flex: 1 !important;
            min-width: 0 !important;
        }
        
        /* Compact feedback button columns */
        div[data-testid="column"]:has(button[key*="thumbs_up"]),
        div[data-testid="column"]:has(button[key*="thumbs_down"]) {
            flex: 0 0 50px !important;
            min-width: 50px !important;
            max-width: 50px !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Style the buttons themselves */
        button[key*="thumbs_up"],
        button[key*="thumbs_down"] {
            width: 48px !important;
            height: 40px !important;
            padding: 0 !important;
            font-size: 1.1rem !important;
            border-radius: 8px !important;
            border: 1px solid rgba(107, 114, 128, 0.3) !important;
            background: rgba(249, 250, 251, 0.8) !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* Remove default button margins */
        .stButton:has(button[title*="helpful"]),
        .stButton:has(button[title*="improvement"]) {
            margin: 0 !important;
            width: 50px !important;
        }
    }
    
    .feedback-btn:hover {
        background: rgba(59, 130, 246, 0.1) !important;
        border-color: #3b82f6 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    .feedback-btn.positive {
        color: #059669 !important;
        border-color: rgba(5, 150, 105, 0.3) !important;
    }
    
    .feedback-btn.positive:hover {
        background: rgba(5, 150, 105, 0.1) !important;
        border-color: #059669 !important;
    }
    
    .feedback-btn.negative {
        color: #dc2626 !important;
        border-color: rgba(220, 38, 38, 0.3) !important;
    }
    
    .feedback-btn.negative:hover {
        background: rgba(220, 38, 38, 0.1) !important;
        border-color: #dc2626 !important;
    }
    
    /* Button styling - mobile-first touch-friendly */
    .stButton > button {
        width: 100% !important;
        height: auto !important;
        min-height: 44px !important; /* Reduced from 48px */
        padding: 10px 14px !important; /* Reduced padding */
        border-radius: 10px !important; /* Slightly smaller radius */
        font-size: 0.85rem !important; /* Smaller text */
        font-weight: 500 !important;
        text-align: center !important; /* Center text for compact buttons */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important; /* Center content */
        transition: all 0.2s ease !important;
        border: 2px solid transparent !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1) !important; /* Smaller shadow */
        background: rgba(255, 255, 255, 0.95) !important;
        color: #374151 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Compact button styling for collapsed state */
    .quick-questions.collapsed .stButton > button {
        min-height: 36px !important;
        padding: 8px 12px !important;
        font-size: 0.8rem !important;
    }
    
    /* Dark mode button styling */
    @media (prefers-color-scheme: dark) {
        .stButton > button {
            background: rgba(31, 41, 55, 0.95) !important;
            color: #f3f4f6 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            border: 2px solid rgba(75, 85, 99, 0.3) !important;
        }
        
        .stButton > button:hover {
            background: rgba(55, 65, 81, 0.95) !important;
            border-color: #3b82f6 !important;
            color: #60a5fa !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
        }
        
        .quick-questions {
            background: rgba(31, 41, 55, 0.3) !important;
            border: 1px solid rgba(75, 85, 99, 0.3) !important;
        }
    }
    
    /* Light mode hover effects */
    .stButton > button:hover {
        background: rgba(249, 250, 251, 0.98) !important;
        border-color: #3b82f6 !important;
        color: #1e40af !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.25) !important;
    }
    
    /* Desktop button improvements */
    @media (min-width: 768px) {
        .stButton > button {
            min-height: 48px !important; /* Reduced from 52px */
            padding: 12px 16px !important; /* Reduced padding */
            font-size: 0.9rem !important; /* Slightly smaller */
        }
        
        .quick-questions.collapsed .stButton > button {
            min-height: 40px !important;
            padding: 10px 14px !important;
            font-size: 0.85rem !important;
        }
    }
    
    /* Reduce chat message spacing for better density */
    .stChatMessage {
        padding: 0.5rem !important; /* Reduced from 0.75rem */
        margin-bottom: 0.25rem !important; /* Reduced from 0.5rem */
        border-radius: 12px !important;
    }
    
    /* Reduce element container spacing */
    .element-container {
        margin-bottom: 0.5rem !important; /* Reduced spacing */
    }
    
    /* Chat input styling - mobile friendly */
    .stChatInput > div > div > div > div {
        border-radius: 16px !important;
        border: 2px solid #e5e7eb !important;
        min-height: 48px !important;
        font-size: 1rem !important;
    }
    
    .stChatInput > div > div > div > div:focus-within {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Dark mode input styling */
    @media (prefers-color-scheme: dark) {
        .stChatInput > div > div > div > div {
            background: rgba(31, 41, 55, 0.8) !important;
            border: 2px solid rgba(75, 85, 99, 0.5) !important;
            color: #f3f4f6 !important;
        }
        
        .stChatInput > div > div > div > div:focus-within {
            border-color: #60a5fa !important;
            box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2) !important;
        }
    }
    
    /* Tips section - theme adaptive */
    .tips-section {
        padding: 12px 16px;
        margin-top: 1rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        color: #92400e;
    }
    
    @media (prefers-color-scheme: dark) {
        .tips-section {
            background: linear-gradient(135deg, rgba(146, 64, 14, 0.2) 0%, rgba(180, 83, 9, 0.15) 100%);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fbbf24;
        }
    }
    
    /* Chat message improvements for mobile */
    .stChatMessage {
        padding: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        border-radius: 12px !important;
    }
    
    /* Loading spinner improvements */
    .stSpinner {
        border-color: #3b82f6 !important;
    }
    
    /* Hide scrollbar on mobile for cleaner look */
    @media (max-width: 768px) {
        .main {
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        
        .main::-webkit-scrollbar {
            display: none;
        }
    }
    
    /* Improved spacing for mobile */
    @media (max-width: 768px) {
        .element-container {
            margin-bottom: 0.75rem !important;
        }
        
        div[data-testid="column"] {
            padding: 0 0.25rem !important;
        }
    }
    
    /* Desktop column padding */
    @media (min-width: 768px) {
        div[data-testid="column"] {
            padding: 0 0.5rem !important;
        }
    }
    
    /* Target feedback buttons specifically */
    button[key*="thumbs_up"], button[key*="thumbs_down"] {
        width: 44px !important;
        height: 36px !important;
        min-width: 44px !important;
        max-width: 44px !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Force columns containing feedback buttons to stay side-by-side */
    div[data-testid="column"]:has(button[key*="thumbs_"]) {
        flex: 0 0 auto !important;
        width: 50px !important;
        min-width: 50px !important;
        max-width: 50px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the pure AI bot
@st.cache_resource
def load_bot():
    """Loads the AI-powered credit card bot for query processing."""
    from utils.ai_powered_qa_engine import create_ai_powered_bot
    
    # Use 100% AI approach for better accuracy and maintainability
    ai_bot = create_ai_powered_bot(
        data_files=["data/axis-atlas.json", "data/icici-epm.json"]
    )
    
    return ai_bot

class QueryEnhancer:
    """Enhances user queries using lessons learned from wizard fixes."""
    
    def __init__(self):
        # Query patterns that work well (learned from wizard fixes)
        self.patterns = {
            'annual_fee': [
                'annual fee', 'yearly fee', 'joining fee', 'membership fee'
            ],
            'reward_rates': [
                'reward rate', 'points rate', 'miles rate', 'earning rate', 'rewards'
            ],
            'lounge_access': [
                'lounge', 'airport lounge', 'lounge access', 'lounge benefit'
            ],
            'welcome_benefits': [
                'welcome benefit', 'joining benefit', 'signup bonus', 'welcome bonus'
            ],
            'eligibility': [
                'eligibility', 'who can apply', 'requirements', 'qualify'
            ],
            'milestones': [
                'milestone', 'spending milestone', 'bonus miles', 'bonus points'
            ],
            'utility_spending': [
                'utility', 'electricity', 'gas bill', 'phone bill', 'broadband'
            ],
            'fuel_spending': [
                'fuel', 'petrol', 'diesel', 'gas station'
            ],
            'insurance_spending': [
                'insurance premium', 'insurance payment', 'insurance'
            ],
            'travel_benefits': [
                'travel insurance', 'travel benefit', 'airline', 'hotel booking'
            ]
        }
        
        # Improved query templates (learned from wizard)
        self.templates = {
            'annual_fee': "What are the annual fees for {}?",
            'reward_rates': "What are the reward rates for {}?", 
            'lounge_access': "What are the airport lounge access benefits for {}?",
            'welcome_benefits': "What are the welcome benefits for {}?",
            'eligibility': "What are the eligibility requirements for {}?",
            'milestones': "Tell me about {} milestones",
            'utility_spending': "What are the rewards and fees for utility payments on {}?",
            'fuel_spending': "What are the rewards and fees for fuel purchases on {}?",
            'insurance_spending': "What are the rewards and fees for insurance payments on {}?",
            'travel_benefits': "What travel benefits does {} offer?"
        }
    
    def preprocess_currency_abbreviations(self, query: str) -> str:
        """Convert Indian currency abbreviations to proper numerical values."""
        import re
        
        # Define mappings for Indian currency abbreviations
        abbreviations = {
            r'(\d+(?:\.\d+)?)\s*(?:crore|crores|cr)\b': lambda m: str(int(float(m.group(1)) * 10000000)),  # crore
            r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)\b': lambda m: str(int(float(m.group(1)) * 100000)),       # lakh  
            r'(\d+(?:\.\d+)?)\s*(?:thousand|k)\b': lambda m: str(int(float(m.group(1)) * 1000)),           # thousand
        }
        
        result = query.lower()
        for pattern, replacement in abbreviations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def enhance_query(self, query: str) -> str:
        """Enhance user query using proven patterns."""
        # First, preprocess currency abbreviations
        query = self.preprocess_currency_abbreviations(query)
        query_lower = query.lower()
        
        # Extract card names
        card_names = []
        if 'axis' in query_lower or 'atlas' in query_lower:
            card_names.append('Axis Bank Atlas')
        if 'icici' in query_lower or 'emeralde' in query_lower:
            card_names.append('ICICI Emeralde Private Metal')
        
        # If no specific card mentioned, keep original query
        if not card_names:
            return query
            
        # Detect query intent and apply template
        for intent, keywords in self.patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                if intent in self.templates:
                    if len(card_names) == 1:
                        enhanced = self.templates[intent].format(card_names[0])
                        return enhanced
                    else:
                        # Multi-card comparison - keep original
                        return query
        
        # No pattern matched, return original
        return query

def log_feedback(query: str, response: str, feedback_type: str, improvement_suggestion: str = ""):
    """Log user feedback with comprehensive analytics for self-learning."""
    import datetime
    import json
    import os
    import re
    import time
    
    # Record timing for analytics
    start_time = time.time()
    
    # Analyze the query for comprehensive analytics
    try:
        # Initialize a temporary bot instance for analytics (reuse session bot if available)
        if not hasattr(st.session_state, 'analytics_bot'):
            from utils.qa_engine import RichDataCreditCardBot
            st.session_state.analytics_bot = RichDataCreditCardBot([
                "data/axis-atlas.json", 
                "data/icici-epm.json"
            ])
        
        bot = st.session_state.analytics_bot
        
        # Preprocess query like the main engine does
        processed_query = bot.preprocess_currency_abbreviations(query.lower())
        
        # Detect intent and extract analytics
        intent_detected = bot.detect_intent(processed_query)
        cards_mentioned = bot.extract_card_names(query.lower())
        
        # Extract spending amount if present
        spend_amount = None
        amount_patterns = [
            r'₹?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lakh|l\b)',
            r'₹?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr\b)',
            r'₹?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:thousand|k\b)',
            r'₹(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*rupees?'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, processed_query, re.IGNORECASE)
            if match:
                spend_amount = match.group(1).replace(',', '')
                break
        
        # Detect spending categories mentioned
        categories_mentioned = []
        category_keywords = {
            'travel': ['travel', 'flight', 'airline', 'hotel', 'booking', 'vacation'],
            'dining': ['dining', 'restaurant', 'food', 'zomato', 'swiggy'],
            'fuel': ['fuel', 'petrol', 'diesel', 'gas', 'station'],
            'grocery': ['grocery', 'supermarket', 'vegetables', 'provisions'],
            'utility': ['utility', 'electricity', 'water', 'mobile', 'internet'],
            'education': ['education', 'school', 'college', 'university', 'fees'],
            'insurance': ['insurance', 'premium', 'policy'],
            'government': ['government', 'tax', 'municipal', 'challan']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in processed_query for keyword in keywords):
                categories_mentioned.append(category)
        
        # Query complexity analysis
        query_complexity = {
            'word_count': len(query.split()),
            'has_comparison': any(word in query.lower() for word in ['better', 'vs', 'compare', 'which']),
            'has_calculation': any(word in query.lower() for word in ['spend', 'points', 'miles', 'rewards']),
            'has_conditional': any(word in query.lower() for word in ['if', 'when', 'what if'])
        }
        
        # Enhanced analytics
        query_analytics = {
            'intent_detected': intent_detected or 'unknown',
            'intent_confidence': 1.0 if intent_detected else 0.0,  # Simple confidence for now
            'cards_mentioned': cards_mentioned,
            'spend_amount': spend_amount,
            'categories_mentioned': categories_mentioned,
            'query_complexity': query_complexity,
            'query_length': len(query),
            'processing_time_ms': round((time.time() - start_time) * 1000, 2)
        }
        
    except Exception as e:
        # Fallback analytics if analysis fails
        query_analytics = {
            'intent_detected': 'analysis_failed',
            'intent_confidence': 0.0,
            'cards_mentioned': [],
            'spend_amount': None,
            'categories_mentioned': [],
            'query_complexity': {'word_count': len(query.split())},
            'query_length': len(query),
            'processing_time_ms': 0,
            'analysis_error': str(e)
        }
    
    # Enhanced feedback entry with comprehensive analytics
    feedback_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "response": response[:500] + "..." if len(response) > 500 else response,
        "feedback": feedback_type,
        "improvement_suggestion": improvement_suggestion,
        "session_id": id(st.session_state),
        # NEW: Comprehensive query analytics
        "analytics": query_analytics,
        "user_journey": {
            "messages_in_session": len(st.session_state.get('messages', [])),
            "feedback_given_count": len(st.session_state.get('feedback_log', [])),
            "session_duration_minutes": round((time.time() - st.session_state.get('session_start', time.time())) / 60, 2)
        }
    }
    
    # Append to session state
    st.session_state.feedback_log.append(feedback_entry)
    
    # Also log to persistent storage (works across Streamlit deployments)
    try:
        from persistent_storage import storage_manager
        
        # Load existing feedback
        existing_feedback = storage_manager.load_feedback_data()
        existing_feedback.append(feedback_entry)
        
        # Save back to persistent storage
        storage_manager.save_feedback_data(existing_feedback)
        
    except Exception as e:
        # Fallback to local file
        feedback_file = "feedback_log.json"
        try:
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r') as f:
                    existing_feedback = json.load(f)
            else:
                existing_feedback = []
            
            existing_feedback.append(feedback_entry)
            
            with open(feedback_file, 'w') as f:
                json.dump(existing_feedback, f, indent=2)
        except Exception:
            # Fail silently to not disrupt user experience
            pass

def main():
    """Enhanced main function with better UX."""
    
    # Header
    st.title("💳 Credit Card Assistant")
    st.markdown('<div class="subtitle">Smart AI assistant for Indian credit cards</div>', unsafe_allow_html=True)
    
    # Card info section
    st.markdown("""
    <div class="card-info">
        <h4>🏦 Supported Cards: Axis Bank Atlas • ICICI Emeralde Private Metal</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize bot and query enhancer
    bot = load_bot()
    enhancer = QueryEnhancer()
    
    # Admin controls and analytics viewer (accessible via URL parameter)
    query_params = st.query_params
    if query_params.get("admin") == "engine":
        # Engine testing dashboard
        st.title("⚙️ Engine Testing Dashboard")
        st.markdown("### 🔧 Engine Control Panel")
        
        # Show current engine stats
        stats = bot.get_engine_stats()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("AI Rollout %", f"{stats['ai_rollout_percentage']}%")
        with col2:
            st.metric("AI Engine", "✅ Available" if stats['ai_engine_available'] else "❌ Unavailable")
        with col3:
            st.metric("Regex Engine", "✅ Available" if stats['regex_engine_available'] else "❌ Unavailable")
        
        st.markdown("---")
        
        # Engine mode controls
        st.subheader("🎯 Force Engine Mode")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🤖 Force AI Mode", use_container_width=True):
                bot.force_ai_mode()
                st.success("Switched to AI mode! All queries will use AI engine.")
                st.rerun()
        
        with col2:
            if st.button("🔧 Force Regex Mode", use_container_width=True):
                bot.force_regex_mode()
                st.success("Switched to Regex mode! All queries will use regex engine.")
                st.rerun()
        
        with col3:
            if st.button("⚖️ Balanced Mode", use_container_width=True):
                bot.balanced_mode()
                st.success("Switched to Balanced mode! 50/50 split between engines.")
                st.rerun()
        
        # Test queries section
        st.markdown("---")
        st.subheader("🧪 Test Problematic Queries")
        
        test_queries = [
            "So if i spend 8L on ICICI EPM, what are the total points and milestone i receive?",
            "For paying joining fee for atlas card, how many miles i get?",
            "What are the renewal benefits of the atlas card?",
            "Which card is better for ₹50k dining spend?"
        ]
        
        selected_query = st.selectbox("Select a test query:", test_queries)
        
        if st.button("🚀 Test Query", use_container_width=True):
            with st.spinner("Processing test query..."):
                result = bot.process_query(selected_query)
                
                st.success(f"✅ Query processed successfully!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Engine Used", result["engine_used"])
                with col2:
                    st.metric("Processing Time", f"{result['processing_time_ms']:.0f}ms")
                
                st.markdown("### Response:")
                st.markdown(result["response"])
        
        return  # Exit main function to show only admin panel
    
    elif query_params.get("admin") == "analytics":
        # Redirect to enhanced analytics dashboard
        st.title("📊 Enhanced Analytics Dashboard")
        st.markdown("### 🚀 **New Enhanced Dashboard Available!**")
        st.markdown("""
        We've created a comprehensive analytics dashboard with advanced insights:
        
        **🎯 Key Features:**
        - Real-time feedback analysis
        - Query performance metrics  
        - Intent detection insights
        - User satisfaction tracking
        - Export functionality
        
        **🔗 Access Methods:**
        1. **Run directly:** `streamlit run analytics_dashboard.py`
        2. **Command line:** `python analytics_dashboard.py`
        """)
        
        st.markdown("---")
        st.subheader("📋 Quick Stats")
        
        # Show quick stats from both data sources
        feedback_count = 0
        query_count = 0
        
        if os.path.exists("feedback_log.json"):
            try:
                with open("feedback_log.json", 'r') as f:
                    feedback_data = json.load(f)
                    feedback_count = len(feedback_data)
            except:
                pass
        
        # Load query analytics from persistent storage
        try:
            from persistent_storage import storage_manager
            query_data = storage_manager.load_analytics_data()
            query_count = len(query_data)
        except:
            # Fallback to local file
            if os.path.exists("query_analytics.json"):
                try:
                    with open("query_analytics.json", 'r') as f:
                        query_data = json.load(f)
                        query_count = len(query_data)
                except:
                    pass
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Feedback", feedback_count)
        with col2:
            st.metric("Queries Analyzed", query_count)
        with col3:
            st.metric("Analytics Active", "✅" if feedback_count > 0 or query_count > 0 else "❌")
        
        # Show trending insights if data is available
        if feedback_count > 0 or query_count > 0:
            st.markdown("---")
            st.subheader("🔥 Live Intelligence Insights")
            
            try:
                from query_pattern_tracker import QueryPatternTracker
                tracker = QueryPatternTracker()
                insights = tracker.get_trending_insights()
                recommendations = tracker.get_recommendations()
                
                # Show trending queries
                trending = insights.get('top_trending_queries', [])
                if trending:
                    st.markdown("**📈 Trending Queries:**")
                    for i, trend in enumerate(trending[:3], 1):
                        st.write(f"{i}. *{trend.get('sample_query', 'N/A')}* (asked {trend.get('total_count', 0)} times)")
                else:
                    st.info("📊 No trending queries yet - need more data!")
                
                # Show key insights
                popular_intent = insights.get('most_popular_intent')
                if popular_intent:
                    st.markdown(f"**🎯 Most Popular Intent:** {popular_intent['intent']} ({popular_intent['count']} queries)")
                
                peak_time = insights.get('peak_usage_time')
                if peak_time:
                    st.markdown(f"**⏰ Peak Usage Hour:** {peak_time['hour']}:00 ({peak_time['query_count']} queries)")
                
                # Show recommendations
                if recommendations:
                    st.markdown("**💡 AI Recommendations:**")
                    for rec in recommendations[:3]:
                        st.info(rec)
                else:
                    st.info("💡 No specific recommendations yet - system is learning!")
                        
            except Exception as e:
                st.error(f"Pattern analysis error: {str(e)}")
                st.info("🔍 Debug: Check if persistent storage is working")
        
        return  # Stop here, don't show the main chatbot
    
    elif query_params.get("admin") == "feedback":
        st.title("📊 Feedback Dashboard")
        
        # Load feedback data from persistent storage (works with GitHub Gist)
        try:
            from persistent_storage import storage_manager
            feedback_data = storage_manager.load_feedback_data()
            
            if feedback_data:
                st.metric("Total Feedback", len(feedback_data))
                st.success(f"✅ Data loaded from: {storage_manager.storage_type}")
                
                # Show recent feedback
                st.subheader("Recent Feedback")
                for i, entry in enumerate(reversed(feedback_data[-10:])):  # Last 10
                    with st.expander(f"{entry['feedback'].upper()}: {entry['query'][:80]}..."):
                        st.write("**Query:**", entry['query'])
                        st.write("**Response:**", entry['response'][:300] + "..." if len(entry['response']) > 300 else entry['response'])
                        st.write("**Feedback:**", entry['feedback'])
                        if entry.get('improvement_suggestion'):
                            st.write("**Suggestion:**", entry['improvement_suggestion'])
                        st.write("**Time:**", entry['timestamp'])
                        
                        # Show analytics if available
                        if 'analytics' in entry:
                            st.json(entry['analytics'])
                
                # Download option
                import pandas as pd
                df = pd.DataFrame(feedback_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download All Feedback as CSV",
                    csv,
                    "feedback_data.csv",
                    "text/csv"
                )
            else:
                st.info("No feedback data yet. Submit some feedback to see it here!")
                st.info(f"🔍 Storage type: {storage_manager.storage_type}")
        except Exception as e:
            st.error(f"Error loading feedback: {e}")
            
            # Fallback to local file
            feedback_file = "feedback_log.json"
            if os.path.exists(feedback_file):
                st.info("📁 Falling back to local file...")
                try:
                    with open(feedback_file, 'r') as f:
                        feedback_data = json.load(f)
                    st.success(f"✅ Loaded {len(feedback_data)} entries from local file")
                except Exception as local_error:
                    st.error(f"Local file error: {local_error}")
            else:
                st.warning("No local file found either.")
        
        st.markdown("---")
        st.markdown("**Access URL:** Add `?admin=feedback` to your app URL to view this page")
        return  # Stop here, don't show the main chatbot
    
    # Initialize chat history and UI state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        welcome_msg = "Hi! I'm your credit card expert. Ask me anything about Axis Atlas or ICICI Emeralde Private Metal cards. I can help with fees, rewards, benefits, eligibility, and more!"
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    if "quick_questions_expanded" not in st.session_state:
        st.session_state.quick_questions_expanded = True
    
    if "feedback_log" not in st.session_state:
        st.session_state.feedback_log = []
    
    # Track session analytics
    if "session_start" not in st.session_state:
        import time
        st.session_state.session_start = time.time()

    # Quick questions section - collapsible after first interaction
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    
    # Auto-collapse after first user interaction (only if not manually toggled)
    if len(user_messages) > 0 and "manual_toggle" not in st.session_state:
        st.session_state.quick_questions_expanded = False
    
    # Collapsible header
    expand_icon = "🔽" if st.session_state.quick_questions_expanded else "▶️"
    collapse_class = "" if st.session_state.quick_questions_expanded else "collapsed"
    
    if len(user_messages) == 0:
        # Show full quick questions initially
        st.markdown(f"""
        <div class="quick-questions {collapse_class}">
            <h3>💡 Popular Questions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        quick_questions = [
            ("💰 Annual fees", "What are the annual fees for both cards?"),
            ("🎁 Welcome benefits", "What are the welcome benefits for both cards?"),
            ("✈️ Lounge access", "What are the airport lounge access benefits for both cards?"),
            ("🏨 Hotel rewards", "If I spend ₹100,000 on hotel bookings which card gives more rewards?"),
            ("⚡ Utility payments", "Do I get reward points on utility payments with both cards?"),
            ("🚗 Fuel payments", "Do I get reward points on fuel payments with both cards?"),
            ("💳 Insurance payments", "Do I get reward points on insurance payments with both cards?"),
            ("👤 Eligibility", "What are the eligibility requirements for both cards?")
        ]
        
        for i, (button_text, query) in enumerate(quick_questions):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.button(button_text, key=f"quick_{i}", use_container_width=True):
                    # Add user message
                    st.session_state.messages.append({"role": "user", "content": query})
                    
                    # Get immediate response
                    enhanced_query = enhancer.enhance_query(query)
                    with st.spinner("Getting answer..."):
                        import time
                        start_time = time.time()
                        response = bot.process_query(enhanced_query)
                        processing_time = (time.time() - start_time) * 1000
                        
                        # Show AI engine info
                        st.caption(f"🤖 Processed by: AI Engine ({processing_time:.0f}ms)")
                    
                    # Add assistant response with engine info
                    response_with_info = f"{response}\n\n*🤖 Processed by: AI Engine ({processing_time:.0f}ms)*"
                    st.session_state.messages.append({"role": "assistant", "content": response_with_info})
                    st.rerun()
    else:
        # Show compact collapsible version after first interaction
        header_col, toggle_col = st.columns([4, 1])
        with header_col:
            st.markdown(f"""
            <div class="quick-questions {collapse_class}">
                <h3>{expand_icon} Quick Questions</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with toggle_col:
            if st.button("Toggle", key="toggle_quick_questions", use_container_width=True):
                st.session_state.quick_questions_expanded = not st.session_state.quick_questions_expanded
                st.session_state.manual_toggle = True  # Mark as manually toggled
                st.rerun()
        
        # Show questions only if expanded
        if st.session_state.quick_questions_expanded:
            col1, col2, col3, col4 = st.columns(4)
            
            compact_questions = [
                ("💰", "What are the annual fees for both cards?"),
                ("⚡", "Do I get reward points on utility payments with both cards?"),
                ("🏨", "If I spend ₹100,000 on hotel bookings which card gives more rewards?"),
                ("✈️", "What are the airport lounge access benefits for both cards?")
            ]
            
            cols = [col1, col2, col3, col4]
            for i, (button_text, query) in enumerate(compact_questions):
                with cols[i]:
                    if st.button(button_text, key=f"compact_{i}", use_container_width=True):
                        # Add user message
                        st.session_state.messages.append({"role": "user", "content": query})
                        
                        # Get immediate response
                        enhanced_query = enhancer.enhance_query(query)
                        with st.spinner("Getting answer..."):
                            import time
                            start_time = time.time()
                            response = bot.process_query(enhanced_query)
                            processing_time = (time.time() - start_time) * 1000
                        
                        # Add assistant response with engine info
                        response_with_info = f"{response}\n\n*🤖 Processed by: AI Engine ({processing_time:.0f}ms)*"
                        st.session_state.messages.append({"role": "assistant", "content": response_with_info})
                        st.rerun()

    # Display chat history with feedback buttons
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add feedback buttons for all assistant messages except the welcome message
            # Welcome message detection: first assistant message with greeting content
            is_welcome_message = (message["role"] == "assistant" and 
                                  i == 0 and 
                                  "Hi!" in message["content"] and 
                                  "credit card expert" in message["content"])
            
            show_feedback = message["role"] == "assistant" and not is_welcome_message
            
            if show_feedback:
                # Simple, reliable feedback using native Streamlit radio buttons
                st.markdown("**Was this answer helpful?**")
                
                feedback_choice = st.radio(
                    "Rate this answer:",
                    options=["👍 Yes, helpful", "👎 Needs improvement", "⭐ Skip rating"],
                    index=2,  # Default to "Skip rating"
                    key=f"feedback_radio_{i}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                # Handle feedback selection
                if feedback_choice == "👍 Yes, helpful":
                    # Close any open improvement forms for this message
                    if f"show_improvement_{i}" in st.session_state:
                        del st.session_state[f"show_improvement_{i}"]
                    
                    # Find the corresponding user message
                    user_query = ""
                    if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                        user_query = st.session_state.messages[i-1]["content"]
                    
                    log_feedback(user_query, message["content"], "positive")
                    st.success("✅ Thanks for the positive feedback!")
                    
                elif feedback_choice == "👎 Needs improvement":
                    # Show improvement form
                    st.session_state[f"show_improvement_{i}"] = True
                    
                elif feedback_choice == "⭐ Skip rating":
                    # Close any open improvement forms when user selects skip
                    if f"show_improvement_{i}" in st.session_state:
                        del st.session_state[f"show_improvement_{i}"]
                
                # Show improvement suggestion input if thumbs down was clicked
                if st.session_state.get(f"show_improvement_{i}", False):
                    with st.expander("💭 Help us improve", expanded=True):
                        improvement_text = st.text_area(
                            "What would you expect as the correct answer?",
                            key=f"improvement_{i}",
                            placeholder="Please describe what you were looking for or what the correct answer should be...",
                            height=100
                        )
                        
                        col_submit, col_cancel = st.columns(2)
                        with col_submit:
                            if st.button("Submit Feedback", key=f"submit_feedback_{i}"):
                                # Find the corresponding user message
                                user_query = ""
                                if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                                    user_query = st.session_state.messages[i-1]["content"]
                                
                                log_feedback(user_query, message["content"], "negative", improvement_text)
                                st.success("Thanks for the detailed feedback! We'll use this to improve. 🙏")
                                
                                # Hide the improvement input
                                st.session_state[f"show_improvement_{i}"] = False
                                st.rerun()
                        
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_feedback_{i}"):
                                # Close the improvement form
                                st.session_state[f"show_improvement_{i}"] = False
                                # Clear the widget state to reset on next rerun
                                if f"feedback_radio_{i}" in st.session_state:
                                    del st.session_state[f"feedback_radio_{i}"]
                                st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask me anything about these credit cards..."):
        # Add user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Enhance the query using lessons learned
        enhanced_query = enhancer.enhance_query(prompt)
        
        # Show enhancement info if query was changed (for transparency)
        if enhanced_query != prompt and len(enhanced_query.strip()) > 0:
            with st.chat_message("assistant"):
                st.markdown(f"*Understanding your question as: \"{enhanced_query}\"*")

        # Get response using AI engine
        with st.spinner("Thinking..."):
            import time
            start_time = time.time()
            response = bot.process_query(enhanced_query)
            processing_time = (time.time() - start_time) * 1000
            
            # Show AI engine info for transparency
            st.caption(f"🤖 Processed by: AI Engine ({processing_time:.0f}ms)")
        
        # Display response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Trigger rerun to show feedback buttons immediately
        st.rerun()


    # Tips section with rotating examples
    if len(user_messages) > 0:
        # Curated tip examples focused on what users really want to know
        tip_examples = [
            'Ask reward questions: "Do I get points on rent payments with both cards?"',
            'Compare with amounts: "If I spend ₹50,000 on dining which card is better?"',
            'Check specific categories: "Do I get rewards on government payments?"',
            'Calculate travel rewards: "If I spend ₹2 lakh on flights which card wins?"',
            'Ask about caps: "What are the reward limits for grocery spending?"'
        ]
        
        # Use message count to cycle through tips
        tip_index = len(user_messages) % len(tip_examples)
        selected_tip = tip_examples[tip_index]
        
        # Add variety with different icons
        tip_icons = ['💡', '✨', '🎯']
        icon_index = (len(user_messages) // 2) % len(tip_icons)
        selected_icon = tip_icons[icon_index]
        
        st.markdown(f"""
        <div class="tips-section">
            <strong>{selected_icon} Try:</strong> {selected_tip}
        </div>
        """, unsafe_allow_html=True)



if __name__ == "__main__":
    main() 