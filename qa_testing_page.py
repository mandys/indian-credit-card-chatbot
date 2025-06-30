import streamlit as st
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="QA Testing Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧪 Credit Card Chatbot - QA Testing Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page:", [
    "Test Runner", 
    "Test Results", 
    "Manual Testing", 
    "Test Case Management"
])

if page == "Test Runner":
    st.header("🚀 Automated Test Runner")
    
    st.markdown("""
    This page allows you to run automated tests against the credit card chatbot.
    Tests check for expected keywords, correct winners in comparisons, and proper responses.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("▶️ Run All Tests", type="primary"):
            with st.spinner("Running tests... This may take a minute."):
                try:
                    # Run the test runner
                    result = subprocess.run([sys.executable, "test_runner.py"], 
                                          capture_output=True, text=True, cwd=".")
                    
                    if result.returncode == 0:
                        st.success("✅ Tests completed successfully!")
                        st.text_area("Test Output:", result.stdout, height=400)
                    else:
                        st.error("❌ Tests failed to run")
                        st.text_area("Error Output:", result.stderr, height=200)
                        
                except Exception as e:
                    st.error(f"Error running tests: {e}")
        
        st.markdown("---")
        
        if st.button("🔄 Quick Test (5 cases)", type="secondary"):
            st.info("Running quick test subset...")
            # Could implement a subset of tests here
    
    with col2:
        st.subheader("Test Categories")
        test_categories = [
            "🏨 Hotel & Travel Spending",
            "⚡ Utility Spending", 
            "🎯 Reward Comparison",
            "✈️ Miles Transfer",
            "💳 Fees & Charges",
            "🛄 Lounge Access"
        ]
        
        for category in test_categories:
            st.markdown(f"• {category}")

elif page == "Test Results":
    st.header("📊 Test Results Dashboard")
    
    # Try to load the latest test report
    try:
        report_files = list(Path(".").glob("test_report_*.txt"))
        if report_files:
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            
            st.subheader(f"Latest Report: {latest_report.name}")
            
            with open(latest_report, 'r') as f:
                report_content = f.read()
            
            # Extract summary stats from report
            lines = report_content.split('\n')
            for line in lines:
                if "Passing:" in line:
                    passing = line.split("Passing: ")[1]
                    st.metric("✅ Passing Tests", passing)
                elif "Failing:" in line:
                    failing = line.split("Failing: ")[1] 
                    st.metric("❌ Failing Tests", failing)
                elif "Overall Score:" in line:
                    score = line.split("Overall Score: ")[1]
                    st.metric("📊 Overall Score", score)
            
            # Show full report
            st.text_area("Full Report:", report_content, height=600)
            
        else:
            st.warning("No test reports found. Run tests first.")
            
    except Exception as e:
        st.error(f"Error loading test results: {e}")
    
    # Button to view HTML test cases
    if st.button("🌐 Open HTML Test Cases"):
        st.markdown("[Click here to view HTML test cases](./test_cases.html)")

elif page == "Manual Testing":
    st.header("🧪 Manual Testing Interface")
    
    st.markdown("""
    Use this interface to manually test specific queries against the chatbot.
    This is useful for debugging specific issues or testing new functionality.
    """)
    
    # Import the bot
    try:
        from utils.qa_engine import RichDataCreditCardBot
        
        @st.cache_resource
        def load_bot():
            return RichDataCreditCardBot(data_files=['data/axis-atlas.json', 'data/icici-epm.json'])
        
        bot = load_bot()
        
        # Test query input
        test_query = st.text_area("Enter test query:", 
                                 placeholder="e.g., What are the joining fees for both cards?",
                                 height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Test Query"):
                if test_query:
                    with st.spinner("Processing query..."):
                        try:
                            response = bot.get_answer(test_query)
                            st.subheader("Bot Response:")
                            st.write(response)
                            
                            # Show debug info
                            with st.expander("🔍 Debug Information"):
                                intent = bot.detect_intent(test_query)
                                cards = bot.extract_card_names(test_query)
                                spend = bot.extract_spend_amount(test_query)
                                
                                st.write(f"**Detected Intent:** {intent}")
                                st.write(f"**Extracted Cards:** {cards}")
                                st.write(f"**Extracted Spend:** {spend}")
                                
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please enter a test query.")
        
        with col2:
            st.subheader("Common Test Queries")
            common_queries = [
                "What are the joining fees for both cards?",
                "I have a 100,000 hotel spend. Which card is better?",
                "Can I transfer ICICI points to airlines?",
                "What are the utility charges?",
                "How many lounge visits do I get?",
                "What are the milestone benefits?"
            ]
            
            for query in common_queries:
                if st.button(f"📝 {query[:40]}..."):
                    st.session_state['manual_query'] = query
    
    except ImportError as e:
        st.error(f"Could not import chatbot: {e}")

elif page == "Test Case Management":
    st.header("📝 Test Case Management")
    
    st.markdown("""
    Manage and edit test cases. Add new test cases or modify existing ones.
    """)
    
    # Test case editor
    st.subheader("Add New Test Case")
    
    with st.form("new_test_case"):
        category = st.selectbox("Category:", [
            "Hotel & Travel Spending",
            "Utility Spending", 
            "Reward Comparison",
            "Miles Transfer",
            "Fees & Charges",
            "Lounge Access",
            "Insurance",
            "Welcome Benefits"
        ])
        
        query = st.text_area("Test Query:")
        expected_keywords = st.text_input("Expected Keywords (comma-separated):")
        expected_winner = st.text_input("Expected Winner (optional):")
        expected_content = st.text_input("Expected Content Type (optional):")
        
        if st.form_submit_button("➕ Add Test Case"):
            if query:
                # Here you would add logic to save the test case
                st.success("Test case added! (Note: This is a demo - implement saving logic)")
            else:
                st.error("Please enter a test query.")
    
    st.markdown("---")
    
    # Current test cases display
    st.subheader("Current Test Cases")
    
    # Sample test cases display (you'd load from actual source)
    test_cases_data = {
        "Category": ["Hotel & Travel", "Utility", "Reward Comparison", "Miles Transfer"],
        "Query": [
            "I have a 200,000 hotel spend...",
            "What are the utility charges...",
            "If I spend 100000 which card...",
            "Can I transfer ICICI points..."
        ],
        "Status": ["✅ Passing", "✅ Passing", "⚠️ Partial", "❌ Failing"]
    }
    
    df = pd.DataFrame(test_cases_data)
    st.dataframe(df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    QA Testing Dashboard v1.0 | Credit Card Chatbot | 
    <a href='test_cases.html' target='_blank'>View HTML Test Cases</a>
</div>
""", unsafe_allow_html=True) 