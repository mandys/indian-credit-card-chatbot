import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(
    page_title="Feedback Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Chatbot Feedback Dashboard")

# Load feedback data
feedback_file = "feedback_log.json"
if os.path.exists(feedback_file):
    with open(feedback_file, 'r') as f:
        feedback_data = json.load(f)
    
    if feedback_data:
        df = pd.DataFrame(feedback_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Feedback", len(df))
        
        with col2:
            positive_count = len(df[df['feedback'] == 'positive'])
            st.metric("👍 Positive", positive_count)
        
        with col3:
            negative_count = len(df[df['feedback'] == 'negative'])
            st.metric("👎 Negative", negative_count)
        
        with col4:
            if len(df) > 0:
                satisfaction_rate = (positive_count / len(df) * 100)
                st.metric("Satisfaction Rate", f"{satisfaction_rate:.1f}%")
        
        # Feedback over time
        if len(df) > 1:
            st.subheader("📈 Feedback Trends")
            df_daily = df.groupby([df['timestamp'].dt.date, 'feedback']).size().reset_index(name='count')
            fig = px.line(df_daily, x='timestamp', y='count', color='feedback', 
                         title="Daily Feedback Count")
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent negative feedback with improvement suggestions
        st.subheader("🔍 Recent Negative Feedback")
        negative_feedback = df[df['feedback'] == 'negative'].sort_values('timestamp', ascending=False)
        
        if not negative_feedback.empty:
            for idx, row in negative_feedback.head(10).iterrows():
                with st.expander(f"Query: {row['query'][:100]}... - {row['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    st.write("**User Query:**", row['query'])
                    st.write("**Bot Response:**", row['response'])
                    if row['improvement_suggestion']:
                        st.write("**User's Expected Answer:**", row['improvement_suggestion'])
                    else:
                        st.write("**User's Expected Answer:** _No suggestion provided_")
        else:
            st.info("No negative feedback yet! 🎉")
        
        # Common query patterns
        st.subheader("🔍 Common Query Patterns")
        if len(df) > 0:
            # Extract keywords from queries
            query_text = ' '.join(df['query'].tolist()).lower()
            common_words = []
            for word in ['fee', 'reward', 'lounge', 'hotel', 'utility', 'fuel', 'insurance', 'travel', 'point', 'mile']:
                count = query_text.count(word)
                if count > 0:
                    common_words.append({'keyword': word, 'count': count})
            
            if common_words:
                word_df = pd.DataFrame(common_words)
                fig = px.bar(word_df, x='keyword', y='count', title="Most Queried Topics")
                st.plotly_chart(fig, use_container_width=True)
        
        # Export functionality
        st.subheader("📁 Export Data")
        if st.button("Download Feedback Data as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"feedback_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No feedback data available yet.")
else:
    st.info("No feedback file found. Start collecting feedback by using the chatbot!")

# Instructions
st.sidebar.markdown("""
## 📋 How to Use

1. **Monitor Satisfaction**: Check the satisfaction rate and trends
2. **Review Negative Feedback**: Focus on improvement suggestions
3. **Identify Patterns**: See which topics users ask about most
4. **Export Data**: Download feedback for further analysis

## 🎯 Improvement Actions

- **Low satisfaction?** Review negative feedback patterns
- **Common complaints?** Update training data or prompts  
- **Missing features?** Add new intents or data sources
- **Unclear responses?** Improve system prompts
""")