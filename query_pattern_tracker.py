"""
Query Pattern Tracker for Credit Card Chatbot
Analyzes user query patterns to identify trends and improve response quality.
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import re

class QueryPatternTracker:
    """
    Tracks and analyzes query patterns to enable intelligent insights and recommendations.
    """
    
    def __init__(self, analytics_file: str = "query_analytics.json", feedback_file: str = "feedback_log.json"):
        self.analytics_file = analytics_file
        self.feedback_file = feedback_file
        self.patterns = self._load_existing_patterns()
    
    def _load_existing_patterns(self) -> Dict:
        """Load existing pattern analysis from file."""
        patterns_file = "query_patterns.json"
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "trending_queries": [],
            "popular_intents": {},
            "seasonal_patterns": {},
            "user_journey_patterns": [],
            "query_success_rates": {},
            "last_updated": None
        }
    
    def analyze_query_patterns(self) -> Dict:
        """Analyze query patterns from analytics data."""
        
        # Load data
        query_data = self._load_query_analytics()
        feedback_data = self._load_feedback_data()
        
        if not query_data and not feedback_data:
            return self.patterns
        
        # Analyze different pattern types
        trending_queries = self._identify_trending_queries(query_data)
        popular_intents = self._analyze_intent_popularity(query_data)
        seasonal_patterns = self._detect_seasonal_patterns(query_data)
        success_rates = self._calculate_query_success_rates(query_data, feedback_data)
        user_journeys = self._analyze_user_journeys(feedback_data)
        
        # Update patterns
        self.patterns.update({
            "trending_queries": trending_queries,
            "popular_intents": popular_intents,
            "seasonal_patterns": seasonal_patterns,
            "query_success_rates": success_rates,
            "user_journey_patterns": user_journeys,
            "last_updated": datetime.now().isoformat()
        })
        
        # Save patterns
        self._save_patterns()
        
        return self.patterns
    
    def _load_query_analytics(self) -> List[Dict]:
        """Load query analytics data from persistent storage."""
        try:
            # Try persistent storage first (GitHub Gist)
            from persistent_storage import storage_manager
            return storage_manager.load_analytics_data()
        except Exception:
            # Fallback to local file
            if not os.path.exists(self.analytics_file):
                return []
            
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
    
    def _load_feedback_data(self) -> List[Dict]:
        """Load feedback data from persistent storage."""
        try:
            # Try persistent storage first (GitHub Gist)
            from persistent_storage import storage_manager
            return storage_manager.load_feedback_data()
        except Exception:
            # Fallback to local file
            if not os.path.exists(self.feedback_file):
                return []
            
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
    
    def _identify_trending_queries(self, query_data: List[Dict]) -> List[Dict]:
        """Identify trending queries based on frequency and recency."""
        if not query_data:
            return []
        
        # Group queries by similarity (simple keyword matching)
        query_groups = defaultdict(list)
        
        for item in query_data:
            query = item.get('query', '').lower()
            
            # Extract key terms for grouping
            key_terms = self._extract_key_terms(query)
            group_key = ' '.join(sorted(key_terms)[:3])  # Use top 3 terms
            
            query_groups[group_key].append({
                'query': item.get('query', ''),
                'timestamp': item.get('timestamp', ''),
                'analytics': item.get('analytics', {})
            })
        
        # Calculate trending score (frequency + recency)
        trending_queries = []
        now = datetime.now()
        
        for group_key, queries in query_groups.items():
            if len(queries) < 2:  # Only consider queries that appear multiple times
                continue
            
            # Calculate recency score (queries in last 24 hours get higher score)
            recent_count = 0
            today_count = 0
            total_count = len(queries)
            
            for query_item in queries:
                try:
                    query_time = datetime.fromisoformat(query_item['timestamp'])
                    hours_ago = (now - query_time).total_seconds() / 3600
                    if hours_ago <= 24:  # Last 24 hours
                        today_count += 1
                    if hours_ago <= 72:  # Last 3 days
                        recent_count += 1
                except:
                    continue
            
            # Trending score: (today * 3) + (recent * 2) + total
            trending_score = (today_count * 3) + (recent_count * 2) + total_count
            
            if trending_score >= 2:  # Lower threshold for faster detection
                trending_queries.append({
                    'query_pattern': group_key,
                    'sample_query': queries[0]['query'],
                    'total_count': total_count,
                    'today_count': today_count,
                    'recent_count': recent_count,
                    'trending_score': trending_score,
                    'last_seen': queries[-1]['timestamp']
                })
        
        # Sort by trending score
        trending_queries.sort(key=lambda x: x['trending_score'], reverse=True)
        return trending_queries[:10]  # Top 10 trending
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from a query for pattern matching."""
        # Remove common words and extract meaningful terms
        stop_words = {'i', 'a', 'an', 'the', 'is', 'are', 'was', 'were', 'will', 'would', 'should', 'could', 'can', 'do', 'does', 'did', 'have', 'has', 'had', 'for', 'in', 'on', 'at', 'to', 'from', 'with', 'by', 'of', 'and', 'or', 'but', 'if', 'then', 'what', 'how', 'when', 'where', 'why', 'which', 'who', 'whom'}
        
        # Extract words and numbers
        words = re.findall(r'\b[a-zA-Z]+\b|\d+', query.lower())
        
        # Filter out stop words and short words
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add specific credit card terms
        credit_terms = ['axis', 'atlas', 'icici', 'emeralde', 'epm', 'points', 'miles', 'rewards', 'lounge', 'fees', 'annual', 'joining']
        for term in credit_terms:
            if term in query.lower():
                key_terms.append(term)
        
        return list(set(key_terms))  # Remove duplicates
    
    def _analyze_intent_popularity(self, query_data: List[Dict]) -> Dict[str, Dict]:
        """Analyze the popularity of different query intents."""
        intent_stats = defaultdict(lambda: {'count': 0, 'recent_count': 0, 'avg_processing_time': 0})
        
        now = datetime.now()
        
        for item in query_data:
            analytics = item.get('analytics', {})
            intent = analytics.get('intent_detected', 'unknown')
            
            if intent:
                intent_stats[intent]['count'] += 1
                
                # Count recent queries (last 7 days)
                try:
                    query_time = datetime.fromisoformat(item.get('timestamp', ''))
                    if (now - query_time).days <= 7:
                        intent_stats[intent]['recent_count'] += 1
                except:
                    pass
                
                # Add processing time
                processing_time = analytics.get('total_processing_time', 0)
                if processing_time:
                    current_avg = intent_stats[intent]['avg_processing_time']
                    count = intent_stats[intent]['count']
                    intent_stats[intent]['avg_processing_time'] = (current_avg * (count - 1) + processing_time) / count
        
        return dict(intent_stats)
    
    def _detect_seasonal_patterns(self, query_data: List[Dict]) -> Dict[str, List]:
        """Detect seasonal patterns in queries."""
        if not query_data:
            return {}
        
        # Group queries by month and day of week
        monthly_patterns = defaultdict(list)
        weekly_patterns = defaultdict(list)
        hourly_patterns = defaultdict(list)
        
        for item in query_data:
            try:
                timestamp = datetime.fromisoformat(item.get('timestamp', ''))
                query = item.get('query', '')
                
                # Monthly patterns
                month_key = timestamp.strftime('%B')
                monthly_patterns[month_key].append(query)
                
                # Weekly patterns
                day_key = timestamp.strftime('%A')
                weekly_patterns[day_key].append(query)
                
                # Hourly patterns
                hour_key = timestamp.hour
                hourly_patterns[hour_key].append(query)
                
            except:
                continue
        
        return {
            'monthly': {month: len(queries) for month, queries in monthly_patterns.items()},
            'weekly': {day: len(queries) for day, queries in weekly_patterns.items()},
            'hourly': {hour: len(queries) for hour, queries in hourly_patterns.items()}
        }
    
    def _calculate_query_success_rates(self, query_data: List[Dict], feedback_data: List[Dict]) -> Dict[str, float]:
        """Calculate success rates for different query types."""
        # Create a mapping of queries to feedback
        feedback_map = {}
        for feedback in feedback_data:
            query = feedback.get('query', '')
            feedback_type = feedback.get('feedback', '')
            feedback_map[query] = feedback_type
        
        # Calculate success rates by intent
        intent_success = defaultdict(lambda: {'total': 0, 'positive': 0})
        
        for item in query_data:
            query = item.get('query', '')
            analytics = item.get('analytics', {})
            intent = analytics.get('intent_detected', 'unknown')
            
            if query in feedback_map:
                intent_success[intent]['total'] += 1
                if feedback_map[query] == 'positive':
                    intent_success[intent]['positive'] += 1
        
        # Calculate percentages
        success_rates = {}
        for intent, stats in intent_success.items():
            if stats['total'] > 0:
                success_rates[intent] = (stats['positive'] / stats['total']) * 100
        
        return success_rates
    
    def _analyze_user_journeys(self, feedback_data: List[Dict]) -> List[Dict]:
        """Analyze user journey patterns within sessions."""
        if not feedback_data:
            return []
        
        # Group by session
        session_journeys = defaultdict(list)
        
        for feedback in feedback_data:
            session_id = feedback.get('session_id')
            if session_id:
                session_journeys[session_id].append({
                    'query': feedback.get('query', ''),
                    'feedback': feedback.get('feedback', ''),
                    'timestamp': feedback.get('timestamp', ''),
                    'analytics': feedback.get('analytics', {})
                })
        
        # Analyze journey patterns
        journey_patterns = []
        
        for session_id, journey in session_journeys.items():
            if len(journey) > 1:  # Multi-query sessions only
                # Sort by timestamp
                journey.sort(key=lambda x: x.get('timestamp', ''))
                
                # Extract pattern
                query_sequence = []
                satisfaction_trend = []
                
                for step in journey:
                    analytics = step.get('analytics', {})
                    intent = analytics.get('intent_detected', 'unknown')
                    query_sequence.append(intent)
                    satisfaction_trend.append(1 if step.get('feedback') == 'positive' else 0)
                
                journey_patterns.append({
                    'session_id': session_id,
                    'query_sequence': query_sequence,
                    'satisfaction_trend': satisfaction_trend,
                    'total_queries': len(journey),
                    'satisfaction_rate': sum(satisfaction_trend) / len(satisfaction_trend) * 100
                })
        
        return journey_patterns
    
    def _save_patterns(self):
        """Save pattern analysis to file."""
        try:
            with open("query_patterns.json", 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception:
            pass  # Fail silently
    
    def get_trending_insights(self) -> Dict:
        """Get current trending insights for display."""
        self.analyze_query_patterns()  # Refresh patterns
        
        insights = {
            'top_trending_queries': self.patterns.get('trending_queries', [])[:5],
            'most_popular_intent': None,
            'peak_usage_time': None,
            'query_success_summary': {}
        }
        
        # Find most popular intent
        popular_intents = self.patterns.get('popular_intents', {})
        if popular_intents:
            most_popular = max(popular_intents.items(), key=lambda x: x[1].get('count', 0))
            insights['most_popular_intent'] = {
                'intent': most_popular[0],
                'count': most_popular[1].get('count', 0),
                'avg_processing_time': most_popular[1].get('avg_processing_time', 0)
            }
        
        # Find peak usage time
        seasonal_patterns = self.patterns.get('seasonal_patterns', {})
        hourly_patterns = seasonal_patterns.get('hourly', {})
        if hourly_patterns:
            peak_hour = max(hourly_patterns.items(), key=lambda x: x[1])
            insights['peak_usage_time'] = {
                'hour': peak_hour[0],
                'query_count': peak_hour[1]
            }
        
        # Success rate summary
        success_rates = self.patterns.get('query_success_rates', {})
        if success_rates:
            avg_success_rate = sum(success_rates.values()) / len(success_rates)
            best_intent = max(success_rates.items(), key=lambda x: x[1]) if success_rates else None
            worst_intent = min(success_rates.items(), key=lambda x: x[1]) if success_rates else None
            
            insights['query_success_summary'] = {
                'average_success_rate': avg_success_rate,
                'best_performing_intent': best_intent,
                'worst_performing_intent': worst_intent
            }
        
        return insights
    
    def get_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on patterns."""
        recommendations = []
        insights = self.get_trending_insights()
        
        # Trending query recommendations
        trending = insights.get('top_trending_queries', [])
        if trending:
            recommendations.append(f"📈 Consider adding quick answers for trending topic: '{trending[0].get('sample_query', 'N/A')}' (asked {trending[0].get('total_count', 0)} times recently)")
        
        # Success rate recommendations
        success_summary = insights.get('query_success_summary', {})
        worst_intent = success_summary.get('worst_performing_intent')
        if worst_intent and worst_intent[1] < 70:  # Less than 70% success rate
            recommendations.append(f"⚠️ Improve responses for '{worst_intent[0]}' queries (only {worst_intent[1]:.1f}% satisfaction rate)")
        
        # Usage pattern recommendations
        peak_time = insights.get('peak_usage_time')
        if peak_time:
            recommendations.append(f"⏰ Peak usage at hour {peak_time['hour']}. Consider monitoring system performance during this time.")
        
        # Popular intent recommendations
        popular_intent = insights.get('most_popular_intent')
        if popular_intent and popular_intent['avg_processing_time'] > 3000:  # > 3 seconds
            recommendations.append(f"🚀 Optimize '{popular_intent['intent']}' responses - they're popular but slow (avg {popular_intent['avg_processing_time']:.0f}ms)")
        
        return recommendations if recommendations else ["✅ No specific recommendations - system performing well!"]


if __name__ == "__main__":
    # Example usage
    tracker = QueryPatternTracker()
    patterns = tracker.analyze_query_patterns()
    insights = tracker.get_trending_insights()
    recommendations = tracker.get_recommendations()
    
    print("Query Pattern Analysis Results:")
    print(f"Trending Queries: {len(patterns.get('trending_queries', []))}")
    print(f"Popular Intents: {len(patterns.get('popular_intents', {}))}")
    print(f"Recommendations: {len(recommendations)}")