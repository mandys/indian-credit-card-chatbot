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
        self.bank_common_terms: Dict[str, Dict[str, Any]] = {}  # Store common terms per bank
        self.card_name_map: Dict[str, str] = {}
        
        for filepath in data_files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                    # Determine bank name from file path
                    bank_name = filepath.split('/')[-1].split('-')[0]  # e.g., 'axis' from 'axis-atlas.json'
                    
                    if "common_terms" in data:
                        self.bank_common_terms[bank_name] = data["common_terms"]
                        
                    if "cards" in data and isinstance(data["cards"], list):
                        for card in data["cards"]:
                            card_name = card.get("name")
                            if card_name:
                                # Store the bank name with the card for later reference
                                card["_bank"] = bank_name
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
        # Consolidate all possible keys from cards and bank common terms
        all_keys = set()
        for bank_terms in self.bank_common_terms.values():
            all_keys.update(bank_terms.keys())
        for card in self.cards_data.values():
            all_keys.update(card.keys())

        patterns = {key.replace('_', ' '): [key.replace('_', ' ')] for key in all_keys}
        
        # Add more specific, human-like patterns
        specific_patterns = {
            'fees': [r'fee', r'charge', r'cost', r'price'],
            'welcome_benefits': [r'welcome', r'joining bonus', r'sign-up'],
            'rewards': [r'reward', r'point', r'earn rate', r'cashback'],
            'reward_comparison': [r'which card.*more reward', r'which.*better reward', r'compare reward', r'more reward', r'better reward', r'which card.*spend.*reward', r'reward.*comparison'],
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
        
        # Check for reward comparison queries first (more specific)
        if re.search(r'which.*card.*(more|better).*reward', query_lower) or \
           re.search(r'(compare|comparison).*reward', query_lower) or \
           re.search(r'spend.*\d+.*which.*card', query_lower) or \
           re.search(r'spend.*\d+.*(vs|versus)', query_lower) or \
           re.search(r'(icici|axis|atlas|emeralde).*(vs|versus).*(icici|axis|atlas|emeralde)', query_lower) or \
           re.search(r'which.*better.*spend.*\d+', query_lower) or \
           re.search(r'better.*reward.*\d+', query_lower):
            return 'reward_comparison'
        
        # Check for specific spending categories first (more specific than general fees)
        spending_category_checks = {
            'utilities': [r'utilit(y|ies)', r'utility.*spend', r'utility.*charge', r'utility.*fee'],
            'fuel': [r'fuel', r'petrol', r'gas station'],
            'rent': [r'rent', r'rental'],
            'education': [r'education', r'school', r'college', r'university'],
            'insurance': [r'insurance'],
            'government': [r'government', r'govt', r'tax payment'],
            'gaming': [r'gaming', r'game'],
            'wallet': [r'wallet', r'paytm', r'phonepe', r'gpay'],
            'gold': [r'gold', r'jewellery', r'jewelry']
        }
        
        for category, patterns in spending_category_checks.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return category
        
        # Then check for other intents
        for intent, patterns in self.intent_patterns.items():
            # Skip spending categories as we already checked them above
            if intent in spending_category_checks:
                continue
                
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

    def extract_spend_amount(self, query: str) -> Optional[int]:
        """Extract spend amount from query."""
        import re
        # Look for numbers in the query
        numbers = re.findall(r'\d+', query)
        if numbers:
            # Take the largest number as the spend amount
            return max(int(num) for num in numbers)
        return None

    def calculate_rewards(self, card_name: str, spend_amount: int) -> Dict:
        """Calculate rewards for a specific card and spend amount."""
        if card_name not in self.cards_data:
            return {"error": f"Card {card_name} not found"}
        
        card_info = self.cards_data[card_name]
        
        # Handle ICICI Emeralde Private Metal
        if "ICICI" in card_name and "Emeralde" in card_name:
            # ICICI: 6 points per ₹200 spent
            points = (spend_amount // 200) * 6
            return {
                "card": card_name,
                "spend_amount": spend_amount,
                "points_earned": points,
                "rate": "6 points per ₹200",
                "calculation": f"₹{spend_amount} ÷ 200 × 6 = {points} points"
            }
        
        # Handle Axis Atlas
        elif "Axis" in card_name and "Atlas" in card_name:
            # Atlas: 2 EDGE Miles per ₹100 for general spend
            miles = (spend_amount // 100) * 2
            return {
                "card": card_name,
                "spend_amount": spend_amount,
                "miles_earned": miles,
                "rate": "2 EDGE Miles per ₹100",
                "calculation": f"₹{spend_amount} ÷ 100 × 2 = {miles} miles"
            }
        
        return {"error": f"Reward calculation not implemented for {card_name}"}

    def get_relevant_data(self, intent: Optional[str], card_names: List[str]) -> Dict:
        """Get relevant data based on the new nested structure, handling spend categories intelligently."""
        # Handle reward comparison queries
        if intent == 'reward_comparison':
            context = {}
            # If no specific cards mentioned, compare all available cards
            if not card_names:
                card_names = list(self.cards_data.keys())
            
            for name in card_names:
                if name in self.cards_data:
                    card_info = self.cards_data[name]
                    context[name] = {
                        'rewards': card_info.get('rewards', {}),
                        'name': name
                    }
            return context
        
        # If the intent is a spend category, gather a comprehensive context.
        if intent and intent.replace('_', ' ') in self.spend_category_intents and card_names:
            context = {}
            for name in card_names:
                if name in self.cards_data:
                    card_info = self.cards_data[name]
                    card_context = {}
                    
                    # Get the bank for this card and use its common terms
                    bank = card_info.get('_bank')
                    if bank and bank in self.bank_common_terms:
                        bank_terms = self.bank_common_terms[bank]
                        # Check for surcharges in bank-specific common terms
                        if 'surcharge_fees' in bank_terms:
                            surcharge_key = intent  # Use intent directly since we're looking for 'utilities', not 'utilities '
                            if surcharge_key in bank_terms['surcharge_fees']:
                                card_context['surcharge_info'] = {surcharge_key: bank_terms['surcharge_fees'][surcharge_key]}
                    # Check for rewards and their exclusions
                    if 'rewards' in card_info:
                        rewards = card_info['rewards']
                        exclusions = None
                        
                        # Check for exclusions in different formats
                        if 'spend_exclusion_policy' in rewards:
                            exclusions = rewards['spend_exclusion_policy']
                        elif 'accrual_exclusions' in rewards:
                            exclusions = rewards['accrual_exclusions']
                            
                        card_context['rewards_info'] = {
                            'base_rate': rewards.get('others'),
                            'exclusions': exclusions
                        }
                    # Check for milestone eligibility exclusions
                    if 'milestone_eligibility' in card_info:
                        card_context['milestone_eligibility_exclusions'] = card_info['milestone_eligibility'].get('spend_exclusion_policies')
                        
                    context[name] = card_context
            return context

        # Fallback to original logic for other intents - check all banks' common terms
        if intent:
            for bank, bank_terms in self.bank_common_terms.items():
                if intent in bank_terms:
                    return {"common_terms": {intent: bank_terms[intent]}}

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
        # Handle reward comparison queries with calculations
        if intent == 'reward_comparison':
            spend_amount = self.extract_spend_amount(query)
            if spend_amount and relevant_data:
                calculations = []
                for card_name in relevant_data.keys():
                    calc_result = self.calculate_rewards(card_name, spend_amount)
                    if 'error' not in calc_result:
                        calculations.append(calc_result)
                
                if calculations:
                    # Create a detailed comparison
                    comparison_text = f"For spending ₹{spend_amount:,}:\n\n"
                    
                    for calc in calculations:
                        if 'points_earned' in calc:
                            comparison_text += f"**{calc['card']}**: {calc['points_earned']} points\n"
                            comparison_text += f"- Rate: {calc['rate']}\n"
                            comparison_text += f"- Calculation: {calc['calculation']}\n\n"
                        elif 'miles_earned' in calc:
                            comparison_text += f"**{calc['card']}**: {calc['miles_earned']} miles\n"
                            comparison_text += f"- Rate: {calc['rate']}\n"
                            comparison_text += f"- Calculation: {calc['calculation']}\n\n"
                    
                    # Determine winner
                    if len(calculations) >= 2:
                        icici_points = next((c['points_earned'] for c in calculations if 'points_earned' in c), 0)
                        atlas_miles = next((c['miles_earned'] for c in calculations if 'miles_earned' in c), 0)
                        
                        if icici_points > atlas_miles:
                            comparison_text += f"**Winner**: ICICI Emeralde gives you more rewards ({icici_points} points vs {atlas_miles} miles)"
                        elif atlas_miles > icici_points:
                            comparison_text += f"**Winner**: Axis Atlas gives you more rewards ({atlas_miles} miles vs {icici_points} points)"
                        else:
                            comparison_text += "**Result**: Both cards give similar reward value"
                    
                    return comparison_text
                else:
                    return "I couldn't calculate rewards for the specified cards. Please make sure you're asking about supported cards."
            else:
                return "Please specify a spend amount to compare rewards (e.g., 'If I spend ₹100,000 which card gives more rewards?')"
        
        context = json.dumps(relevant_data, indent=2)

        # Define two separate prompts based on the intent
        if intent in self.spend_category_intents:
            system_prompt = f"""
You are a credit card expert. A user is asking about a specific spending category: '{intent}'.
Your task is to answer their question based ONLY on the provided JSON data.

IMPORTANT: Address BOTH fees AND rewards in your response:

1. FEES/CHARGES: If there's surcharge_info in the data, mention any fees or charges for this category.

2. REWARDS: 
   - Check if the category appears in any exclusions list:
     * For Axis cards: look in 'categories' under spend_exclusion_policy 
     * For ICICI cards: look in accrual_exclusions array
   - If the category IS in exclusions: User can make the transaction but will NOT earn rewards/points
   - If the category is NOT in exclusions: User will earn the standard rewards/points

Be specific about amounts, thresholds, and conditions. Keep the answer helpful, clear, and concise.
Do not invent information. If the data is missing, say so.
"""
        elif intent == 'reward_comparison':
            system_prompt = """
You are a credit card expert specializing in reward comparisons. 
Help users understand which card gives better rewards for their spending.
Use the provided data to make accurate calculations and comparisons.
Show your work clearly with calculations.
"""
        elif intent == 'rewards':
            system_prompt = """
You are a credit card expert answering questions about reward rates and earning patterns.

CRITICAL RULES FOR REWARD RATES:
1. Answer ONLY based on the provided JSON data
2. ALWAYS prioritize specific category rates over general rates
3. When user asks about a specific spending category (hotels, travel, dining, etc.):
   - First check if there's a specific section for that category (e.g., "travel", "dining")
   - If the category appears in a specific section, use THAT rate
   - Only use "others" rate if no specific category rate exists
4. Be specific about caps, limits, and conditions
5. If there are multiple tiers or caps, explain them clearly

EXAMPLE HIERARCHY:
- If user asks about "hotel spends" and there's a "travel" section with "Direct Hotels" → use the travel rate
- If user asks about "dining" and there's a "dining" section → use the dining rate  
- Only use "others" rate for general spends or categories not specifically mentioned

Be helpful but strictly factual based only on the provided data.
"""
        elif intent == 'miles_transfer':
            system_prompt = """
You are a credit card expert answering questions about transfer partners and miles/points transfers.

CRITICAL RULES:
1. Answer ONLY based on the provided JSON data
2. If the JSON data does NOT contain transfer partner information for a card, you MUST say "I don't have transfer partner information for this card in my database"
3. Do NOT invent or assume any transfer partners (airlines, hotels, etc.)
4. Do NOT use your general knowledge about credit cards
5. Only mention transfer partners that are explicitly listed in the provided data
6. If no transfer partner data exists, clearly state this limitation

Be helpful but strictly factual based only on the provided data.
"""
        else:
            system_prompt = """
You are a friendly and knowledgeable credit card expert. Your goal is to provide clear, helpful, and concise answers with a touch of personality.

CRITICAL RULES:
1. Answer ONLY based on the provided JSON data
2. Do NOT invent or assume any information not present in the data
3. If the information is not in the provided data, clearly say "I don't have that information"
4. Do NOT use your general knowledge about credit cards to fill gaps
5. Keep your answers direct and to the point
6. Be helpful but strictly factual based only on the provided data
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
                temperature=0.1,
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
