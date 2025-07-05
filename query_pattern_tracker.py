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
        query_complexity_trends = self._analyze_query_complexity(query_data, feedback_data)
        
        # Update patterns
        self.patterns.update({
            "trending_queries": trending_queries,
            "popular_intents": popular_intents,
            "seasonal_patterns": seasonal_patterns,
            "query_success_rates": success_rates,
            "user_journey_patterns": user_journeys,
            "query_complexity_trends": query_complexity_trends,
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
            group_key = ' '.join(sorted(key_terms))
            
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
        words = re.findall(r'\\b[a-zA-Z]+\\b|\\d+', query.lower())\n        \n        # Filter out stop words and short words\n        key_terms = [word for word in words if word not in stop_words and len(word) > 2]\n        \n        # Add specific credit card terms\n        credit_terms = ['axis', 'atlas', 'icici', 'emeralde', 'epm', 'points', 'miles', 'rewards', 'lounge', 'fees', 'annual', 'joining']\n        for term in credit_terms:\n            if term in query.lower():\n                key_terms.append(term)\n        \n        return list(set(key_terms))  # Remove duplicates\n    \n    def _analyze_intent_popularity(self, query_data: List[Dict]) -> Dict[str, Dict]:\n        \"\"\"Analyze the popularity of different query intents.\"\"\"\n        intent_stats = defaultdict(lambda: {'count': 0, 'recent_count': 0, 'avg_processing_time': 0})\n        \n        now = datetime.now()\n        \n        for item in query_data:\n            analytics = item.get('analytics', {})\n            intent = analytics.get('intent_detected', 'unknown')\n            \n            if intent:\n                intent_stats[intent]['count'] += 1\n                \n                # Count recent queries (last 7 days)\n                try:\n                    query_time = datetime.fromisoformat(item.get('timestamp', ''))\n                    if (now - query_time).days <= 7:\n                        intent_stats[intent]['recent_count'] += 1\n                except:\n                    pass\n                \n                # Add processing time\n                processing_time = analytics.get('total_processing_time', 0)\n                if processing_time:\n                    current_avg = intent_stats[intent]['avg_processing_time']\n                    count = intent_stats[intent]['count']\n                    intent_stats[intent]['avg_processing_time'] = (current_avg * (count - 1) + processing_time) / count\n        \n        return dict(intent_stats)\n    \n    def _detect_seasonal_patterns(self, query_data: List[Dict]) -> Dict[str, List]:\n        \"\"\"Detect seasonal patterns in queries.\"\"\"\n        if not query_data:\n            return {}\n        \n        # Group queries by month and day of week\n        monthly_patterns = defaultdict(list)\n        weekly_patterns = defaultdict(list)\n        hourly_patterns = defaultdict(list)\n        \n        for item in query_data:\n            try:\n                timestamp = datetime.fromisoformat(item.get('timestamp', ''))\n                query = item.get('query', '')\n                \n                # Monthly patterns\n                month_key = timestamp.strftime('%B')\n                monthly_patterns[month_key].append(query)\n                \n                # Weekly patterns\n                day_key = timestamp.strftime('%A')\n                weekly_patterns[day_key].append(query)\n                \n                # Hourly patterns\n                hour_key = timestamp.hour\n                hourly_patterns[hour_key].append(query)\n                \n            except:\n                continue\n        \n        return {\n            'monthly': {month: len(queries) for month, queries in monthly_patterns.items()},\n            'weekly': {day: len(queries) for day, queries in weekly_patterns.items()},\n            'hourly': {hour: len(queries) for hour, queries in hourly_patterns.items()}\n        }\n    \n    def _calculate_query_success_rates(self, query_data: List[Dict], feedback_data: List[Dict]) -> Dict[str, float]:\n        \"\"\"Calculate success rates for different query types.\"\"\"\n        # Create a mapping of queries to feedback\n        feedback_map = {}\n        for feedback in feedback_data:\n            query = feedback.get('query', '')\n            feedback_type = feedback.get('feedback', '')\n            feedback_map[query] = feedback_type\n        \n        # Calculate success rates by intent\n        intent_success = defaultdict(lambda: {'total': 0, 'positive': 0})\n        \n        for item in query_data:\n            query = item.get('query', '')\n            analytics = item.get('analytics', {})\n            intent = analytics.get('intent_detected', 'unknown')\n            \n            if query in feedback_map:\n                intent_success[intent]['total'] += 1\n                if feedback_map[query] == 'positive':\n                    intent_success[intent]['positive'] += 1\n        \n        # Calculate percentages\n        success_rates = {}\n        for intent, stats in intent_success.items():\n            if stats['total'] > 0:\n                success_rates[intent] = (stats['positive'] / stats['total']) * 100\n        \n        return success_rates\n    \n    def _analyze_user_journeys(self, feedback_data: List[Dict]) -> List[Dict]:\n        \"\"\"Analyze user journey patterns within sessions.\"\"\"\n        if not feedback_data:\n            return []\n        \n        # Group by session\n        session_journeys = defaultdict(list)\n        \n        for feedback in feedback_data:\n            session_id = feedback.get('session_id')\n            if session_id:\n                session_journeys[session_id].append({\n                    'query': feedback.get('query', ''),\n                    'feedback': feedback.get('feedback', ''),\n                    'timestamp': feedback.get('timestamp', ''),\n                    'analytics': feedback.get('analytics', {})\n                })\n        \n        # Analyze journey patterns\n        journey_patterns = []\n        \n        for session_id, journey in session_journeys.items():\n            if len(journey) > 1:  # Multi-query sessions only\n                # Sort by timestamp\n                journey.sort(key=lambda x: x.get('timestamp', ''))\n                \n                # Extract pattern\n                query_sequence = []\n                satisfaction_trend = []\n                \n                for step in journey:\n                    analytics = step.get('analytics', {})\n                    intent = analytics.get('intent_detected', 'unknown')\n                    query_sequence.append(intent)\n                    satisfaction_trend.append(1 if step.get('feedback') == 'positive' else 0)\n                \n                journey_patterns.append({\n                    'session_id': session_id,\n                    'query_sequence': query_sequence,\n                    'satisfaction_trend': satisfaction_trend,\n                    'total_queries': len(journey),\n                    'satisfaction_rate': sum(satisfaction_trend) / len(satisfaction_trend) * 100\n                })\n        \n        return journey_patterns\n    \n    def _analyze_query_complexity(self, query_data: List[Dict], feedback_data: List[Dict]) -> Dict:\n        \"\"\"Analyze relationship between query complexity and user satisfaction.\"\"\"\n        # Create feedback mapping\n        feedback_map = {feedback.get('query', ''): feedback.get('feedback', '') for feedback in feedback_data}\n        \n        complexity_analysis = {\n            'simple_queries': {'total': 0, 'positive': 0},\n            'medium_queries': {'total': 0, 'positive': 0},\n            'complex_queries': {'total': 0, 'positive': 0}\n        }\n        \n        for item in query_data:\n            query = item.get('query', '')\n            analytics = item.get('analytics', {})\n            \n            # Determine complexity\n            query_complexity = analytics.get('query_complexity', {})\n            word_count = query_complexity.get('word_count', 0)\n            has_comparison = query_complexity.get('has_comparison', False)\n            has_calculation = query_complexity.get('has_calculation', False)\n            has_conditional = query_complexity.get('has_conditional', False)\n            \n            # Complexity scoring\n            complexity_score = word_count\n            if has_comparison:\n                complexity_score += 5\n            if has_calculation:\n                complexity_score += 5\n            if has_conditional:\n                complexity_score += 3\n            \n            # Categorize complexity\n            if complexity_score <= 10:\n                category = 'simple_queries'\n            elif complexity_score <= 20:\n                category = 'medium_queries'\n            else:\n                category = 'complex_queries'\n            \n            # Check if we have feedback for this query\n            if query in feedback_map:\n                complexity_analysis[category]['total'] += 1\n                if feedback_map[query] == 'positive':\n                    complexity_analysis[category]['positive'] += 1\n        \n        # Calculate success rates\n        for category in complexity_analysis:\n            total = complexity_analysis[category]['total']\n            if total > 0:\n                positive = complexity_analysis[category]['positive']\n                complexity_analysis[category]['success_rate'] = (positive / total) * 100\n            else:\n                complexity_analysis[category]['success_rate'] = 0\n        \n        return complexity_analysis\n    \n    def _save_patterns(self):\n        \"\"\"Save pattern analysis to file.\"\"\"\n        try:\n            with open(\"query_patterns.json\", 'w') as f:\n                json.dump(self.patterns, f, indent=2)\n        except Exception:\n            pass  # Fail silently\n    \n    def get_trending_insights(self) -> Dict:\n        \"\"\"Get current trending insights for display.\"\"\"\n        self.analyze_query_patterns()  # Refresh patterns\n        \n        insights = {\n            'top_trending_queries': self.patterns.get('trending_queries', [])[:5],\n            'most_popular_intent': None,\n            'peak_usage_time': None,\n            'query_success_summary': {}\n        }\n        \n        # Find most popular intent\n        popular_intents = self.patterns.get('popular_intents', {})\n        if popular_intents:\n            most_popular = max(popular_intents.items(), key=lambda x: x[1].get('count', 0))\n            insights['most_popular_intent'] = {\n                'intent': most_popular[0],\n                'count': most_popular[1].get('count', 0),\n                'avg_processing_time': most_popular[1].get('avg_processing_time', 0)\n            }\n        \n        # Find peak usage time\n        seasonal_patterns = self.patterns.get('seasonal_patterns', {})\n        hourly_patterns = seasonal_patterns.get('hourly', {})\n        if hourly_patterns:\n            peak_hour = max(hourly_patterns.items(), key=lambda x: x[1])\n            insights['peak_usage_time'] = {\n                'hour': peak_hour[0],\n                'query_count': peak_hour[1]\n            }\n        \n        # Success rate summary\n        success_rates = self.patterns.get('query_success_rates', {})\n        if success_rates:\n            avg_success_rate = sum(success_rates.values()) / len(success_rates)\n            best_intent = max(success_rates.items(), key=lambda x: x[1]) if success_rates else None\n            worst_intent = min(success_rates.items(), key=lambda x: x[1]) if success_rates else None\n            \n            insights['query_success_summary'] = {\n                'average_success_rate': avg_success_rate,\n                'best_performing_intent': best_intent,\n                'worst_performing_intent': worst_intent\n            }\n        \n        return insights\n    \n    def get_recommendations(self) -> List[str]:\n        \"\"\"Generate actionable recommendations based on patterns.\"\"\"\n        recommendations = []\n        insights = self.get_trending_insights()\n        \n        # Trending query recommendations\n        trending = insights.get('top_trending_queries', [])\n        if trending:\n            recommendations.append(f\"📈 Consider adding quick answers for trending topic: '{trending[0].get('sample_query', 'N/A')}' (asked {trending[0].get('total_count', 0)} times recently)\")\n        \n        # Success rate recommendations\n        success_summary = insights.get('query_success_summary', {})\n        worst_intent = success_summary.get('worst_performing_intent')\n        if worst_intent and worst_intent[1] < 70:  # Less than 70% success rate\n            recommendations.append(f\"⚠️ Improve responses for '{worst_intent[0]}' queries (only {worst_intent[1]:.1f}% satisfaction rate)\")\n        \n        # Complexity recommendations\n        complexity_trends = self.patterns.get('query_complexity_trends', {})\n        complex_success = complexity_trends.get('complex_queries', {}).get('success_rate', 0)\n        if complex_success < 60:\n            recommendations.append(\"🧠 Complex queries have lower satisfaction. Consider simplifying responses or adding clarifying questions.\")\n        \n        # Usage pattern recommendations\n        peak_time = insights.get('peak_usage_time')\n        if peak_time:\n            recommendations.append(f\"⏰ Peak usage at hour {peak_time['hour']}. Consider monitoring system performance during this time.\")\n        \n        # Popular intent recommendations\n        popular_intent = insights.get('most_popular_intent')\n        if popular_intent and popular_intent['avg_processing_time'] > 3000:  # > 3 seconds\n            recommendations.append(f\"🚀 Optimize '{popular_intent['intent']}' responses - they're popular but slow (avg {popular_intent['avg_processing_time']:.0f}ms)\")\n        \n        return recommendations if recommendations else [\"✅ No specific recommendations - system performing well!\"]\n\n\nif __name__ == \"__main__\":\n    # Example usage\n    tracker = QueryPatternTracker()\n    patterns = tracker.analyze_query_patterns()\n    insights = tracker.get_trending_insights()\n    recommendations = tracker.get_recommendations()\n    \n    print(\"Query Pattern Analysis Results:\")\n    print(f\"Trending Queries: {len(patterns.get('trending_queries', []))}\")\n    print(f\"Popular Intents: {len(patterns.get('popular_intents', {}))}\")\n    print(f\"Recommendations: {len(recommendations)}\")"