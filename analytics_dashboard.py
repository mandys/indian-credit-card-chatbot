"""
Enhanced Analytics Dashboard for Credit Card Chatbot
Provides comprehensive insights into user feedback, query patterns, and system performance.
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from collections import Counter, defaultdict
import numpy as np

def load_analytics_data():
    """Load all analytics data from JSON files."""
    data = {
        'feedback': [],
        'queries': []
    }
    
    # Load feedback data
    if os.path.exists('feedback_log.json'):
        try:
            with open('feedback_log.json', 'r') as f:
                data['feedback'] = json.load(f)
        except Exception as e:
            st.error(f"Error loading feedback data: {e}")
    
    # Load query analytics data
    if os.path.exists('query_analytics.json'):
        try:
            with open('query_analytics.json', 'r') as f:
                data['queries'] = json.load(f)
        except Exception as e:
            st.error(f"Error loading query analytics: {e}")
    
    return data

def analyze_feedback_data(feedback_data):
    """Analyze feedback data and return insights."""
    if not feedback_data:
        return None
    
    df = pd.DataFrame(feedback_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Basic metrics
    total_feedback = len(df)
    positive_feedback = len(df[df['feedback'] == 'positive'])
    negative_feedback = len(df[df['feedback'] == 'negative'])
    satisfaction_rate = (positive_feedback / total_feedback * 100) if total_feedback > 0 else 0
    
    # Analytics metrics (new enhanced data)
    analytics_available = 'analytics' in df.columns and df['analytics'].notna().any()
    
    insights = {
        'total_feedback': total_feedback,
        'positive_feedback': positive_feedback,
        'negative_feedback': negative_feedback,
        'satisfaction_rate': satisfaction_rate,
        'analytics_available': analytics_available,
        'df': df
    }
    
    if analytics_available:
        # Extract analytics data
        analytics_df = pd.json_normalize(df['analytics'].dropna())
        
        # Intent analysis
        if 'intent_detected' in analytics_df.columns:
            intent_feedback = df[df['analytics'].notna()].copy()
            intent_feedback['intent'] = intent_feedback['analytics'].apply(lambda x: x.get('intent_detected', 'unknown') if isinstance(x, dict) else 'unknown')
            intent_satisfaction = intent_feedback.groupby('intent')['feedback'].apply(lambda x: (x == 'positive').sum() / len(x) * 100).to_dict()
            insights['intent_satisfaction'] = intent_satisfaction
        
        # Cards mentioned analysis
        if 'cards_mentioned' in analytics_df.columns:
            cards_feedback = df[df['analytics'].notna()].copy()
            cards_feedback['cards'] = cards_feedback['analytics'].apply(lambda x: ', '.join(x.get('cards_mentioned', [])) if isinstance(x, dict) else '')
            card_satisfaction = cards_feedback[cards_feedback['cards'] != ''].groupby('cards')['feedback'].apply(lambda x: (x == 'positive').sum() / len(x) * 100).to_dict()
            insights['card_satisfaction'] = card_satisfaction
    
    return insights

def analyze_query_data(query_data):
    """Analyze query processing data and return insights."""
    if not query_data:
        return None
    
    df = pd.DataFrame(query_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract analytics data
    analytics_df = pd.json_normalize(df['analytics'])
    
    # Performance metrics
    avg_processing_time = analytics_df['total_processing_time'].mean() if 'total_processing_time' in analytics_df.columns else 0
    avg_data_retrieval = analytics_df['data_retrieval_time'].mean() if 'data_retrieval_time' in analytics_df.columns else 0
    avg_response_generation = analytics_df['response_generation_time'].mean() if 'response_generation_time' in analytics_df.columns else 0
    
    # Intent distribution
    intent_distribution = analytics_df['intent_detected'].value_counts().to_dict() if 'intent_detected' in analytics_df.columns else {}
    
    # API usage
    api_usage = analytics_df['api_used'].value_counts().to_dict() if 'api_used' in analytics_df.columns else {}
    
    # Cards mentioned frequency
    cards_mentioned = []
    if 'cards_mentioned' in analytics_df.columns:
        for cards in analytics_df['cards_mentioned'].dropna():
            if isinstance(cards, list):
                cards_mentioned.extend(cards)
    card_frequency = Counter(cards_mentioned)
    
    insights = {
        'total_queries': len(df),
        'avg_processing_time': avg_processing_time,
        'avg_data_retrieval': avg_data_retrieval,
        'avg_response_generation': avg_response_generation,
        'intent_distribution': intent_distribution,
        'api_usage': api_usage,
        'card_frequency': dict(card_frequency),
        'df': df,
        'analytics_df': analytics_df
    }
    
    return insights

def create_dashboard():
    """Create the enhanced analytics dashboard."""
    st.set_page_config(
        page_title="Analytics Dashboard - Credit Card Chatbot",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Enhanced Analytics Dashboard")
    st.markdown("**Comprehensive insights into user feedback and query patterns**")
    
    # Load data
    data = load_analytics_data()
    feedback_insights = analyze_feedback_data(data['feedback'])
    query_insights = analyze_query_data(data['queries'])
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    
    # Date range filter
    if data['feedback'] or data['queries']:
        # Determine date range
        all_dates = []
        if data['feedback']:
            all_dates.extend([datetime.fromisoformat(item['timestamp']) for item in data['feedback']])
        if data['queries']:
            all_dates.extend([datetime.fromisoformat(item['timestamp']) for item in data['queries']])
        
        if all_dates:
            min_date = min(all_dates).date()
            max_date = max(all_dates).date()
            
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.experimental_rerun()
    
    # Main dashboard content
    if not feedback_insights and not query_insights:
        st.warning("No analytics data available yet. Start using the chatbot to generate data!")
        return
    
    # Key Metrics Row
    st.header("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if feedback_insights:
            st.metric(
                "User Satisfaction",
                f"{feedback_insights['satisfaction_rate']:.1f}%",
                delta=f"{feedback_insights['positive_feedback']} positive"
            )
        else:
            st.metric("User Satisfaction", "No data", delta="0 feedback")
    
    with col2:
        if feedback_insights:
            st.metric(
                "Total Feedback",
                feedback_insights['total_feedback'],
                delta=f"{feedback_insights['negative_feedback']} negative"
            )
        else:
            st.metric("Total Feedback", "0", delta="No feedback yet")
    
    with col3:
        if query_insights:
            st.metric(
                "Avg Response Time",
                f"{query_insights['avg_processing_time']:.0f}ms",
                delta=f"{query_insights['total_queries']} queries"
            )
        else:
            st.metric("Avg Response Time", "No data", delta="0 queries")
    
    with col4:
        if query_insights and query_insights['api_usage']:
            primary_api = max(query_insights['api_usage'], key=query_insights['api_usage'].get)
            st.metric(
                "Primary AI Model",
                primary_api.title(),
                delta=f"{query_insights['api_usage'][primary_api]} uses"
            )
        else:
            st.metric("Primary AI Model", "No data", delta="0 uses")
    
    # Feedback Analysis Section
    if feedback_insights:
        st.header("💬 Feedback Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Feedback distribution pie chart
            feedback_counts = [feedback_insights['positive_feedback'], feedback_insights['negative_feedback']]
            fig_pie = px.pie(
                values=feedback_counts,
                names=['Positive', 'Negative'],
                title="Feedback Distribution",
                color_discrete_sequence=['#10b981', '#ef4444']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Feedback over time
            if len(feedback_insights['df']) > 1:
                df_daily = feedback_insights['df'].set_index('timestamp').resample('D')['feedback'].value_counts().unstack(fill_value=0)
                
                fig_time = go.Figure()
                if 'positive' in df_daily.columns:
                    fig_time.add_trace(go.Scatter(x=df_daily.index, y=df_daily['positive'], mode='lines+markers', name='Positive', line=dict(color='#10b981')))
                if 'negative' in df_daily.columns:
                    fig_time.add_trace(go.Scatter(x=df_daily.index, y=df_daily['negative'], mode='lines+markers', name='Negative', line=dict(color='#ef4444')))
                
                fig_time.update_layout(title="Feedback Trends Over Time", xaxis_title="Date", yaxis_title="Feedback Count")
                st.plotly_chart(fig_time, use_container_width=True)
        
        # Intent satisfaction analysis (if available)
        if feedback_insights.get('intent_satisfaction'):
            st.subheader("📋 Satisfaction by Query Intent")
            intent_df = pd.DataFrame(list(feedback_insights['intent_satisfaction'].items()), columns=['Intent', 'Satisfaction %'])
            intent_df = intent_df.sort_values('Satisfaction %', ascending=True)
            
            fig_intent = px.bar(
                intent_df,
                x='Satisfaction %',
                y='Intent',
                orientation='h',
                title="User Satisfaction by Query Intent",
                color='Satisfaction %',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_intent, use_container_width=True)
        
        # Recent negative feedback
        if feedback_insights['negative_feedback'] > 0:
            st.subheader("⚠️ Recent Negative Feedback")
            negative_df = feedback_insights['df'][feedback_insights['df']['feedback'] == 'negative'].sort_values('timestamp', ascending=False).head(5)
            
            for _, row in negative_df.iterrows():
                with st.expander(f"🔍 {row['query'][:80]}..."):
                    st.write("**Query:**", row['query'])
                    st.write("**Response:**", row['response'])
                    if row.get('improvement_suggestion'):
                        st.write("**User Suggestion:**", row['improvement_suggestion'])
                    
                    # Show analytics if available
                    if 'analytics' in row and isinstance(row['analytics'], dict):
                        analytics = row['analytics']
                        st.write("**Analytics:**")
                        if analytics.get('intent_detected'):
                            st.write(f"- Intent: {analytics['intent_detected']}")
                        if analytics.get('cards_mentioned'):
                            st.write(f"- Cards: {', '.join(analytics['cards_mentioned'])}")
                        if analytics.get('categories_mentioned'):
                            st.write(f"- Categories: {', '.join(analytics['categories_mentioned'])}")
    
    # Query Analytics Section
    if query_insights:
        st.header("🔍 Query Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Intent distribution
            if query_insights['intent_distribution']:
                intent_df = pd.DataFrame(list(query_insights['intent_distribution'].items()), columns=['Intent', 'Count'])
                fig_intent_dist = px.pie(intent_df, values='Count', names='Intent', title="Query Intent Distribution")
                st.plotly_chart(fig_intent_dist, use_container_width=True)
        
        with col2:
            # Performance metrics
            perf_data = {
                'Metric': ['Data Retrieval', 'Response Generation', 'Total Processing'],
                'Time (ms)': [
                    query_insights['avg_data_retrieval'],
                    query_insights['avg_response_generation'],
                    query_insights['avg_processing_time']
                ]
            }
            fig_perf = px.bar(pd.DataFrame(perf_data), x='Metric', y='Time (ms)', title="Average Processing Times")
            st.plotly_chart(fig_perf, use_container_width=True)
        
        # Card popularity
        if query_insights['card_frequency']:
            st.subheader("🏦 Card Query Frequency")
            card_df = pd.DataFrame(list(query_insights['card_frequency'].items()), columns=['Card', 'Queries'])
            card_df = card_df.sort_values('Queries', ascending=True)
            
            fig_cards = px.bar(card_df, x='Queries', y='Card', orientation='h', title="Most Queried Cards")
            st.plotly_chart(fig_cards, use_container_width=True)
        
        # Processing time distribution
        if 'total_processing_time' in query_insights['analytics_df'].columns:
            st.subheader("⚡ Response Time Distribution")
            processing_times = query_insights['analytics_df']['total_processing_time'].dropna()
            
            fig_hist = px.histogram(
                processing_times,
                nbins=20,
                title="Response Time Distribution",
                labels={'value': 'Processing Time (ms)', 'count': 'Number of Queries'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
    
    # Export functionality
    st.header("📥 Data Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if feedback_insights and not feedback_insights['df'].empty:
            csv_feedback = feedback_insights['df'].to_csv(index=False)
            st.download_button(
                "Download Feedback Data",
                csv_feedback,
                "feedback_analytics.csv",
                "text/csv"
            )
    
    with col2:
        if query_insights and not query_insights['df'].empty:
            csv_queries = query_insights['df'].to_csv(index=False)
            st.download_button(
                "Download Query Analytics",
                csv_queries,
                "query_analytics.csv",
                "text/csv"
            )

if __name__ == "__main__":
    create_dashboard()