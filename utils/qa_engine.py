import os
import re
import json
import random
import openai
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional

class RuleBasedCreditCardBot:
    """
    A fast, rule-based chatbot for credit card Q&A with a fun and chatty personality.
    It uses regex for intent/entity detection and a single API call for answer generation.
    """
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.credit_card_data = self._load_credit_card_data()
        self.intent_patterns = self._setup_intent_patterns()
        self.card_name_patterns = self._setup_card_name_patterns()

    def _load_credit_card_data(self) -> Dict[str, Dict]:
        """Loads all credit card data from the data/ directory."""
        card_data = {}
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        if not os.path.exists(data_dir):
            return {}
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    card_name = data.get("card_name")
                    if card_name:
                        card_data[card_name] = data
        return card_data

    def _setup_intent_patterns(self) -> Dict[str, List[str]]:
        """Define regex patterns for each top-level JSON key (intent)."""
        return {
            'annual_fee': [r'annual fee', r'joining fee', r'cost', r'price', r'charge'],
            'foreign_currency_markup_fee': [r'foreign currency', r'fx markup', r'forex', r'currency conversion', r'international transaction'],
            'welcome_benefit': [r'welcome benefit', r'joining bonus', r'sign-up offer'],
            'reward_point_structure': [r'reward', r'point', r'earn rate', r'cashback', r'milestone'],
            'mcc_exclusions': [r'mcc', r'merchant code', r'exclusion', r'not eligible', r'not count'],
            'tier_details': [r'tier', r'status', r'level', r'upgrade', r'downgrade'],
            'lounge_access': [r'lounge', r'airport access'],
            'miles_transfer_program': [r'miles transfer', r'partner', r'conversion'],
            'additional_benefits': [r'additional benefit', r'extra', r'insurance', r'golf', r'concierge']
        }

    def _setup_card_name_patterns(self) -> Dict[str, List[str]]:
        """Define keywords to identify each card."""
        patterns = {}
        for name in self.credit_card_data.keys():
            keywords = [word.lower() for word in name.split() if len(word) > 3 and word.lower() not in ['bank', 'card', 'credit']]
            patterns[name] = keywords
        return patterns

    def detect_intent(self, query: str) -> Tuple[Optional[str], float]:
        """Detect intent using pattern matching and return a confidence score."""
        query_lower = query.lower()
        best_intent = None
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, query_lower))
            normalized_score = score / len(patterns)
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_intent = intent
        
        return best_intent, best_score

    def extract_card_names(self, query: str) -> List[str]:
        """Extract all card names mentioned in the query."""
        query_lower = query.lower()
        found_cards = set()
        for card_name, keywords in self.card_name_patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_cards.add(card_name)
        return list(found_cards)
        
    def get_greeting(self) -> str:
        """Fun greeting message"""
        greetings = [
            "Hey there! 👋 Ready to dive into the exciting world of credit cards? (Yes, I just called credit cards exciting - deal with it! 😄)",
            "Welcome to your friendly neighborhood credit card guru! 🦸‍♂️ What card mysteries can I solve for you today?",
            "Hello! I'm here to make credit cards less confusing and more fun. Ask me anything - I promise not to bore you to death! 😊",
            "Hi! Think of me as your credit card wingman. I've got all the insider info and I'm not afraid to share it! 🎯"
        ]
        return random.choice(greetings)
    
    def detect_greeting(self, query: str) -> bool:
        """Check if user is just saying hello."""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in query.lower() for greeting in greetings) and len(query.split()) <= 3

    def get_relevant_data(self, intent: Optional[str], card_names: List[str]) -> Dict:
        """Get relevant data based on intent and a list of cards."""
        # Handle comparison queries with multiple cards
        if len(card_names) > 1 and intent:
            comparison_data = {}
            for name in card_names:
                if name in self.credit_card_data and intent in self.credit_card_data[name]:
                    comparison_data[name] = {intent: self.credit_card_data[name][intent]}
            return comparison_data

        # Handle single card queries
        if len(card_names) == 1:
            card_name = card_names[0]
            if card_name in self.credit_card_data:
                card_data = self.credit_card_data[card_name]
                if intent and intent in card_data:
                    return {card_name: {intent: card_data[intent]}}
                else:
                    return {card_name: card_data} # Return full data if intent unclear

        # Handle queries with an intent but no specified card
        if not card_names and intent:
            relevant_data = {}
            for name, data in self.credit_card_data.items():
                if intent in data:
                    relevant_data[name] = {intent: data[intent]}
            return relevant_data
            
        return {}

    def generate_answer(self, query: str, relevant_data: Dict) -> str:
        """Generate a chatty, helpful answer using a single LLM call."""
        if not relevant_data:
            return """
Oops! 🤔 I'm like a detective without clues here! I couldn't find the specific information you're looking for in my credit card database. 

Maybe try being a bit more specific? For example, instead of asking "tell me about rewards," try "what are the milestone benefits for the Axis Atlas card?" 

I promise I'm usually much more helpful than this! 😅
"""
        
        context = json.dumps(relevant_data, indent=2)
        
        prompt = f"""
Answer the following question using the credit card data provided. Be friendly, clear, and direct. Get straight to the point. Keep the answer to a single short paragraph. Use emojis sparingly, if at all. Avoid long explanations unless absolutely necessary.

Question: {query}

Relevant Data:
{context}

Instructions for your response:
- Be friendly, clear, and direct.
- Get straight to the point.
- Keep the answer to a single short paragraph.
- Use emojis sparingly, if at all.

Provide a clear and direct answer based on the data above.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and clear credit card expert. You provide accurate, direct answers in a friendly and professional tone. You avoid excessive humor and get straight to the point."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=250
        )
        
        return response.choices[0].message.content

    def get_answer(self, user_query: str) -> str:
        """Main method: uses a rule-based engine and a single API call."""
        if not self.client.api_key or self.client.api_key == "your-api-key-here":
            return "Error: OPENAI_API_KEY is not set. Please set it in your .env file."
        
        try:
            # Check for simple greetings first
            if self.detect_greeting(user_query):
                return self.get_greeting()

            intent, confidence = self.detect_intent(user_query)
            card_names = self.extract_card_names(user_query)

            if confidence < 0.2 and not card_names:
                return """
Hmm, I'm scratching my head a bit here! 🤔 Your question is a bit like asking "what's that thing about that stuff?" - I need a bit more to work with!

Try asking something like:
- "What are the MCC exclusions for ICICI cards?"
- "What's the annual fee for the Axis Atlas?"

I'm much better when I know what you're looking for! 😊
"""
            
            relevant_data = self.get_relevant_data(intent, card_names)
            answer = self.generate_answer(user_query, relevant_data)
            return answer
            
        except Exception as e:
            return f"""
Oops! Something went wrong in my digital brain! 🤖💥 

Technical details (for the nerds): {str(e)}

But don't worry, just try asking your question again - I'm usually much more reliable than this embarrassing moment suggests! 😅
"""

if __name__ == '__main__':
    bot = RuleBasedCreditCardBot()
    print("Loaded cards:", list(bot.credit_card_data.keys()))
    
    test_question = "hi"
    print(f"\nQ: {test_question}")
    print("A:", bot.get_answer(test_question))

    test_question_2 = "what is the annual fee for axis atlas"
    print(f"\nQ: {test_question_2}")
    print("A:", bot.get_answer(test_question_2))

    test_question_3 = "between icici epm and axis atlas which has less forex markup fee"
    print(f"\nQ: {test_question_3}")
    print("A:", bot.get_answer(test_question_3))
