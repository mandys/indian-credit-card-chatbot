import streamlit as st
from utils.qa_engine import RuleBasedCreditCardBot

st.set_page_config(page_title="Credit Card Q&A", layout="wide")

# Cache the bot instance so it's loaded only once.
@st.cache_resource
def get_bot():
    """Initializes and returns the RuleBasedCreditCardBot."""
    return RuleBasedCreditCardBot()

def main():
    """Main function to run the Streamlit app."""
    st.title("💳 Indian Credit Card Terms Q&A")
    st.markdown("""
    Ask a question about the terms and conditions of popular Indian credit cards. 
    This tool uses a fast, rule-based engine for intent detection and **GPT-3.5-Turbo** for answer generation.
    """)

    bot = get_bot()
    
    if not bot.credit_card_data:
        st.error("No card data found. Make sure there are valid JSON files in the 'data/' directory.")
        return
        
    st.sidebar.header("Available Cards")
    for card_name in bot.credit_card_data.keys():
        st.sidebar.success(card_name)
    
    st.sidebar.header("Sample Topics")
    st.sidebar.info("""
    You can ask about:
    - Annual or Joining Fees
    - Welcome Bonuses
    - Reward Points & Milestones
    - MCC Exclusions
    - Lounge Access
    - Insurance & Other Benefits
    """)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": bot.get_greeting()}]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask me anything about these cards..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = bot.get_answer(prompt)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
