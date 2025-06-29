import streamlit as st
from utils.qa_engine import RichDataCreditCardBot

# Page configuration
st.set_page_config(
    page_title="Credit Card Benefits Chatbot",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization and blue design
st.markdown("""
<style>
    /* Override Streamlit's default padding more aggressively */
    .main .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Remove Streamlit's default margins */
    .stApp > div > div > div > div {
        padding-top: 0 !important;
    }
    
    /* Compact header for mobile */
    h1 {
        font-size: 1.5rem !important;
        margin-bottom: 0.1rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        color: #1e3a8a !important;
    }
    
    /* Compact subtitle */
    .subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 0.6rem;
        margin-top: 0;
        font-style: italic;
    }
    
    /* Compact section header */
    h3 {
        font-size: 1rem !important;
        margin-bottom: 0.4rem !important;
        margin-top: 0.2rem !important;
        padding-top: 0 !important;
        color: #3b82f6 !important;
    }
    
    /* Button styling with thin blue border and white background */
    .stButton > button {
        background: white !important;
        color: #1e3a8a !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.85rem !important;
        line-height: 1.2 !important;
        height: auto !important;
        min-height: 2.5rem !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background: #f8fafc !important;
        border-color: #1d4ed8 !important;
        color: #1d4ed8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* Chat input styling */
    .stChatInput > div > div > div > div {
        border-color: #3b82f6 !important;
    }
    
    /* Reduce spacing between elements more aggressively */
    .element-container {
        margin-bottom: 0.2rem !important;
        margin-top: 0 !important;
    }
    
    /* Remove default streamlit margins */
    .stMarkdown {
        margin-bottom: 0.3rem !important;
        margin-top: 0 !important;
    }
    
    /* Remove button container margins */
    .stButton {
        margin-bottom: 0.3rem !important;
        margin-top: 0 !important;
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0.1rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        
        h1 {
            font-size: 1.3rem !important;
        }
        
        .stButton > button {
            font-size: 0.8rem !important;
            padding: 0.35rem 0.6rem !important;
            min-height: 2.2rem !important;
        }
        
        .subtitle {
            margin-bottom: 0.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize the bot with both data files
@st.cache_resource
def load_bot():
    """Loads the credit card bot."""
    return RichDataCreditCardBot(data_files=["data/axis-atlas.json", "data/icici-epm.json"])

bot = load_bot()

def main():
    """Main function to run the Streamlit app."""
    st.title("💳 Credit Card Chatbot")
    st.markdown('<div class="subtitle">Your AI assistant for credit card info</div>', unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial welcome message
        welcome_msg = "Welcome! Ask me anything about the Axis Atlas or ICICI Emeralde Private Metal credit cards."
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    # Show conversation starters only if no user messages yet
    user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
    if len(user_messages) == 0:
        st.markdown("### ✨ Quick questions:")
        
        # Create columns for starter buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💳 ICICI Emeralde joining fee?", use_container_width=True):
                handle_starter_click("What's the joining fee for the ICICI Emeralde card?")
            
            if st.button("🚫 ICICI reward exclusions?", use_container_width=True):
                handle_starter_click("Which MCCs are excluded from rewards on the ICICI card?")
        
        with col2:
            if st.button("✨ Atlas milestone benefits?", use_container_width=True):
                handle_starter_click("Tell me about the milestone benefits on the Axis Atlas card")
            
            if st.button("✈️ Atlas lounge visits?", use_container_width=True):
                handle_starter_click("How many lounge visits do I get with Axis Atlas?")
        
        st.markdown("---")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get assistant response
        with st.spinner("Thinking..."):
            response = bot.get_answer(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def handle_starter_click(question):
    """Handle when a starter button is clicked."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Get assistant response
    response = bot.get_answer(question)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update the display
    st.rerun()

if __name__ == "__main__":
    main()
