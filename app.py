import streamlit as st
from utils.qa_engine import RichDataCreditCardBot

# Page configuration
st.set_page_config(
    page_title="Credit Card Benefits Chatbot",
    page_icon="💳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize the bot with both data files
@st.cache_resource
def load_bot():
    """Loads the credit card bot."""
    return RichDataCreditCardBot(data_files=["data/axis-atlas.json", "data/icici-epm.json"])

bot = load_bot()

def main():
    """Main function to run the Streamlit app."""
    st.title("💳 Credit Card Benefits Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add initial welcome message
        welcome_msg = "Welcome! Ask me anything about the Axis Atlas or ICICI Emeralde Private Metal credit cards."
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})


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

if __name__ == "__main__":
    main()
