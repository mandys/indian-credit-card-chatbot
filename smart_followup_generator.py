"""
Smart Follow-up Question Generator for Credit Card Chatbot
Generates contextually relevant follow-up questions based on user queries and patterns.
"""

import json
import random
from typing import List, Dict, Optional
from datetime import datetime

class SmartFollowupGenerator:
    """
    Generates intelligent follow-up questions based on query context, user history, and trending patterns.
    """
    
    def __init__(self):
        self.followup_templates = self._initialize_templates()
        self.trending_patterns = self._load_trending_patterns()
    
    def _initialize_templates(self) -> Dict[str, List[str]]:
        """Initialize follow-up question templates organized by intent and context."""
        return {
            "reward_calculation": [
                "Would you like to compare this with the other card's rewards?",
                "Are you interested in maximizing rewards for this spending category?",
                "Would you like to know about any spending caps for this category?",
                "Should I calculate the annual rewards for your typical spending pattern?",
                "Do you want to know about bonus multipliers for this category?"
            ],
            "feature_comparison": [
                "Which specific feature matters most to you?",
                "Would you like to know about the eligibility requirements for these cards?",
                "Are you interested in the joining and annual fees comparison?",
                "Should I explain the application process for the better option?",
                "Would you like to see a side-by-side benefits comparison?"
            ],
            "general_query": [
                "Would you like more details about any specific aspect?",
                "Are you comparing this with another card?",
                "Do you have questions about eligibility or application?",
                "Would you like to know about recent offers or promotions?",
                "Should I help you with a spending scenario calculation?"
            ],
            "redemption_query": [
                "Would you like to know the best redemption options for maximum value?",
                "Are you interested in transfer partners for better redemption rates?",
                "Should I explain the redemption process step-by-step?",
                "Would you like to compare redemption values across different options?",
                "Do you want to know about any redemption restrictions or expiry?"
            ],
            "lounge_access": [
                "Would you like to know about international lounge access?",
                "Are you interested in guest access policies?",
                "Should I help you find lounges at specific airports?",
                "Would you like to know about lounge access limits and restrictions?",
                "Do you want to compare lounge networks between cards?"
            ],
            "miles_transfer": [
                "Would you like to know about transfer ratios to specific airlines?",
                "Are you interested in transfer time and fees?",
                "Should I explain the best airlines for your travel routes?",
                "Would you like to know about transfer bonuses and promotions?",
                "Do you want to calculate the value of transferred miles?"
            ],
            "fee_query": [
                "Would you like to know about fee waiver conditions?",
                "Are you interested in ways to offset the annual fee?",
                "Should I explain the fee structure for additional cards?",
                "Would you like to compare the fee vs benefits value?",
                "Do you want to know about first-year fee offers?"
            ]
        }
    
    def _load_trending_patterns(self) -> Dict:
        """Load trending patterns to inform follow-up questions."""
        try:
            with open('query_patterns.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def generate_followup_questions(self, 
                                   user_query: str, 
                                   detected_intent: Optional[str] = None,
                                   cards_mentioned: List[str] = None,
                                   spending_amount: Optional[str] = None,
                                   categories_mentioned: List[str] = None,
                                   conversation_history: List[Dict] = None) -> List[str]:
        """Generate smart follow-up questions based on context."""
        
        followups = []
        cards_mentioned = cards_mentioned or []
        categories_mentioned = categories_mentioned or []
        conversation_history = conversation_history or []
        
        # Get intent-based follow-ups
        if detected_intent and detected_intent in self.followup_templates:
            intent_followups = self.followup_templates[detected_intent].copy()
            followups.extend(random.sample(intent_followups, min(2, len(intent_followups))))
        
        # Add context-specific follow-ups
        context_followups = self._generate_context_specific_followups(
            user_query, cards_mentioned, spending_amount, categories_mentioned
        )
        followups.extend(context_followups)
        
        # Add conversation-aware follow-ups
        conversation_followups = self._generate_conversation_followups(conversation_history)
        followups.extend(conversation_followups)
        
        # Add trending topic follow-ups
        trending_followups = self._generate_trending_followups(detected_intent)
        followups.extend(trending_followups)
        
        # Deduplicate and limit
        unique_followups = list(set(followups))
        
        # Prioritize and select best follow-ups
        prioritized_followups = self._prioritize_followups(unique_followups, user_query, detected_intent)
        
        return prioritized_followups[:3]  # Return top 3 follow-ups
    
    def _generate_context_specific_followups(self, 
                                           user_query: str,
                                           cards_mentioned: List[str],
                                           spending_amount: Optional[str],
                                           categories_mentioned: List[str]) -> List[str]:
        """Generate follow-ups based on specific context clues."""
        followups = []
        
        # Card-specific follow-ups
        if len(cards_mentioned) == 1:
            other_card = "ICICI Emeralde Private Metal" if "Atlas" in cards_mentioned[0] else "Axis Atlas"
            followups.append(f"Would you like to compare this with the {other_card} card?")
        elif len(cards_mentioned) == 0:
            followups.append("Which card are you most interested in - Axis Atlas or ICICI Emeralde Private Metal?")
        
        # Spending amount follow-ups
        if spending_amount:
            try:
                amount = float(spending_amount.replace(',', ''))
                if amount >= 100000:  # 1 lakh or more
                    followups.append("For this spending level, would you like to know about tier benefits and milestone rewards?")
                elif amount >= 50000:
                    followups.append("Would you like to see how to maximize rewards for this spending amount?")
                else:
                    followups.append("Are you looking to understand rewards for regular monthly spending?")
            except:
                pass
        
        # Category-specific follow-ups
        if "travel" in categories_mentioned:
            followups.extend([
                "Are you interested in travel insurance benefits?",
                "Would you like to know about airport lounge access?",
                "Should I explain foreign transaction fee waivers?"
            ])
        
        if "dining" in categories_mentioned:
            followups.extend([
                "Would you like to know about dining vouchers and offers?",
                "Are you interested in restaurant partnerships and discounts?"
            ])
        
        if "fuel" in categories_mentioned:
            followups.append("Would you like to know about fuel surcharge waivers?")
        
        if "education" in categories_mentioned:
            followups.append("Are you looking at education loan payment options or fee payments?")
        
        # Query complexity follow-ups
        if any(word in user_query.lower() for word in ["better", "best", "recommend"]):
            followups.append("What's your primary use case - travel, dining, or general spending?")
        
        if "if" in user_query.lower() or "what if" in user_query.lower():
            followups.append("Would you like me to calculate a few different spending scenarios?")
        
        return followups
    
    def _generate_conversation_followups(self, conversation_history: List[Dict]) -> List[str]:
        """Generate follow-ups based on conversation history."""
        followups = []
        
        if not conversation_history:
            return followups
        
        # Analyze recent messages (last 3)
        recent_messages = conversation_history[-3:]
        user_messages = [msg for msg in recent_messages if msg.get('role') == 'user']
        
        if len(user_messages) >= 2:
            # Multi-query session - suggest comprehensive comparison
            followups.append("Since you're exploring multiple aspects, would you like a comprehensive card comparison?")
            
            # Check for pattern in queries
            queries = [msg.get('content', '').lower() for msg in user_messages]
            
            if any("fee" in query for query in queries) and any("reward" in query for query in queries):
                followups.append("Would you like to see a cost-benefit analysis comparing both cards?")
            
            if any("travel" in query for query in queries):
                followups.append("Are you planning a specific trip? I can help optimize card benefits for your travel.")
        
        # First-time user follow-ups
        if len(user_messages) == 1:
            followups.extend([
                "Is this your first credit card, or are you looking to upgrade?",
                "Would you like to know about the application process and eligibility?"
            ])
        
        return followups
    
    def _generate_trending_followups(self, detected_intent: Optional[str]) -> List[str]:
        """Generate follow-ups based on trending topics and patterns."""
        followups = []
        
        trending_patterns = self.trending_patterns.get('trending_queries', [])
        if not trending_patterns:
            return followups
        
        # Get trending topics related to current intent
        for trend in trending_patterns[:3]:  # Top 3 trends
            sample_query = trend.get('sample_query', '').lower()
            
            if detected_intent == 'reward_calculation' and 'reward' in sample_query:
                followups.append("Many users are asking about reward optimization - would you like personalized tips?")
            
            elif detected_intent == 'lounge_access' and 'lounge' in sample_query:
                followups.append("Lounge access is trending - would you like to know about upcoming lounge expansions?")
            
            elif 'travel' in sample_query and detected_intent in ['reward_calculation', 'feature_comparison']:
                followups.append("Travel rewards are popular right now - interested in travel-specific benefits?")
        
        # Seasonal follow-ups based on patterns
        current_month = datetime.now().strftime('%B')
        seasonal_patterns = self.trending_patterns.get('seasonal_patterns', {}).get('monthly', {})
        
        if seasonal_patterns.get(current_month, 0) > 0:
            if current_month in ['December', 'January']:  # Holiday season
                followups.append("Holiday season is here - interested in bonus category offers and shopping rewards?")
            elif current_month in ['March', 'April']:  # Tax season
                followups.append("Tax season - would you like to know about payment options and reward earning on tax payments?")
            elif current_month in ['June', 'July', 'August']:  # Travel season
                followups.append("Travel season - interested in maximizing travel rewards and benefits?")
        
        return followups
    
    def _prioritize_followups(self, followups: List[str], user_query: str, detected_intent: Optional[str]) -> List[str]:
        """Prioritize follow-up questions based on relevance and context."""
        if not followups:
            return []
        
        # Scoring system for prioritization
        scored_followups = []
        
        for followup in followups:
            score = 0
            
            # Higher score for intent-matched follow-ups
            if detected_intent and detected_intent in self.followup_templates:
                if followup in self.followup_templates[detected_intent]:
                    score += 10
            
            # Higher score for query keyword matches
            query_words = user_query.lower().split()
            followup_words = followup.lower().split()
            common_words = set(query_words) & set(followup_words)
            score += len(common_words) * 2
            
            # Specific keyword bonuses
            if "compare" in user_query.lower() and "compar" in followup.lower():
                score += 5
            if "reward" in user_query.lower() and "reward" in followup.lower():
                score += 5
            if "fee" in user_query.lower() and "fee" in followup.lower():
                score += 5
            
            # Deduct score for generic questions
            if followup.startswith("Would you like more details"):
                score -= 2
            
            # Boost score for actionable follow-ups
            if any(word in followup.lower() for word in ["calculate", "compare", "explain", "help"]):
                score += 3
            
            scored_followups.append((followup, score))
        
        # Sort by score (descending) and return questions
        scored_followups.sort(key=lambda x: x[1], reverse=True)
        return [q[0] for q in scored_followups]


if __name__ == "__main__":
    # Example usage
    generator = SmartFollowupGenerator()
    
    # Test follow-up generation
    followups = generator.generate_followup_questions(
        user_query="What rewards will I get for spending 50000 on dining?",
        detected_intent="reward_calculation",
        cards_mentioned=["Axis Atlas"],
        spending_amount="50000",
        categories_mentioned=["dining"]
    )
    
    print("Generated Follow-ups:")
    for i, followup in enumerate(followups, 1):
        print(f"{i}. {followup}")