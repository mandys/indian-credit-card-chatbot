import os
import re
import json
import random
import openai
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any

# Try to import Google's Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class RichDataCreditCardBot:
    """
    A chatbot engineered to understand a rich, nested JSON structure with common and card-specific terms.
    """
    def __init__(self, data_files: list[str]):
        load_dotenv()
        
        # Check for API keys in order of preference: Gemini -> OpenAI
        gemini_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if gemini_key and GEMINI_AVAILABLE:
            print("✨ Using Google Gemini API (Fast & India-friendly!)")
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.api_type = "gemini"
            self.model = "gemini-1.5-flash"
        elif openai_key:
            print("🤖 Using OpenAI API")
            self.client = openai.OpenAI(api_key=openai_key)
            self.api_type = "openai"
            self.model = "gpt-3.5-turbo"
        else:
            raise ValueError("No API key found! Please set GOOGLE_API_KEY or OPENAI_API_KEY in .env file")
        
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
            # Filter out internal metadata keys that start with _
            valid_keys = {key for key in card.keys() if not key.startswith('_')}
            all_keys.update(valid_keys)

        patterns = {key.replace('_', ' '): [key.replace('_', ' ')] for key in all_keys}
        
        # Add more specific, human-like patterns
        specific_patterns = {
            'fees': [r'fee', r'charge', r'cost', r'price'],
            'annual_fee_reversal_spend_threshold': [r'annual fee waiver', r'fee waiver', r'waiver.*spend', r'spend.*waiver', r'criteria.*waiver', r'waiver.*condition', r'annual fee.*waived', r'fee.*reversal'],
            'welcome_benefits': [r'welcome', r'joining bonus', r'sign-up'],
            'rewards': [r'reward', r'point', r'earn rate', r'cashback'],
            'reward_comparison': [r'which card.*more reward', r'which.*better reward', r'compare reward', r'more reward', r'better reward', r'which card.*spend.*reward', r'reward.*comparison'],
            'milestones': [r'milestone'],
            'tier_structure': [r'tier', r'status', 'level', r'gold tier', r'silver tier', r'platinum tier', r'gold.*benefit', r'silver.*benefit', r'platinum.*benefit'],
            'lounge_access': [r'lounge', r'airport'],
            'miles_transfer': [r'miles transfer', r'partner', r'conversion'],
            'insurance_spending': [r'insurance.*payment', r'insurance.*spend', r'pay.*insurance', r'points.*insurance.*payment', r'points.*insurance.*spend', r'reward.*insurance.*payment', r'reward.*insurance.*spend'],
            'insurance': [r'insurance.*benefit', r'insurance.*cover', r'insurance.*claim', r'travel.*insurance', r'accident.*insurance'],
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
            'gold': [r'gold', r'jewellery']
        }
        
        for intent, regex_list in specific_patterns.items():
            if intent in patterns:
                patterns[intent].extend(regex_list)
            else:
                patterns[intent] = regex_list
        
        self.intent_patterns = patterns
        self.spend_category_intents = ['travel', 'education', 'fuel', 'rent', 'wallet', 'utilities', 'insurance_spending', 'gaming', 'government', 'gold', 'jewellery']

    def detect_intent(self, query: str) -> Optional[str]:
        """Detect intent using regex pattern matching."""
        query_lower = query.lower()
        
        # Check for annual fee waiver queries first (most specific)
        if re.search(r'annual fee waiver', query_lower) or \
           re.search(r'fee waiver', query_lower) or \
           re.search(r'waiver.*spend', query_lower) or \
           re.search(r'spend.*waiver', query_lower) or \
           re.search(r'criteria.*waiver', query_lower) or \
           re.search(r'waiver.*condition', query_lower) or \
           re.search(r'annual fee.*waived', query_lower) or \
           re.search(r'fee.*reversal', query_lower) or \
           re.search(r'waiver.*annual', query_lower):
            return 'annual_fee_reversal_spend_threshold'
            
        # Check for lounge access queries (before reward comparison)
        if re.search(r'lounge.*access', query_lower) or \
           re.search(r'lounge.*better', query_lower) or \
           re.search(r'which.*card.*better.*lounge', query_lower) or \
           re.search(r'international.*lounge', query_lower) or \
           re.search(r'domestic.*lounge', query_lower) or \
           re.search(r'lounge.*visit', query_lower) or \
           re.search(r'airport.*lounge', query_lower):
            return 'lounge_access'
            
        # Check for miles transfer / redemption queries
        if re.search(r'transfer.*points', query_lower) or \
           re.search(r'transfer.*miles', query_lower) or \
           re.search(r'transfer.*airline', query_lower) or \
           re.search(r'points.*airline', query_lower) or \
           re.search(r'miles.*partner', query_lower) or \
           re.search(r'transfer.*partner', query_lower) or \
           re.search(r'redeem.*airline', query_lower) or \
           re.search(r'convert.*airline', query_lower) or \
           re.search(r'what.*do.*with.*\d+.*(points|miles)', query_lower) or \
           re.search(r'what.*can.*\d+.*(points|miles)', query_lower) or \
           re.search(r'use.*\d+.*(points|miles)', query_lower) or \
           re.search(r'redeem.*\d+.*(points|miles)', query_lower) or \
           re.search(r'\d+.*(points|miles).*redeem', query_lower) or \
           re.search(r'\d+.*(points|miles).*use', query_lower) or \
           re.search(r'\d+.*(points|miles).*worth', query_lower) or \
           re.search(r'value.*\d+.*(points|miles)', query_lower):
            return 'miles_transfer'
        
        # Check for reward calculation queries (broader patterns to catch more cases)
        if re.search(r'which.*card.*(more|better).*reward', query_lower) or \
           re.search(r'(compare|comparison).*reward', query_lower) or \
           re.search(r'spend.*\d+.*which.*card', query_lower) or \
           re.search(r'spend.*\d+.*(vs|versus)', query_lower) or \
           re.search(r'(icici|axis|atlas|emeralde).*(vs|versus).*(icici|axis|atlas|emeralde)', query_lower) or \
           re.search(r'which.*better.*spend.*\d+', query_lower) or \
           re.search(r'better.*reward.*\d+', query_lower) or \
           re.search(r'which.*card.*better', query_lower) or \
           re.search(r'\d+.*spend.*which.*card', query_lower) or \
           re.search(r'\d+.*(hotel|travel|airline|flight).*spend.*which.*card', query_lower) or \
           re.search(r'which.*card.*better.*(hotel|travel|airline|flight)', query_lower) or \
           re.search(r'which.*better.*\d+.*(hotel|travel|airline|flight)', query_lower) or \
           re.search(r'which.*better.*for.*\d+.*(hotel|travel|airline|flight)', query_lower) or \
           re.search(r'better.*for.*\d+.*(hotel|travel|airline|flight)', query_lower) or \
           re.search(r'which.*better.*for.*\d+', query_lower) or \
           re.search(r'reward.*points.*earned.*\d+.*spend', query_lower) or \
           re.search(r'points.*earned.*\d+.*spend', query_lower) or \
           re.search(r'miles.*earned.*\d+.*spend', query_lower) or \
           re.search(r'\d+.*spend.*(axis|atlas|icici|emeralde)', query_lower) or \
           re.search(r'(axis|atlas|icici|emeralde).*\d+.*spend', query_lower) or \
           re.search(r'\d+.*(hotel|travel|airline|flight).*using.*(axis|atlas|icici|emeralde)', query_lower):
            return 'reward_comparison'
        
        # Check for reward calculation queries first (must be before spending categories)
        if (re.search(r'how many.*points.*earn', query_lower) or 
            re.search(r'how many.*miles.*earn', query_lower) or
            re.search(r'points.*earn.*spend', query_lower) or
            re.search(r'miles.*earn.*spend', query_lower) or
            re.search(r'spend.*\d+.*points', query_lower) or
            re.search(r'spend.*\d+.*miles', query_lower) or
            re.search(r'\d+.*spend.*points', query_lower) or
            re.search(r'\d+.*spend.*miles', query_lower)):
            return 'reward_calculation'
        
        # Check for tier-specific queries first (most specific)
        if re.search(r'(gold|silver|platinum).*tier', query_lower) or \
           re.search(r'tier.*(gold|silver|platinum)', query_lower) or \
           re.search(r'(gold|silver|platinum).*benefit', query_lower) or \
           re.search(r'benefit.*(gold|silver|platinum)', query_lower):
            return 'tier_structure'
        
        # Check for specific spending categories (more specific than general fees)
        spending_category_checks = {
            'travel': [r'hotel', r'airline', r'flight', r'travel', r'booking', r'trip'],
            'utilities': [r'utilit(y|ies)', r'utility.*spend', r'utility.*charge', r'utility.*fee'],
            'fuel': [r'fuel', r'petrol', r'gas station'],
            'rent': [r'rent', r'rental'],
            'education': [r'education', r'school', r'college', r'university'],
            'insurance_spending': [r'insurance.*payment', r'insurance.*spend', r'pay.*insurance', r'points.*insurance.*payment', r'points.*insurance.*spend', r'reward.*insurance.*payment', r'reward.*insurance.*spend'],
            'insurance': [r'insurance.*benefit', r'insurance.*cover', r'insurance.*claim', r'travel.*insurance', r'accident.*insurance'],
            'government': [r'government', r'govt', r'tax payment'],
            'gaming': [r'gaming', r'game'],
            'wallet': [r'wallet', r'paytm', r'phonepe', r'gpay'],
            'gold': [r'gold.*jewellery', r'jewellery', r'jewelry', r'gold.*purchase', r'purchase.*gold', r'buy.*gold', r'buying.*gold']  # Gold/jewellery spending
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
        
        # Check for specific abbreviations first
        if 'epm' in query_lower:
            found_cards.add('ICICI Bank Emeralde Private Metal Credit Card')
        if 'atlas' in query_lower:
            found_cards.add('Axis Bank Atlas Credit Card')
            
        # Then check for standard keywords
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
        
        # First preprocess currency abbreviations
        processed_query = self.preprocess_currency_abbreviations(query)
        
        # Look for numbers in the query, including ones with commas
        numbers = re.findall(r'\d+(?:,\d+)*', processed_query)
        if numbers:
            # Remove commas and convert to int, take the largest number
            cleaned_numbers = [int(num.replace(',', '')) for num in numbers]
            return max(cleaned_numbers)
        return None

    def preprocess_currency_abbreviations(self, query: str) -> str:
        """Convert Indian currency abbreviations to full numbers."""
        import re
        
        # Define mappings for Indian currency abbreviations
        abbreviations = {
            r'(\d+(?:\.\d+)?)\s*(?:crore|crores|cr)\b': lambda m: str(int(float(m.group(1)) * 10000000)),  # crore
            r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)\b': lambda m: str(int(float(m.group(1)) * 100000)),       # lakh  
            r'(\d+(?:\.\d+)?)\s*(?:thousand|k)\b': lambda m: str(int(float(m.group(1)) * 1000)),           # thousand
        }
        
        result = query.lower()
        for pattern, replacement in abbreviations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result

    def calculate_rewards(self, card_name: str, spend_amount: int, category: str = None) -> Dict:
        """Calculate rewards for a specific card and spend amount, considering spending category."""
        if card_name not in self.cards_data:
            return {"error": f"Card {card_name} not found"}
        
        card_info = self.cards_data[card_name]
        
        # Handle ICICI Emeralde Private Metal
        if "ICICI" in card_name and "Emeralde" in card_name:
            # Check if the spending category is excluded from earning rewards
            rewards_info = card_info.get('rewards', {})
            excluded_categories = rewards_info.get('accrual_exclusions', [])
            
            # Create a mapping for categories to check against exclusions
            category_exclusion_map = {
                'government': ['government services', 'tax'],
                'tax': ['government services', 'tax'],
                'rent': ['rent'],
                'fuel': ['fuel payments'],
                'emi': ['EMI conversions']
                # Note: utilities are NOT excluded - they have capping instead
            }
            
            # Check if this category is excluded
            if category and category.lower() in category_exclusion_map:
                exclusion_keywords = category_exclusion_map[category.lower()]
                for exclusion in excluded_categories:
                    for keyword in exclusion_keywords:
                        if keyword.lower() in exclusion.lower():
                            return {
                                "card": card_name,
                                "spend_amount": spend_amount,
                                "points_earned": 0,
                                "rate": "No reward points earned (excluded category)",
                                "calculation": f"₹{spend_amount:,} - 0 points ({category} excluded from rewards)",
                                "category": category,
                                "excluded": True,
                                "exclusion_reason": exclusion
                            }
            
            # Check for capped categories (utility, grocery, education, insurance)
            capping_info = rewards_info.get('capping_per_statement_cycle', {})
            if category and category.lower() in ['utility', 'utilities', 'grocery', 'education', 'insurance']:
                # Map category names to capping keys
                cap_key_map = {
                    'utility': 'utility',
                    'utilities': 'utility',
                    'grocery': 'grocery', 
                    'education': 'education',
                    'insurance': 'insurance'
                }
                cap_key = cap_key_map.get(category.lower())
                
                if cap_key and cap_key in capping_info:
                    # Extract cap amount (e.g., "1,000 Reward Points" -> 1000)
                    cap_text = capping_info[cap_key]
                    import re
                    cap_match = re.search(r'(\d{1,3}(?:,\d{3})*)', cap_text)
                    if cap_match:
                        cap_points = int(cap_match.group(1).replace(',', ''))
                        
                        # Calculate points: 6 points per ₹200 spent
                        uncapped_points = (spend_amount // 200) * 6
                        capped_points = min(uncapped_points, cap_points)
                        
                        if uncapped_points > cap_points:
                            return {
                                "card": card_name,
                                "spend_amount": spend_amount,
                                "points_earned": capped_points,
                                "rate": f"6 points per ₹200 (capped at {cap_points:,} points per cycle)",
                                "calculation": f"₹{spend_amount:,} ÷ 200 × 6 = {uncapped_points} points, capped at {cap_points:,} points",
                                "category": category,
                                "cap_applied": True,
                                "cap_amount": cap_points
                            }
                        else:
                            return {
                                "card": card_name,
                                "spend_amount": spend_amount,
                                "points_earned": capped_points,
                                "rate": f"6 points per ₹200 (up to {cap_points:,} points per cycle)",
                                "calculation": f"₹{spend_amount:,} ÷ 200 × 6 = {capped_points} points",
                                "category": category,
                                "cap_applied": False,
                                "cap_amount": cap_points
                            }
            
            # If not excluded and not a capped category, calculate normal points: 6 points per ₹200 spent
            points = (spend_amount // 200) * 6
            return {
                "card": card_name,
                "spend_amount": spend_amount,
                "points_earned": points,
                "rate": "6 points per ₹200 (general rate)",
                "calculation": f"₹{spend_amount} ÷ 200 × 6 = {points} points",
                "category": category or "general"
            }
        
        # Handle Axis Atlas
        elif "Axis" in card_name and "Atlas" in card_name:
            rewards_info = card_info.get('rewards', {})
            
            # Check if the spending category is excluded from earning rewards
            excluded_categories = []
            spend_exclusion_policy = card_info.get('tier_structure', {}).get('spend_exclusion_policy', {})
            if 'categories' in spend_exclusion_policy:
                excluded_categories = [cat.lower() for cat in spend_exclusion_policy['categories']]
            
            # Map category to exclusion names
            category_exclusion_map = {
                'utility': 'utilities',
                'utilities': 'utilities',
                'fuel': 'fuel',
                'rent': 'rent',
                'wallet': 'wallet',
                'insurance': 'insurance',
                'government': 'government institution',
                'tax': 'government institution',  # Tax falls under government
                'telecom': 'telecom',
                'gold': 'gold/ jewellery',
                'jewellery': 'gold/ jewellery'
            }
            
            # Check if this category is excluded
            if category and category.lower() in category_exclusion_map:
                exclusion_name = category_exclusion_map[category.lower()]
                if exclusion_name in excluded_categories:
                    return {
                        "card": card_name,
                        "spend_amount": spend_amount,
                        "miles_earned": 0,
                        "rate": "No EDGE Miles earned (excluded category)",
                        "calculation": f"₹{spend_amount:,} - 0 miles ({category} excluded from rewards)",
                        "category": category,
                        "excluded": True
                    }
            
            # Check if this is a travel-related spend (hotels, airlines)
            if category and category.lower() in ['hotel', 'travel', 'airline', 'flight']:
                # Atlas: 5 EDGE Miles per ₹100 for travel (up to ₹2L monthly cap)
                # Check monthly cap
                monthly_cap = 200000  # ₹2L cap for travel category
                capped_spend = min(spend_amount, monthly_cap)
                excess_spend = max(0, spend_amount - monthly_cap)
                
                # Calculate miles for capped amount at 5x rate
                miles_5x = (capped_spend // 100) * 5
                # Calculate miles for excess at 2x rate
                miles_2x = (excess_spend // 100) * 2
                total_miles = miles_5x + miles_2x
                
                calculation_details = f"₹{capped_spend:,} ÷ 100 × 5 = {miles_5x} miles"
                if excess_spend > 0:
                    calculation_details += f" + ₹{excess_spend:,} ÷ 100 × 2 = {miles_2x} miles"
                calculation_details += f" = {total_miles} total miles"
                
                return {
                    "card": card_name,
                    "spend_amount": spend_amount,
                    "miles_earned": total_miles,
                    "rate": "5 EDGE Miles per ₹100 (travel category, up to ₹2L/month), then 2x",
                    "calculation": calculation_details,
                    "category": "travel",
                    "monthly_cap_applied": spend_amount > monthly_cap
                }
            else:
                # Atlas: 2 EDGE Miles per ₹100 for general spend (only if not excluded)
                miles = (spend_amount // 100) * 2
                return {
                    "card": card_name,
                    "spend_amount": spend_amount,
                    "miles_earned": miles,
                    "rate": "2 EDGE Miles per ₹100 (general rate)",
                    "calculation": f"₹{spend_amount:,} ÷ 100 × 2 = {miles} miles",
                    "category": category or "general"
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
        
        # Handle reward calculation queries
        if intent == 'reward_calculation':
            context = {}
            # If no specific cards mentioned, get all available cards
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
        
        # Handle general queries without specific cards - show all available cards' data
        if intent and not card_names:
            context = {}
            context['available_cards'] = list(self.cards_data.keys())
            
            # Check if the intent exists in any card's data
            found_data = False
            for name, card_info in self.cards_data.items():
                if intent in card_info:
                    if name not in context:
                        context[name] = {}
                    context[name][intent] = card_info[intent]
                    context[name]['name'] = name
                    found_data = True
            
            # Also check bank common terms
            for bank, bank_terms in self.bank_common_terms.items():
                if intent in bank_terms:
                    context['common_terms'] = {intent: bank_terms[intent]}
                    found_data = True
            
            if found_data:
                return context
        
        # If the intent is miles transfer or redemption, gather relevant data
        if intent in ['miles_transfer', 'redemption']:
            context = {}
            
            # If no specific cards mentioned, get all cards
            if not card_names:
                card_names = list(self.cards_data.keys())
                
            for name in card_names:
                if name in self.cards_data:
                    card_info = self.cards_data[name]
                    card_context = {'name': name}
                    
                    # Get miles transfer data if available
                    if 'miles_transfer' in card_info:
                        card_context['miles_transfer'] = card_info['miles_transfer']
                        
                    # Get redemption data if available
                    if 'redemption' in card_info:
                        card_context['redemption'] = card_info['redemption']
                        
                    # Get rewards data for context
                    if 'rewards' in card_info:
                        card_context['rewards'] = card_info['rewards']
                        
                    context[name] = card_context
            return context
            
        # If the intent is a surcharge fee category, gather comprehensive context including common terms
        if intent in ['utilities', 'rent', 'fuel', 'education', 'gaming', 'wallet', 'insurance_spending', 'government', 'gold']:
            context = {}
            
            # If no specific cards mentioned, get all cards
            if not card_names:
                card_names = list(self.cards_data.keys())
                
            for name in card_names:
                if name in self.cards_data:
                    card_info = self.cards_data[name]
                    card_context = {'name': name}
                    
                    # Get surcharge fees from common terms - match card to correct bank
                    if 'ICICI' in name:
                        bank_key = 'icici'
                    elif 'Axis' in name:
                        bank_key = 'axis'
                    else:
                        bank_key = None
                        
                    if bank_key and bank_key in self.bank_common_terms:
                        bank_terms = self.bank_common_terms[bank_key]
                        if 'surcharge_fees' in bank_terms and intent in bank_terms['surcharge_fees']:
                            card_context['surcharge_fees'] = {intent: bank_terms['surcharge_fees'][intent]}
                            
                    # Also get reward information if available for utilities etc.
                    if 'rewards' in card_info:
                        rewards = card_info['rewards']
                        
                        # Get exclusions from multiple possible sources
                        exclusions = []
                        if 'accrual_exclusions' in rewards:
                            exclusions = rewards['accrual_exclusions']
                        elif 'spend_exclusion_policy' in rewards and 'categories' in rewards['spend_exclusion_policy']:
                            exclusions = rewards['spend_exclusion_policy']['categories']
                        
                        card_context['rewards'] = {
                            'general_rate': rewards.get('rate_general'),
                            'others_rate': rewards.get('others'),
                            'value_per_point': rewards.get('value_per_point'),
                            'accrual_exclusions': exclusions,
                            'spend_exclusion_policy': rewards.get('spend_exclusion_policy', {}),
                            'capping_per_statement_cycle': rewards.get('capping_per_statement_cycle', {})
                        }
                        
                        # Add unified earning rate for easier AI processing
                        if rewards.get('rate_general'):
                            card_context['rewards']['earning_rate'] = rewards.get('rate_general')
                        elif rewards.get('others') and isinstance(rewards.get('others'), dict):
                            others_rate = rewards.get('others', {}).get('rate')
                            if others_rate:
                                card_context['rewards']['earning_rate'] = others_rate
                        
                    context[name] = card_context
            return context
        
        # Handle queries with specific cards (including lounge access comparisons)
        if card_names:
            context = {}
            for name in card_names:
                if name in self.cards_data:
                    card_info = self.cards_data[name]
                    if intent and intent in card_info:
                        if name not in context:
                            context[name] = {}
                        context[name][intent] = card_info[intent]
                        context[name]['name'] = name
                    elif not intent:
                        context[name] = card_info
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
                            # Map insurance_spending intent to insurance surcharge key
                            surcharge_key = 'insurance' if intent == 'insurance_spending' else intent
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
                        
                        # Include comprehensive reward information for spending categories
                        reward_info = {
                            'general_rate': rewards.get('rate_general'),
                            'others_rate': rewards.get('others'),
                            'value_per_point': rewards.get('value_per_point'),
                            'accrual_exclusions': exclusions,
                            'spend_exclusion_policy': rewards.get('spend_exclusion_policy', {}),
                            'capping_per_statement_cycle': rewards.get('capping_per_statement_cycle', {})
                        }
                        
                        # Include category-specific caps if they exist
                        if 'capping_per_statement_cycle' in rewards:
                            caps = rewards['capping_per_statement_cycle']
                            # Map insurance_spending intent to insurance cap key
                            cap_key = 'insurance' if intent == 'insurance_spending' else intent
                            if cap_key in caps:
                                reward_info['category_cap'] = caps[cap_key]
                            reward_info['all_caps'] = caps
                            
                        card_context['rewards_info'] = reward_info
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
        Generates an answer using the configured API (Gemini or OpenAI) based on the relevant data.
        """
        # Handle reward calculation queries with specific card rates
        if intent == 'reward_calculation':
            spend_amount = self.extract_spend_amount(query)
            
            # Detect spending category from the query
            spending_category = None
            query_lower = query.lower()
            category_keywords = {
                'hotel': ['hotel', 'hotels'],
                'travel': ['travel', 'trip', 'airline', 'flight', 'flights'],
                'dining': ['dining', 'restaurant', 'food'],
                'fuel': ['fuel', 'petrol', 'gas'],
                'utility': ['utility', 'utilities'],
                'rent': ['rent'],
                'education': ['education', 'school', 'college'],
                'insurance': ['insurance'],
                'government': ['government', 'govt', 'tax'],
                'gaming': ['gaming', 'games'],
                'wallet': ['wallet', 'paytm', 'phonepe', 'gpay'],
                'gold': ['gold', 'jewellery', 'jewelry']
            }
            
            for category, keywords in category_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    spending_category = category
                    break
            
            if spend_amount and relevant_data:
                calculations = []
                for card_name in relevant_data.keys():
                    calc_result = self.calculate_rewards(card_name, spend_amount, spending_category)
                    if 'error' not in calc_result:
                        calculations.append(calc_result)
                
                if calculations:
                    # Create a detailed response for single card
                    response_text = f"For spending ₹{spend_amount:,}:\n\n"
                    
                    for calc in calculations:
                        if 'points_earned' in calc:
                            response_text += f"**{calc['card']}**: {calc['points_earned']} points\n"
                            response_text += f"- Rate: {calc['rate']}\n"
                            response_text += f"- Calculation: {calc['calculation']}\n"
                        elif 'miles_earned' in calc:
                            response_text += f"**{calc['card']}**: {calc['miles_earned']} miles\n"
                            response_text += f"- Rate: {calc['rate']}\n"
                            response_text += f"- Calculation: {calc['calculation']}\n"
                    
                    return response_text
                else:
                    return "I couldn't calculate rewards for the specified card. Please make sure you're asking about a supported card."
            else:
                return "Please specify a spend amount to calculate rewards (e.g., 'How many points would I earn for spending ₹50,000?')"
        
        # Handle reward comparison queries with calculations
        if intent == 'reward_comparison':
            spend_amount = self.extract_spend_amount(query)
            
            # Detect spending category from the query
            spending_category = None
            query_lower = query.lower()
            category_keywords = {
                'hotel': ['hotel', 'hotels'],
                'travel': ['travel', 'trip', 'airline', 'flight', 'flights'],
                'dining': ['dining', 'restaurant', 'food'],
                'fuel': ['fuel', 'petrol', 'gas'],
                'utility': ['utility', 'utilities'],
                'rent': ['rent'],
                'education': ['education', 'school', 'college'],
                'insurance': ['insurance'],
                'government': ['government', 'govt', 'tax'],
                'gaming': ['gaming', 'games'],
                'wallet': ['wallet', 'paytm', 'phonepe', 'gpay'],
                'gold': ['gold', 'jewellery', 'jewelry']
            }
            
            for category, keywords in category_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    spending_category = category
                    break
            
            if spend_amount and relevant_data:
                calculations = []
                for card_name in relevant_data.keys():
                    calc_result = self.calculate_rewards(card_name, spend_amount, spending_category)
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
            elif not spend_amount and spending_category:
                # Handle queries without spend amount but with specific category (like airline bookings)
                if spending_category in ['travel', 'hotel'] and relevant_data:
                    comparison_text = f"For {spending_category} spending:\n\n"
                    
                    # Check Axis Atlas
                    if 'Axis Bank Atlas Credit Card' in relevant_data:
                        comparison_text += "**Axis Bank Atlas Credit Card**: 5 EDGE Miles per ₹100 spent (travel category, up to ₹2L monthly cap), then 2x for excess\n\n"
                    
                    # Check ICICI EPM
                    if 'ICICI Bank Emeralde Private Metal Credit Card' in relevant_data:
                        comparison_text += "**ICICI Bank Emeralde Private Metal Credit Card**: 6 points per ₹200 spent (general rate)\n\n"
                    
                    comparison_text += "**Winner**: Axis Atlas is better for travel/airline bookings due to the 5x rate for the travel category."
                    return comparison_text
                else:
                    return "Please specify a spend amount to compare rewards (e.g., 'If I spend ₹100,000 which card gives more rewards?')"
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

2. REWARDS ELIGIBILITY CHECK:
   FIRST, determine if the category earns rewards:
   - Look for the category name (e.g., "rent", "fuel", "government") in the exclusions list
   - For ICICI: check accrual_exclusions array (utilities are NOT excluded but have caps)
   - For Axis: check categories under spend_exclusion_policy (utilities ARE excluded)
   - If category IS FOUND in exclusions → NO REWARDS (stop here)
   - If category is NOT FOUND in exclusions → PROCEED to calculate rewards
   - For ICICI: utilities/grocery/education/insurance have capping_per_statement_cycle limits

3. REWARDS CALCULATION (only if category earns rewards):
   - Use general_rate (e.g., "6 points per ₹200") 
   - Calculate total points based on spend amount
   - Check for category_cap and apply it as the maximum limit
   - Mention value_per_point if available

4. CALCULATION LOGIC (only if rewards are earned):
   - Step 1: Calculate theoretical points (spend ÷ rate × points)
   - Step 2: Check if category_cap exists for this spending category
   - Step 3: If cap exists, the FINAL answer is the LOWER of calculated points OR cap
   - Step 4: Clearly state both the calculated amount and the capped amount

5. IMPORTANT: Be very clear about whether the category earns rewards or not. Don't contradict yourself.

Be specific about amounts, thresholds, and conditions. Include earning rates, caps, and point values.
Do not invent information. If the data is missing, say so.
"""
        elif intent == 'reward_comparison':
            system_prompt = """
You are a credit card expert specializing in reward comparisons. 
Help users understand which card gives better rewards for their spending.
Use the provided data to make accurate calculations and comparisons.
Show your work clearly with calculations.
"""
        elif intent == 'miles_transfer':
            system_prompt = """
You are a credit card expert answering questions about redemption options, transfer partners, and the value of points/miles.

CRITICAL RULES FOR REDEMPTION & MILES TRANSFER:
1. Answer ONLY based on the provided JSON data
2. If user asks "what can I do with X points/miles" - focus on REDEMPTION OPTIONS and VALUE
3. Check redemption section first for: platforms, options, value per point/mile
4. Check miles_transfer section for: transfer partners, conversion rates, limits
5. Do NOT calculate backwards how much spend is needed to earn the points - that's not what they're asking

REDEMPTION VALUE CALCULATION:
6. If redemption section shows "value": "₹1 = 1 EDGE Mile", then X miles = ₹X value
7. For ICICI: points may have different values for different redemptions (flight vouchers vs cashback)
8. Always mention the redemption value clearly

RESPONSE FORMAT FOR "WHAT CAN I DO WITH X POINTS/MILES":
9. State the redemption value: "5000 EDGE Miles = ₹5000 value"
10. List redemption options: Flights, Hotels, Experiences, etc.
11. List transfer partners if available
12. Mention platforms where redemption can be done
13. Include any important limitations or caps

TRANSFER PARTNERS FORMAT:
14. Group partners by categories (airlines, hotels, etc.)
15. Mention conversion rates and annual limits
16. For each partner group, list the specific partners available

Be helpful, specific, and focus on what they can actually DO with their existing points/miles.
"""
        elif intent in ['utilities', 'rent', 'fuel', 'education', 'gaming', 'wallet']:
            system_prompt = """
You are a credit card expert answering questions about surcharge fees and rewards for specific spending categories like utilities, rent, fuel, education, etc.

CRITICAL RULES FOR EXCLUSION CHECKING:
1. Answer ONLY based on the provided JSON data
2. To check if a category earns rewards, look at the "accrual_exclusions" list
3. A category earns rewards if it is NOT found in the "accrual_exclusions" list
4. If a category is NOT in "accrual_exclusions", it DOES earn rewards at the specified rate
5. Check "capping_per_statement_cycle" for any caps on specific categories

STEP-BY-STEP EXCLUSION CHECK:
6. For each card, examine the "accrual_exclusions" array carefully
7. Look for the exact category name (e.g., "education", "utilities", "rent") in that array
8. If the category is NOT found in the array, state "earns rewards"
9. If the category IS found in the array, state "NO rewards (excluded)"
10. For ICICI cards, check "capping_per_statement_cycle" for caps

REWARD RATE DETECTION:
11. Check for reward rates in this order:
    - "earning_rate" field (unified rate for both cards)
    - "general_rate" field (used by ICICI cards)
    - "others_rate" field (used by Axis cards) - look for "rate" inside this object
12. If "earning_rate" exists, use that - it's the unified rate field
13. If "general_rate" is null but "others_rate" exists, use the rate from "others_rate"
14. For Axis Atlas: "others_rate": {"rate": "2 EDGE Miles/₹100"} means 2 EDGE Miles per ₹100
15. NEVER say "no general rate provided" if earning_rate or others_rate exists

CONCRETE EXAMPLE FOR AXIS ATLAS:
If you see this data structure:
"earning_rate": "2 EDGE Miles/₹100",
"general_rate": null,
"others_rate": {
  "rate": "2 EDGE Miles/₹100",
  "effective_from": "2022-12-20"
}
Then the earning rate is: 2 EDGE Miles per ₹100 (from earning_rate field)

RESPONSE FORMAT:
16. For each card, clearly state: Fees + Reward Status + Rate (if applicable) + Caps (if applicable)
17. Use clear section headers for each card
18. Be explicit: "Education is NOT in exclusions, so it earns rewards" or "Education is in exclusions, so NO rewards"
19. Show the actual earning rate if rewards are earned
20. Mention any category caps from "capping_per_statement_cycle"

EXAMPLE LOGIC FOR EDUCATION:
21. Axis Atlas: Check if "education" appears in accrual_exclusions → If NOT found → Check "earning_rate" → Earns 2 EDGE Miles per ₹100
22. ICICI EPM: Check if "education" appears in accrual_exclusions → If NOT found → Check "general_rate" → Earns 6 points per ₹200, capped at 1000 points per cycle

COMPARISON HANDLING:
23. When comparing cards with different reward types (points vs miles), show both rates clearly
24. Don't try to convert between points and miles unless explicit conversion rates are provided
25. Focus on the earning rates, fees, and caps for each card
26. Let the user decide which is better based on their redemption preferences

Be precise, check the actual data carefully, and don't assume exclusions that aren't explicitly listed. Always check BOTH general_rate and others_rate fields.
"""
        elif intent == 'tier_structure':
            system_prompt = """
You are a credit card expert answering questions about tier structures and tier-specific benefits.

CRITICAL RULES FOR TIER QUERIES:
1. Answer ONLY based on the provided JSON data
2. Look for "tier_structure" section in the card data
3. If user asks about specific tier (Gold, Silver, Platinum), focus on that tier's benefits
4. Include spend thresholds, milestone rewards, lounge access, and any tier-specific benefits
5. Be specific about the differences between tiers
6. If comparing tiers, show a clear comparison

RESPONSE FORMAT:
7. Start with the requested tier's key benefits
8. Include spend threshold required to achieve that tier
9. List all benefits: milestone miles/points, annual bonus, lounge access
10. Compare with other tiers if relevant
11. Be clear about which benefits are tier-specific vs general card benefits

Be helpful and specific about tier requirements and benefits.
"""
        elif intent == 'lounge_access':
            system_prompt = """
You are a credit card expert answering questions about lounge access benefits.

CRITICAL RULES FOR LOUNGE ACCESS:
1. Answer ONLY based on the provided JSON data
2. Focus on the specific type of lounge access mentioned (domestic vs international)
3. Always mention guest policies and costs if available
4. For tier-based cards, explain the different tiers and their benefits
5. When comparing cards, provide a clear recommendation based on the user's needs

COMPARISON FORMAT:
7. Present information for each card clearly
8. Highlight key differences (unlimited vs limited, guest costs, etc.)
9. Provide a clear recommendation based on the query
10. If guest access is mentioned, prioritize that information

INTERNATIONAL LOUNGE ACCESS FOCUS:
11. For international lounge queries, focus on international benefits
12. Mention Priority Pass or similar programs if available
13. Always state guest charges if applicable
14. Compare value proposition for frequent travelers

Be helpful, specific, and provide actionable advice based only on the provided data.
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

CALCULATION RULES:
6. When user provides a spend amount, ALWAYS calculate the rewards:
   - Extract the rate (e.g., "5 EDGE Miles/₹100")
   - Calculate: (Spend Amount ÷ Rate Denominator) × Points per Unit
   - Example: ₹100,000 ÷ ₹100 × 5 = 1,000 × 5 = 5,000 EDGE Miles
   - DOUBLE-CHECK your math before providing the final answer
7. Show your calculation clearly for transparency

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

SPECIAL HANDLING FOR MULTIPLE CARDS:
7. If data for multiple cards is provided in the context, present information for ALL cards in a comparison format
8. If you see "available_cards" in the context, mention which cards are available in our portfolio
9. Format multi-card responses clearly with card names as headers
10. When user asks general questions without specifying a card, provide information for all relevant cards in our portfolio

EXAMPLE MULTI-CARD FORMAT:
**Axis Atlas Card:**
- [relevant information]

**ICICI Emeralde Private Metal Card:**
- [relevant information]
"""
        
        prompt = f"""
{system_prompt}

CONTEXT:
{context}
"""
        
        # Call the appropriate API
        try:
            if self.api_type == "gemini":
                response = self.gemini_model.generate_content(f"{prompt}\n\nUser Query: {query}")
                return response.text
            else:
                # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1,
                    max_tokens=350
                )
                return response.choices[0].message.content
                
        except Exception as e:
            # Fallback logic
            if self.api_type == "gemini" and os.getenv("OPENAI_API_KEY"):
                print(f"⚠️ Gemini failed ({e}), falling back to OpenAI...")
                try:
                    fallback_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    response = fallback_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": query}
                        ],
                        temperature=0.1,
                        max_tokens=350
                    )
                    return response.choices[0].message.content
                except Exception as fallback_error:
                    return f"I'm sorry, both Gemini and OpenAI encountered errors: {e} | {fallback_error}"

            else:
                return f"I'm sorry, I encountered an error: {e}"

    def detect_portfolio_query(self, query: str) -> bool:
        """Check if user is asking about available cards/portfolio."""
        portfolio_keywords = ['what cards', 'which cards', 'available cards', 'portfolio', 'cards do you have', 'cards available', 'what credit cards']
        return any(keyword in query.lower() for keyword in portfolio_keywords)

    def get_portfolio_info(self) -> str:
        """Return information about available cards in our portfolio."""
        cards_info = []
        for card_name in self.cards_data.keys():
            cards_info.append(f"• **{card_name}**")
        
        response = "Here are the credit cards in our portfolio:\n\n"
        response += "\n".join(cards_info)
        response += "\n\nYou can ask me questions about any of these cards, such as:\n"
        response += "- Joining and annual fees\n"
        response += "- Reward rates and benefits\n"
        response += "- Lounge access\n"
        response += "- Welcome benefits\n"
        response += "- Insurance coverage\n"
        response += "- And much more!"
        
        return response

    def get_answer(self, user_query: str) -> str:
        """Main method to process a query and return an answer."""
        if self.detect_greeting(user_query):
            return self.get_greeting()
        
        if self.detect_portfolio_query(user_query):
            return self.get_portfolio_info()

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
