"""
AI-Powered Credit Card QA Engine
Replaces regex-based intent detection with intelligent AI processing.
"""

import os
import re
import json
import openai
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, Tuple

# Try to import Google's Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIPoweredCreditCardBot:
    """
    An AI-powered chatbot that uses LLM for both intent detection and response generation.
    Eliminates the need for complex regex patterns and manual intent mapping.
    """
    
    def __init__(self, data_files: list[str]):
        load_dotenv()
        
        # Initialize AI client (prefer Gemini for cost and speed)
        self._setup_ai_client()
        
        # Load card data
        self.cards_data = self._load_credit_card_data(data_files)
        
        # Load example queries for context
        self.example_queries = self._load_example_queries()
        
    def _setup_ai_client(self):
        """Setup AI client with preference for Gemini."""
        gemini_key = os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if gemini_key and GEMINI_AVAILABLE:
            print("✨ Using Google Gemini API for AI-powered intent detection")
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.api_type = "gemini"
            self.model = "gemini-1.5-flash"
        elif openai_key:
            print("🤖 Using OpenAI API for AI-powered intent detection")
            self.client = openai.OpenAI(api_key=openai_key)
            self.api_type = "openai"
            self.model = "gpt-3.5-turbo"
        else:
            raise ValueError("No API key found! Please set GOOGLE_API_KEY or OPENAI_API_KEY in .env file")
    
    def _load_credit_card_data(self, data_files: list[str]) -> Dict[str, Any]:
        """Load all credit card data from JSON files."""
        cards_data = {}
        
        for filepath in data_files:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                if "cards" in data and isinstance(data["cards"], list):
                    for card in data["cards"]:
                        card_name = card.get("name")
                        if card_name:
                            cards_data[card_name] = card
                            
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load {filepath}: {e}")
                
        return cards_data
    
    def _load_example_queries(self) -> Dict[str, List[str]]:
        """Load example queries for different intent types to provide context to AI."""
        return {
            "reward_calculation": [
                "If I spend ₹50,000 on dining, how many points will I earn?",
                "What points for ₹8L spend on ICICI EPM?",
                "How many miles do I get for ₹2L travel spend on Atlas?",
                "So if i spend 8L on ICICI EPM, what are the total points and milestone i receive? (ANSWER: Regular: ₹8,00,000÷₹200×6=24,000 points + Milestone: ₹6,000 EaseMyTrip vouchers = TOTAL: 24,000 points + ₹6,000 vouchers)"
            ],
            "welcome_benefits": [
                "What are the joining benefits of Atlas card?",
                "For paying joining fee for atlas card, how many miles i get? (ANSWER: Welcome benefits, NOT the fee amount)",
                "What do I get when I first get the ICICI EPM card?",
                "What are the renewal benefits of the atlas card?"
            ],
            "fees": [
                "What is the annual fee for both cards?",
                "How much does it cost to get the Atlas card?",
                "What are the charges for ICICI EPM?"
            ],
            "reward_comparison": [
                "Which card is better for ₹50k dining spend?",
                "Compare rewards between Atlas and ICICI for travel",
                "Which gives more points - Atlas or EPM for general spend?",
                "If I spend ₹100,000 on hotel bookings which card gives more rewards? (ANSWER: Atlas: ₹100,000÷₹100×5=5,000 miles vs ICICI: ₹100,000÷₹200×6=3,000 points)",
                "I have monthly spends of 1L, split as 20% Rent, 10% Utility, 20% Grocery, 10% Uber, 20% on Food and Eating Out, 20% on Buying Gift cards... which card is better? (ANSWER: Check exclusions first - Rent=0 on both, Utility=0 on Axis but earns on ICICI, etc.)"
            ],
            "lounge_access": [
                "How many lounge visits do I get?",
                "Compare lounge access between both cards",
                "Can I use international lounges with Atlas?"
            ],
            "exclusions": [
                "Do I get rewards on government payments?",
                "Are insurance payments excluded from earning points?",
                "What transactions don't earn miles on Atlas?"
            ]
        }
    
    def _create_comprehensive_system_prompt(self) -> str:
        """Create a comprehensive system prompt for AI processing."""
        
        # Get available data structure
        data_structure = self._get_data_structure_summary()
        
        # Create example context
        examples_text = ""
        for intent, queries in self.example_queries.items():
            examples_text += f"\n{intent.upper()} Examples:\n"
            for query in queries[:2]:  # Limit examples to keep prompt manageable
                examples_text += f"- {query}\n"
        
        system_prompt = f"""You are an expert credit card advisor specializing in Indian credit cards. 

AVAILABLE CREDIT CARDS DATA:
{json.dumps(data_structure, indent=2)}

YOUR TASK:
1. Understand the user's question completely
2. Identify which card(s) and data sections are relevant  
3. Provide accurate, helpful answers based ONLY on the provided data
4. Handle complex queries involving calculations, comparisons, and multiple concepts

IMPORTANT RULES:
- ALWAYS base answers on the provided card data
- For reward calculations, consider category-specific rates, caps, and exclusions
- For milestone queries, include BOTH regular earning AND milestone bonuses
- For comparison queries, analyze both cards and provide clear recommendations
- If data is missing, clearly state what information is not available
- Use Indian currency notation (₹, lakh, crore) naturally
- Be precise with numbers and calculations

CRITICAL: DISTINGUISH BETWEEN FEES AND BENEFITS:
- "joining fee" = cost to get the card (look in "fees" section)
- "joining benefits" = rewards you get when you join (look in "welcome_benefits" section)
- "For paying joining fee, how many miles/points?" = asking about WELCOME BENEFITS, NOT fees
- Always check if user is asking about cost vs rewards

CRITICAL: MILESTONE BENEFITS CALCULATION:
- Check "milestones" section in the provided data for accurate milestone information
- For ICICI EPM ₹8L spend example: Regular points + milestone vouchers (as per data)
- For Axis Atlas yearly spends: Regular miles + ALL applicable milestone miles (cumulative)
- MILESTONE LOGIC: Milestones are CUMULATIVE - you earn ALL milestones up to your spend level
- CRITICAL: For ₹7.5L spend on Atlas:
  * ✅ ₹3L milestone: 2500 miles (earned because 7.5L > 3L)
  * ✅ ₹7.5L milestone: 2500 miles (earned because 7.5L >= 7.5L) 
  * ❌ ₹15L milestone: NOT earned (because 7.5L < 15L)
  * TOTAL MILESTONE: 2500 + 2500 = 5000 miles
- CRITICAL: For ₹15L spend on Atlas:
  * ✅ ₹3L milestone: 2500 miles (earned because 15L > 3L)
  * ✅ ₹7.5L milestone: 2500 miles (earned because 15L > 7.5L)
  * ✅ ₹15L milestone: 5000 miles (earned because 15L >= 15L)
  * TOTAL MILESTONE: 2500 + 2500 + 5000 = 10000 miles
  * TOTAL EARNING: 30000 regular + 10000 milestone = 40000 miles
- ALWAYS calculate regular earning first, then ADD ALL applicable milestone benefits
- NEVER say "no milestone benefits" without checking the data

QUERY TYPES & EXAMPLES:
{examples_text}

CALCULATION GUIDELINES - CRITICAL FOR ACCURACY:
- Check earning rates for specific categories (travel, dining, etc.)
- Apply spending caps where mentioned
- For milestone queries, ALWAYS calculate BOTH:
  1. Regular reward points/miles earned from spending
  2. Milestone bonus benefits (vouchers, extra points, etc.)
- MANDATORY: NEVER give milestone benefits without regular earning calculation
- SPECIFICALLY for ICICI EPM ₹8L spend: 
  a) Regular: ₹8,00,000 ÷ ₹200 × 6 = 24,000 points
  b) Milestone: ₹6,000 EaseMyTrip vouchers
- Show detailed breakdowns: "Regular Points: X + Milestone Benefits: Y = Total Value"
- CRITICAL: User spent money, so they ALWAYS earn regular points PLUS any milestones

EXCLUSIONS - ABSOLUTELY CRITICAL:
- ALWAYS check "accrual_exclusions" and "spend_exclusion_policy" fields in the provided data
- IGNORE any assumptions - use ONLY the actual data provided
- If category is NOT listed in "accrual_exclusions", it DOES earn rewards
- Check "capping_per_statement_cycle" for caps on earning categories
- INSURANCE EXAMPLE: Check if "insurance" appears in accrual_exclusions list
  * If NOT in exclusions → Earns rewards (check for caps in capping_per_statement_cycle section)
  * If IN exclusions → No rewards earned
  * ICICI EPM: Insurance NOT in accrual_exclusions, so it DOES earn points with 5000 point cap
  * AXIS ATLAS: Insurance IS in accrual_exclusions, so it does NOT earn points

TRAVEL CATEGORY DETECTION - CRITICAL FOR HOTEL/AIRLINE QUERIES:
- ALWAYS check if "travel" section exists in the card data
- For HOTEL queries: Look for "Hotels", "Direct Hotels", or "hotel" in travel.categories
- For AIRLINE queries: Look for "Airlines", "Direct Airlines", or "airline" in travel.categories  
- If found in travel.categories → Use the travel.rate (e.g., "5 EDGE Miles/₹100")
- If NOT found in travel.categories → Use rate_general
- AXIS ATLAS EXAMPLE: "Direct Hotels" is in travel.categories, so hotels earn 5x rate, NOT general 2x rate
- NEVER default to general rate if travel section exists with relevant categories
- NEVER make assumptions - always verify against the actual JSON data provided

MATHEMATICAL ACCURACY - CRITICAL:
- ALWAYS show step-by-step calculation: Spend Amount ÷ Spend Unit × Points Rate = Total Points
- ALWAYS verify your arithmetic: 100,000 ÷ 100 = 1,000, then 1,000 × 5 = 5,000
- EXAMPLE: ₹100,000 ÷ ₹100 × 5 = 1,000 × 5 = 5,000 EDGE Miles (NOT 500!)
- EXAMPLE: ₹100,000 ÷ ₹200 × 6 = 500 × 6 = 3,000 Points (NOT 300!)
- Break down complex calculations: (Amount ÷ Unit) × Rate = (1,000) × 5 = 5,000
- Double-check all arithmetic before providing final answer
- Never provide results without showing the calculation steps
- If calculation seems wrong, recalculate step by step

UTILITY/CATEGORY PAYMENT DETAILS:
- For utility, fuel, rent, education, insurance payments, ALWAYS mention:
  1. Whether rewards are earned (check exclusions and accrual_exclusions)
  2. Any fees/charges (look in surcharge_fees, common_terms sections)
  3. Any caps/limits on rewards (look in capping, rate_cap sections)
  4. Specific thresholds (₹25,000, ₹50,000 limits mentioned in data)
- SPECIFICALLY check "surcharge_fees" field in common_terms for fee details
- SPECIFICALLY check "capping" sections in rewards for point limits
- Example: "Utility payments: 1% fee above ₹50k, earns rewards with 1000 point cap"

RESPONSE FORMAT:
- CONCISE, direct answers - don't explain your thinking process
- For simple questions, give simple answers (1-2 sentences)
- For complex questions, structure clearly but avoid unnecessary details
- Don't list all categories unless specifically asked
- Answer the specific question asked, not everything you know

EXAMPLES OF GOOD CONCISENESS:
- Q: "Is education excluded?" A: "No, education earns 2 EDGE Miles per ₹100 on Axis Atlas."
- Q: "Which card better for dining?" A: "Atlas: 2 miles/₹100, ICICI: 6 points/₹200. Atlas slightly better."
- Don't explain general rates unless relevant to the question

FOR MULTI-CATEGORY SPENDING QUERIES:
- Provide "Category-by-Category Breakdown" section
- Show each category: spending amount, exclusion status, rewards earned
- Format: "Rent: ₹20,000 - 0 rewards (excluded on both cards)"
- Format: "Utility: ₹10,000 - ICICI: 300 points, Atlas: 0 miles (excluded)"
- Provide total summary with strategic recommendations
- Suggest optimal spending allocation between cards
"""
        return system_prompt
    
    def _get_data_structure_summary(self) -> Dict[str, List[str]]:
        """Get a summary of available data structure for the AI prompt."""
        structure = {}
        for card_name, card_data in self.cards_data.items():
            # Get top-level keys (exclude internal metadata)
            keys = [key for key in card_data.keys() if not key.startswith('_')]
            structure[card_name] = keys
        return structure
    
    def process_query(self, user_query: str, conversation_history: List[Dict] = None) -> str:
        """
        Process user query using AI for both intent detection and response generation.
        Single API call replaces entire regex-based pipeline.
        """
        
        # Preprocess currency abbreviations (keep this useful preprocessing)
        processed_query = self._preprocess_currency(user_query)
        
        # Create comprehensive prompt with full context
        prompt = self._create_query_prompt(processed_query, conversation_history)
        
        # Get AI response
        try:
            if self.api_type == "gemini":
                response = self._get_gemini_response(prompt)
            else:
                response = self._get_openai_response(prompt)
                
            return response
            
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request right now. Please try again. Error: {str(e)}"
    
    def _create_query_prompt(self, user_query: str, conversation_history: List[Dict] = None) -> str:
        """Create the complete prompt with user query and relevant card data."""
        
        # Include conversation context if available
        context_text = ""
        if conversation_history:
            context_text = "\nCONVERSATION CONTEXT:\n"
            for exchange in conversation_history[-3:]:  # Last 3 exchanges
                context_text += f"User: {exchange.get('query', '')}\n"
                context_text += f"Assistant: {exchange.get('response', '')}\n"
        
        # Extract only relevant card data for better AI processing
        relevant_data = self._extract_relevant_data(user_query)
        
        prompt = f"""
USER QUESTION: {user_query}

{context_text}

RELEVANT CREDIT CARD DATA:
{json.dumps(relevant_data, indent=2)}

Please provide a comprehensive answer based on the credit card data above.
"""
        return prompt
    
    def _extract_relevant_data(self, user_query: str) -> Dict:
        """Extract only relevant data sections based on the query to improve AI accuracy."""
        query_lower = user_query.lower()
        relevant_data = {}
        
        # Determine which cards to include
        cards_to_include = []
        if 'axis' in query_lower or 'atlas' in query_lower:
            cards_to_include.append('Axis Bank Atlas Credit Card')
        if 'icici' in query_lower or 'emeralde' in query_lower or 'epm' in query_lower:
            cards_to_include.append('ICICI Bank Emeralde Private Metal Credit Card')
        
        # If no specific card mentioned, include both
        if not cards_to_include:
            cards_to_include = list(self.cards_data.keys())
        
        # Extract relevant sections based on query type
        for card_name in cards_to_include:
            if card_name not in self.cards_data:
                continue
                
            card_data = self.cards_data[card_name]
            relevant_card_data = {
                'name': card_name,
                'rewards': card_data.get('rewards', {}),
            }
            
            # Add specific sections based on query content
            if any(word in query_lower for word in ['fee', 'cost', 'charge', 'annual', 'joining']):
                relevant_card_data['fees'] = card_data.get('fees', {})
            
            if any(word in query_lower for word in ['welcome', 'joining', 'benefit', 'bonus']):
                relevant_card_data['welcome_benefits'] = card_data.get('welcome_benefits', {})
            
            if any(word in query_lower for word in ['milestone', 'tier', 'spend', 'yearly', 'annual']):
                relevant_card_data['milestones'] = card_data.get('milestones', [])
                relevant_card_data['tier_structure'] = card_data.get('tier_structure', {})
            
            if any(word in query_lower for word in ['lounge', 'airport']):
                relevant_card_data['lounge_access'] = card_data.get('lounge_access', {})
            
            if any(word in query_lower for word in ['transfer', 'partner', 'airline', 'redeem']):
                relevant_card_data['miles_transfer'] = card_data.get('miles_transfer', {})
                relevant_card_data['redemption'] = card_data.get('redemption', {})
            
            relevant_data[card_name] = relevant_card_data
        
        return relevant_data
    
    def _get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini API."""
        system_prompt = self._create_comprehensive_system_prompt()
        full_prompt = system_prompt + "\n\n" + prompt
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2000,
            )
        )
        
        return response.text
    
    def _get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI API."""
        system_prompt = self._create_comprehensive_system_prompt()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def _preprocess_currency(self, query: str) -> str:
        """Preprocess Indian currency abbreviations (keep this useful feature)."""
        # Convert Indian currency notation
        query = re.sub(r'(\d+)\s*[Ll](?!\w)', r'\1 lakh', query)  # 3L -> 3 lakh
        query = re.sub(r'(\d+)\s*[Cc][Rr](?!\w)', r'\1 crore', query)  # 2Cr -> 2 crore
        query = re.sub(r'(\d+)\s*[Kk](?!\w)', r'\1 thousand', query)  # 50k -> 50 thousand
        
        # Convert spelled out numbers to actual values in context
        query = re.sub(r'(\d+)\s*lakh', lambda m: f'₹{int(m.group(1)) * 100000}', query)
        query = re.sub(r'(\d+)\s*crore', lambda m: f'₹{int(m.group(1)) * 10000000}', query)
        query = re.sub(r'(\d+)\s*thousand', lambda m: f'₹{int(m.group(1)) * 1000}', query)
        
        return query
    
    def get_analytics_data(self, user_query: str, response: str, processing_time: float) -> Dict:
        """Generate analytics data for the query (for compatibility with existing analytics)."""
        return {
            "query": user_query,
            "response_preview": response[:100] + "..." if len(response) > 100 else response,
            "processing_approach": "ai_powered",
            "total_processing_time": processing_time,
            "api_used": self.api_type,
            "model_used": self.model,
            "query_complexity": {
                "word_count": len(user_query.split()),
                "has_currency": bool(re.search(r'₹|\d+[Ll]|\d+[Kk]|\d+\s*crore', user_query)),
                "has_comparison": bool(re.search(r'compare|better|vs|versus', user_query.lower())),
                "has_calculation": bool(re.search(r'spend|earn|points|miles|\d+', user_query.lower()))
            }
        }


def create_ai_powered_bot(data_files: list[str]) -> AIPoweredCreditCardBot:
    """Factory function to create AI-powered bot instance."""
    return AIPoweredCreditCardBot(data_files)


# Example usage and testing
if __name__ == "__main__":
    # Test the AI-powered approach
    bot = create_ai_powered_bot([
        "data/axis-atlas.json",
        "data/icici-epm.json"
    ])
    
    # Test problematic queries from user feedback
    test_queries = [
        "So if i spend 8L on ICICI EPM, what are the total points and milestone i receive?",
        "For paying joining fee for atlas card, how many miles i get?",
        "Which card is better for ₹50k dining spend?",
        "What are the renewal benefits of the atlas card?"
    ]
    
    print("Testing AI-Powered QA Engine:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = bot.process_query(query)
        print(f"Response: {response}")
        print("-" * 30)