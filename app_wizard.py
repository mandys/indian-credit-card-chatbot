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
    
    /* Clean, minimal button styling */
    .stButton > button {
        background: white;
        color: #2c3e50;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stButton > button:hover {
        border-color: #3498db;
        background: #f8f9fa;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.15);
    }
    
    /* Primary action buttons */
    .primary-button button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
    }
    
    .primary-button button:hover {
        background: linear-gradient(135deg, #2980b9 0%, #1f6ec7 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(52, 152, 219, 0.25);
    }
    
    /* Card selection styling */
    .card-selection {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .card-selection:hover {
        border-color: #3498db;
        background: #f8f9fa;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
    }
    
    /* Category grid - cleaner spacing */
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Info boxes - softer styling */
    .info-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #3498db;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #2c3e50;
    }
    
    /* Progress indicator - minimal */
    .progress-step {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 25px;
        background: #f8f9fa;
        color: #6c757d;
        font-size: 0.9rem;
        border: 1px solid #e9ecef;
    }
    
    .progress-step.active {
        background: #3498db;
        color: white;
        border-color: #3498db;
    }
    
    /* Reduce visual noise */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 8px;
    }
    
    .stTextArea > div > div > textarea {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        background: white;
    }
    
    /* Clean subcategory buttons */
    .subcategory-button {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #495057;
        transition: all 0.2s ease;
    }
    
    .subcategory-button:hover {
        border-color: #3498db;
        background: #f8f9fa;
        color: #2c3e50;
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
    
    # Quick action buttons - reduced to most essential
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Compare Rewards", key="quick_rewards", help="Compare reward rates"):
            query = "If I spend 100000 which card gives me more rewards?"
            answer = st.session_state.chat_engine.get_answer(query)
            st.markdown("**Answer:**")
            st.markdown(answer)
    
    with col2:
        if st.button("✈️ Airport Benefits", key="quick_airport", help="Lounge access and travel benefits"):
            query = "What are the airport lounge access benefits?"
            answer = st.session_state.chat_engine.get_answer(query)
            st.markdown("**Answer:**")
            st.markdown(answer)
    
    with col3:
        if st.button("💳 Annual Fees", key="quick_fees", help="Fee structure and waivers"):
            query = "What are the annual fee waiver conditions?"
            answer = st.session_state.chat_engine.get_answer(query)
            st.markdown("**Answer:**")
            st.markdown(answer)
    
    st.markdown("---")
    
    # Free-form text input
    user_query = st.text_area(
        "Ask any question about credit cards:",
        placeholder="e.g., If I spend ₹2 lakhs on hotels, which card gives better rewards?",
        height=120,
        key="chat_input"
    )
    
    # Single centered submit button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Get Answer", key="chat_submit", disabled=not user_query.strip(), use_container_width=True):
            if user_query.strip():
                with st.spinner("Thinking..."):
                    answer = st.session_state.chat_engine.get_answer(user_query)
                st.markdown("### 🤖 Answer:")
                st.markdown(answer)
    
    # Show helpful examples only if no input
    if not user_query.strip():
        st.markdown("---")
        st.markdown("**💡 Example Questions:**")
        
        examples = [
            "If I spend ₹2 lakhs on hotels, which card gives better rewards?",
            "What are the utility payment charges?", 
            "Can I transfer ICICI points to airlines?",
            "Which card has better lounge access for international travel?",
            "What insurance benefits do these cards provide?"
        ]
        
        for i, example in enumerate(examples):
            if st.button(f"💭 {example}", key=f"example_{i}", help="Click to use this example"):
                # Set the example as the query and get answer
                answer = st.session_state.chat_engine.get_answer(example)
                st.markdown(f"**Question:** {example}")
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