import streamlit as st
from utils.qa_engine import get_card_data, get_answer

st.set_page_config(page_title="Credit Card Q&A", layout="wide")

def main():
    """Main function to run the Streamlit app."""
    st.title("💳 Indian Credit Card Terms Q&A")
    st.markdown("""
    Ask a question about the terms and conditions of popular Indian credit cards. 
    This tool uses OpenAI's GPT-4o to understand your question and provide answers from a structured database of card features.
    """)

    # Load data once and cache it
    @st.cache_data
    def load_data():
        return get_card_data()

    card_data = load_data()
    
    if not card_data:
        st.error("No card data found. Make sure there are valid JSON files in the 'data/' directory.")
        return
        
    st.sidebar.header("Available Cards")
    for card_name in card_data.keys():
        st.sidebar.success(card_name)
    
    st.sidebar.header("Sample Queries")
    sample_queries = [
        "What is the annual fee for Axis Atlas?",
        "Does ICICI EPM give a welcome bonus?",
        "How many free lounge visits are available for silver tier holders on the Axis Atlas card?",
        "What are the milestone benefits of the ICICI Emeralde card?",
        "Which MCCs are excluded from reward points on the ICICI card?"
    ]
    for query in sample_queries:
        if st.sidebar.button(query):
            st.session_state.question = query
        
    # Handle user input
    if 'question' not in st.session_state:
        st.session_state.question = "What is the joining fee for ICICI EPM?"

    question = st.text_input("Ask your question:", value=st.session_state.question, key="question_input")

    if question:
        with st.spinner("Finding the answer..."):
            answer = get_answer(question, card_data)
            st.markdown("---")
            st.header("Answer")
            st.markdown(answer)

if __name__ == "__main__":
    main()
