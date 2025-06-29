import os
import re
import json
import random
import openai
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

class RichDataCreditCardBot:
    """
    A chatbot engineered to understand a rich, nested JSON structure with common and card-specific terms.
    """
    def __init__(self, data_files: list[str]):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._load_credit_card_data(data_files)
        self._setup_intent_patterns()

    def _load_credit_card_data(self, data_files: list[str]):
        """Loads all credit card data from the provided list of files into a structured format."""
        self.cards_data: Dict[str, Dict[str, Any]] = {}
        self.common_terms: Dict[str, Any] = {}
        self.card_name_map: Dict[str, str] = {}
        
        for filepath in data_files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if "common_terms" in data:
                        self.common_terms.update(data["common_terms"])
                    if "cards" in data and isinstance(data["cards"], list):
                        for card in data["cards"]:
                            card_name = card.get("name")
                            if card_name:
                                self.cards_data[card_name] = card
                                self.card_name_map[card_name] = self._generate_keywords(card_name)
            except FileNotFoundError:
                print(f"Warning: Data file not found at {filepath}")
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON from {filepath}")

    def _generate_keywords(self, name: str) -> List[str]:
        """Generates searchable keywords from a card name."""
        return [word.lower() for word in name.split() if len(word) > 3 and word.lower() not in ['bank', 'card', 'credit']]

    def _setup_intent_patterns(self):
        """Define regex patterns for each potential intent."""
        # Consolidate all possible keys from cards and common terms
        all_keys = set(self.common_terms.keys())
        for card in self.cards_data.values():
            all_keys.update(card.keys())

        patterns = {key.replace('_', ' '): [key.replace('_', ' ')] for key in all_keys}
        
        # Add more specific, human-like patterns
        specific_patterns = {
            'fees': [r'fee', r'charge', r'cost', r'price'],
            'welcome_benefits': [r'welcome', r'joining bonus', r'sign-up'],
            'rewards': [r'reward', r'point', r'earn rate', r'cashback'],
            'milestones': [r'milestone'],
            'tier_structure': [r'tier', r'status', 'level'],
            'lounge_access': [r'lounge', r'airport'],
            'miles_transfer': [r'miles transfer', r'partner', r'conversion'],
            'insurance': [r'insurance'],
            'eligibility': [r'eligibility', r'eligible', r'apply'],
            'finance_charges': [r'finance charge', r'interest rate'],
            'education': [r'education'],
            'fuel': [r'fuel'],
            'rent': [r'rent'],
            'wallet': [r'wallet'],
            'utilities': [r'utilities'],
            'gaming': [r'gaming'],
            'government': [r'government', r'govt', r'tax'],
            'telecom': [r'telecom'],
            'insurance': [r'insurance'],
            'gold': [r'gold', r'jewellery']
        }
        
        for intent, regex_list in specific_patterns.items():
            if intent in patterns:
                patterns[intent].extend(regex_list)
            else:
                patterns[intent] = regex_list
        
        self.intent_patterns = patterns
        self.spend_category_intents = ['education', 'fuel', 'rent', 'wallet', 'utilities', 'insurance', 'gaming', 'government', 'gold', 'jewellery']

    def detect_intent(self, query: str) -> Optional[str]:
        """Detect intent using regex pattern matching."""
        query_lower = query.lower()
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # This maps a human-friendly key back to the actual JSON key
                    return intent.replace(' ', '_') 
        return None

    def extract_card_names(self, query: str) -> List[str]:
        """Extract all card names mentioned in the query."""
        query_lower = query.lower()
        found_cards = set()
        for card_name, keywords in self.card_name_map.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_cards.add(card_name)
        return list(found_cards)
        
    def get_greeting(self) -> str:
        """A standard, welcoming greeting."""
        return "Hello! How can I help you with your credit card questions today?"
    
    def detect_greeting(self, query: str) -> bool:
        """Check if user is just saying hello."""
        greetings = ['hello', 'hi', 'hey']
        return any(greeting in query.lower() for greeting in greetings) and len(query.split()) <= 2

    def get_relevant_data(self, intent: Optional[str], card_names: List[str]) -> Dict:
        """Get relevant data based on the new nested structure, handling spend categories intelligently."""
        # If the intent is a spend category, gather a comprehensive context.
        if intent and intent.replace('_', ' ') in self.spend_category_intents and card_names:
            context = {}
            for name in card_names:
                if name in self.cards_data:
                    card_info = self.cards_data[name]
                    card_context = {}
                    # Check for surcharges in common terms
                    if 'surcharge_fees' in self.common_terms:
                        surcharge_key = intent.replace('_', ' ')
                        if surcharge_key in self.common_terms['surcharge_fees']:
                            card_context['surcharge_info'] = {surcharge_key: self.common_terms['surcharge_fees'][surcharge_key]}
                    # Check for rewards and their exclusions
                    if 'rewards' in card_info:
                        card_context['rewards_info'] = {
                            'base_rate': card_info['rewards'].get('others'),
                            'exclusions': card_info['rewards'].get('spend_exclusion_policy')
                        }
                    # Check for milestone eligibility exclusions
                    if 'milestone_eligibility' in card_info:
                        card_context['milestone_eligibility_exclusions'] = card_info['milestone_eligibility'].get('spend_exclusion_policies')
                        
                    context[name] = card_context
            return context

        # Fallback to original logic for other intents
        if intent and intent in self.common_terms:
            return {"common_terms": {intent: self.common_terms[intent]}}

        if card_names:
            context = {}
            for name in card_names:
                if name in self.cards_data:
                    card_info = self.cards_data[name]
                    if intent and intent in card_info:
                        context[name] = {intent: card_info[intent]}
                    elif not intent:
                        context[name] = card_info
            return context
            
        return {}

    def generate_answer(self, query: str, relevant_data: dict, intent: Optional[str]) -> str:
        """
        Generates an answer using OpenAI API based on the relevant data.
        """
        context = json.dumps(relevant_data, indent=2)

        # Define two separate prompts based on the intent
        if intent in self.spend_category_intents:
            system_prompt = f"""
You are a credit card expert. A user is asking about a specific spending category: '{intent}'.
Your task is to answer their question based ONLY on the provided JSON data.

- If the data contains an "exclusions" list and the user's category ('{intent}') is mentioned there, you MUST clarify the following:
    1. The user *can* still make the transaction with their card.
    2. However, they will *not* earn any rewards, points, or benefits for that transaction because it is an excluded category.
- If the category is NOT in the exclusions list, confirm that they will earn the standard rewards.
- Do not invent information. If the data is missing, say so.
- Keep the answer helpful, clear, and concise.
"""
        else:
            system_prompt = """
You are a friendly and knowledgeable credit card expert. Your goal is to provide clear, helpful, and concise answers with a touch of personality.
Do not invent or assume any information not present in the data.
If the information is not in the provided data, just say that you don't have that information.
Keep your answers direct and to the point.
"""
        prompt = f"""
{system_prompt}

CONTEXT:
{context}
"""
        # Call the OpenAI API
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.5,
                max_tokens=350
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"I'm sorry, I encountered an error: {e}"

    def get_answer(self, user_query: str) -> str:
        """Main method to process a query and return an answer."""
        if self.detect_greeting(user_query):
            return self.get_greeting()

        intent = self.detect_intent(user_query)
        card_names = self.extract_card_names(user_query)
        
        relevant_data = self.get_relevant_data(intent, card_names)
        answer = self.generate_answer(user_query, relevant_data, intent)
        
        return answer

if __name__ == '__main__':
    bot = RichDataCreditCardBot()
    
    print("--- Testing with New Data Structure ---")
    test_q1 = "What are the finance charges?"
    print(f"Q: {test_q1}\nA: {bot.get_answer(test_q1)}")
    
    test_q2 = "Tell me about dining benefits on the atlas card"
    print(f"\nQ: {test_q2}\nA: {bot.get_answer(test_q2)}")

    test_q3 = "what is the tier structure for axis atlas?"
    print(f"\nQ: {test_q3}\nA: {bot.get_answer(test_q3)}")

    test_q4 = "Can you tell me about education spends of axis atlas"
    print(f"\nQ: {test_q4}\nA: {bot.get_answer(test_q4)}")

    test_q5 = "Can you tell me if I can make government tax payments using axis atlas"
    print(f"\nQ: {test_q5}\nA: {bot.get_answer(test_q5)}")
