import streamlit as st
from utils.qa_engine import RichDataCreditCardBot
import re

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
    
    /* Quick questions section - mobile optimized */
    .quick-questions {
        padding: 1rem;
        margin-bottom: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        background: rgba(59, 130, 246, 0.05);
    }
    
    .quick-questions h3 {
        font-size: 1rem !important;
        margin-bottom: 1rem !important;
        text-align: center;
        font-weight: 600 !important;
        color: #3b82f6 !important;
    }
    
    @media (min-width: 768px) {
        .quick-questions h3 {
            font-size: 1.2rem !important;
        }
    }
    
    /* Button styling - mobile-first touch-friendly */
    .stButton > button {
        width: 100% !important;
        height: auto !important;
        min-height: 48px !important; /* iOS touch target minimum */
        padding: 12px 16px !important;
        border-radius: 12px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease !important;
        border: 2px solid transparent !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        color: #374151 !important;
        backdrop-filter: blur(10px) !important;
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
            min-height: 52px !important;
            padding: 14px 18px !important;
            font-size: 0.95rem !important;
        }
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
</style>
""", unsafe_allow_html=True)

# Initialize the bot
@st.cache_resource
def load_bot():
    """Loads the credit card bot with enhanced query processing."""
    return RichDataCreditCardBot(data_files=["data/axis-atlas.json", "data/icici-epm.json"])

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
        
        # Define currency abbreviation mappings
        currency_mappings = {
            'k': '000',        # 20k = 20,000
            'l': '00000',      # 2L = 2,00,000 (2 lakhs)
            'cr': '0000000',   # 1cr = 1,00,00,000 (1 crore)
            'crore': '0000000'
        }
        
        # Pattern to match number + abbreviation (case insensitive)
        pattern = r'(\d+(?:\.\d+)?)\s*([klcr]+|crore)\b'
        
        def replace_currency(match):
            number = match.group(1)
            suffix = match.group(2).lower()
            
            # Handle decimal numbers
            if '.' in number:
                base_num = float(number)
                if suffix in currency_mappings:
                    result = int(base_num * (10 ** len(currency_mappings[suffix])))
                    return str(result)
            else:
                base_num = int(number)
                if suffix in currency_mappings:
                    result = base_num * (10 ** len(currency_mappings[suffix]))
                    return str(result)
            
            return match.group(0)  # Return original if no mapping found
        
        # Apply the replacement
        processed_query = re.sub(pattern, replace_currency, query, flags=re.IGNORECASE)
        return processed_query
    
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
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        welcome_msg = "Hi! I'm your credit card expert. Ask me anything about Axis Atlas or ICICI Emeralde Private Metal cards. I can help with fees, rewards, benefits, eligibility, and more!"
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    # Quick questions section (always show, but compact after first interaction)
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    
    # Show full quick questions initially, compact version after first interaction
    if len(user_messages) == 0:
        st.markdown("""
        <div class="quick-questions">
            <h3>💡 Popular Questions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        quick_questions = [
            ("💰 What are the annual fees?", "What are the annual fees for both cards?"),
            ("🎁 What welcome benefits do I get?", "What are the welcome benefits for both cards?"),
            ("✈️ Airport lounge access details?", "What are the airport lounge access benefits for both cards?"),
            ("🏨 Hotel spending rewards?", "If I spend ₹100,000 on hotel bookings which card gives more rewards?"),
            ("⚡ Utility payment rewards?", "Do I get reward points on utility payments with both cards?"),
            ("🚗 Fuel payment rewards?", "Do I get reward points on fuel payments with both cards?"),
            ("💳 Insurance payment rewards?", "Do I get reward points on insurance payments with both cards?"),
            ("👤 Who can apply for these cards?", "What are the eligibility requirements for both cards?")
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
                        response = bot.get_answer(enhanced_query)
                    
                    # Add assistant response
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
        
        st.markdown("---")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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

        # Get response
        with st.spinner("Thinking..."):
            response = bot.get_answer(enhanced_query)
        
        # Display response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Compact quick questions (positioned after chat, before tips for better visibility)
    if len(user_messages) > 0:
        st.markdown("""
        <div class="quick-questions">
            <h3>💡 Quick Questions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Show 4 most popular questions in a single row
        col1, col2, col3, col4 = st.columns(4)
        
        compact_questions = [
            ("💰 Fees", "What are the annual fees for both cards?"),
            ("⚡ Utility", "Do I get reward points on utility payments with both cards?"),
            ("🏨 Hotel", "If I spend ₹100,000 on hotel bookings which card gives more rewards?"),
            ("✈️ Lounge", "What are the airport lounge access benefits for both cards?")
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
                        response = bot.get_answer(enhanced_query)
                    
                    # Add assistant response
                    st.session_state.messages.append({"role": "assistant", "content": response})
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