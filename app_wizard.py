import streamlit as st
import os
from utils.qa_wizard_engine import CreditCardWizard
from utils.qa_engine import RichDataCreditCardBot

# Page configuration
st.set_page_config(
    page_title="Credit Card Assistant",
    page_icon="💳", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1E88E5 0%, #42A5F5 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    }
    
    /* Card selection buttons */
    .card-button {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .card-button:hover {
        border-color: #1E88E5;
        background: #f8f9fa;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #F3E5F5 100%);
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Chat interface styling */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Progress indicator */
    .progress-step {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 20px;
        background: #E3F2FD;
        color: #1976D2;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .progress-step.active {
        background: #1976D2;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def initialize_engines():
    """Initialize both wizard and chat engines"""
    data_files = ['data/axis-atlas.json', 'data/icici-epm.json']
    
    if 'wizard_engine' not in st.session_state:
        st.session_state.wizard_engine = CreditCardWizard(data_files)
    
    if 'chat_engine' not in st.session_state:
        st.session_state.chat_engine = RichDataCreditCardBot(data_files)
    
    if 'interface_mode' not in st.session_state:
        st.session_state.interface_mode = 'wizard'

def render_interface_selector():
    """Render interface mode selection"""
    st.markdown("### 💳 Credit Card Assistant")
    st.markdown("Choose how you'd like to interact:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🧙‍♂️ Guided Assistant", 
            key="select_wizard",
            help="Step-by-step guided questions for accurate results",
            use_container_width=True
        ):
            st.session_state.interface_mode = 'wizard'
            st.rerun()
    
    with col2:
        if st.button(
            "💬 Chat Assistant", 
            key="select_chat", 
            help="Free-form conversation for quick questions",
            use_container_width=True
        ):
            st.session_state.interface_mode = 'chat'
            st.rerun()
    
    # Show current mode
    if st.session_state.interface_mode == 'wizard':
        st.info("🧙‍♂️ **Guided Assistant Mode** - Get accurate answers through step-by-step guidance")
    else:
        st.info("💬 **Chat Assistant Mode** - Ask questions in natural language")

def render_chat_interface():
    """Render the traditional chat interface"""
    st.markdown("### 💬 Chat with your Credit Card Assistant")
    
    # Quick action buttons
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Check returns on my cards", key="quick_returns"):
            query = "If I spend 100000 which card gives me more rewards?"
            answer = st.session_state.chat_engine.get_answer(query)
            st.markdown("**Answer:**")
            st.markdown(answer)
    
    with col2:
        if st.button("Airport Benefits", key="quick_airport"):
            query = "What are the airport lounge access benefits?"
            answer = st.session_state.chat_engine.get_answer(query)
            st.markdown("**Answer:**")
            st.markdown(answer)
    
    with col3:
        if st.button("Annual Fee Waiver", key="quick_waiver"):
            query = "What are the annual fee waiver conditions?"
            answer = st.session_state.chat_engine.get_answer(query)
            st.markdown("**Answer:**")
            st.markdown(answer)
    
    st.markdown("---")
    
    # Free-form text input
    user_query = st.text_area(
        "Ask any question about credit cards:",
        placeholder="e.g., If I spend ₹2 lakhs on hotels, which card gives better rewards?",
        height=100,
        key="chat_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("Get Answer", key="chat_submit", disabled=not user_query.strip()):
            if user_query.strip():
                with st.spinner("Thinking..."):
                    answer = st.session_state.chat_engine.get_answer(user_query)
                st.markdown("### 🤖 Answer:")
                st.markdown(answer)
    
    # Show conversation starters if no input
    if not user_query.strip():
        st.markdown("**Popular Questions:**")
        
        categories = [
            ("🏨 Hotels", "Rent", "⚡ Utilities", "⛽ Fuel"),
            ("🎓 Education", "🏛️ Government", "💍 Gold/Jewellery", "🛡️ Insurance"),
            ("✈️ Travel", "🎮 Gaming", "📱 Online", "🛍️ Shopping")
        ]
        
        for category_row in categories:
            cols = st.columns(len(category_row))
            for col, category in zip(cols, category_row):
                with col:
                    if st.button(category, key=f"category_{category}", use_container_width=True):
                        # Generate a sample query for the category
                        category_queries = {
                            "🏨 Hotels": "What are the rewards for hotel bookings?",
                            "Rent": "What are the charges for rent payments?", 
                            "⚡ Utilities": "What are the rewards and fees for utility payments?",
                            "⛽ Fuel": "What are the charges for fuel purchases?",
                            "🎓 Education": "What are the fees for education payments?",
                            "🏛️ Government": "What are the charges for government payments?",
                            "💍 Gold/Jewellery": "Are gold purchases excluded from rewards?",
                            "🛡️ Insurance": "What are the fees for insurance payments?",
                            "✈️ Travel": "What are the travel benefits?",
                            "🎮 Gaming": "Are gaming transactions excluded from rewards?",
                            "📱 Online": "What are the rewards for online shopping?",
                            "🛍️ Shopping": "What are the general shopping rewards?"
                        }
                        
                        if category in category_queries:
                            query = category_queries[category]
                            answer = st.session_state.chat_engine.get_answer(query)
                            st.markdown(f"**Question:** {query}")
                            st.markdown("**Answer:**")
                            st.markdown(answer)

def main():
    """Main application function"""
    # Initialize engines
    initialize_engines()
    
    # Sidebar for navigation and settings
    with st.sidebar:
        st.markdown("## Navigation")
        
        # Interface mode toggle
        current_mode = st.session_state.interface_mode
        new_mode = st.selectbox(
            "Interface Mode:",
            options=['wizard', 'chat'],
            index=0 if current_mode == 'wizard' else 1,
            format_func=lambda x: "🧙‍♂️ Guided Assistant" if x == 'wizard' else "💬 Chat Assistant"
        )
        
        if new_mode != current_mode:
            st.session_state.interface_mode = new_mode
            st.rerun()
        
        st.markdown("---")
        
        # Available Cards Info
        st.markdown("## Available Cards")
        st.markdown("• **ICICI Emeralde Private Metal**")
        st.markdown("• **Axis Bank Atlas**")
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("## Quick Comparison")
        st.markdown("**ICICI EPM:**")
        st.markdown("• 6 points per ₹200")
        st.markdown("• Annual Fee: ₹12,499")
        st.markdown("• Premium travel benefits")
        
        st.markdown("**Axis Atlas:**")
        st.markdown("• 2-5 miles per ₹100")
        st.markdown("• Annual Fee: ₹5,000")
        st.markdown("• Travel category bonuses")
        
        st.markdown("---")
        
        # Reset option
        if st.button("🔄 Reset Session", key="reset_session"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    if st.session_state.interface_mode == 'wizard':
        # Render wizard interface
        st.session_state.wizard_engine.render_wizard()
    else:
        # Render chat interface
        render_chat_interface()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
            "💳 Credit Card Assistant | Powered by AI"
            "</div>", 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main() 