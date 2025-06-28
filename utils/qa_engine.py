import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_card_data():
    """Loads all credit card data from the data/ directory."""
    card_data = {}
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                card_name = data.get("card_name")
                if card_name:
                    card_data[card_name] = data
    return card_data

def get_answer(question: str, card_data: dict):
    """
    Answers a user's question by identifying the card, finding the relevant data,
    and generating a human-readable response.
    """
    if not openai.api_key or openai.api_key == "your-api-key-here":
        return "Error: OPENAI_API_KEY is not set. Please set it in your .env file."

    card_names = list(card_data.keys())
    if not card_names:
        return "Error: No card data found."

    # Get sample top-level keys to guide the model, assuming all JSONs have a similar structure.
    sample_card_keys = list(card_data[card_names[0]].keys())

    # Step 1: Identify the card and intent using GPT
    prompt1 = f"""
    Given the user question: "{question}"
    And the available credit cards: {card_names}

    Your task is to identify the user's intent.
    1.  "card_name": Find the credit card the user is asking about.
    2.  "intent": Match the user's query to ONE of the following JSON keys: {sample_card_keys}

    Respond with a JSON object containing "card_name" and "intent".
    Example: {{"card_name": "Axis Bank Atlas Credit Card", "intent": "annual_fee"}}
    If the card is not found or the intent is unclear, respond with {{"card_name": "N/A", "intent": "N/A"}}.
    """
    
    print("\n--- DEBUG INFO ---")
    print("--- PROMPT 1 (Intent Extraction) ---")
    print(prompt1)
    print("------------------------------------\n")

    try:
        response1 = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt1}],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        raw_response1 = response1.choices[0].message.content
        print("--- RESPONSE 1 (Raw JSON from Model) ---")
        print(raw_response1)
        print("----------------------------------------\n")

        intent_json = json.loads(raw_response1)
        card_name = intent_json.get("card_name")
        intent = intent_json.get("intent")
        
        print(f"--- PARSED INTENT ---")
        print(f"Card: {card_name}, Intent: {intent}")
        print(f"---------------------\n")


        if card_name == "N/A" or card_name not in card_data:
            return "I couldn't determine which card you're asking about. Please specify a card from the available list."

        if intent == "N/A" or intent not in sample_card_keys:
            return f"I understand you're asking about the {card_name}, but I'm not sure what specific information you need. Please clarify your question."

        # Step 2: Extract the relevant data
        data_for_card = card_data.get(card_name, {})
        relevant_data = data_for_card.get(intent)

        if relevant_data is None:
            return f"I couldn't find information about '{intent}' for the {card_name}."

        # Step 3: Generate a human-readable answer
        prompt2 = f"""
        You are a helpful assistant for Indian credit cards.
        The user asked: "{question}"
        The specific data from the card's terms and conditions is:
        {json.dumps({intent: relevant_data}, indent=2)}

        Based on this data, provide a clear, human-readable answer to the user's question.
        Do not just repeat the JSON. Explain it like an expert.
        Start your answer by mentioning the card's name.
        """

        print("--- PROMPT 2 (Answer Generation) ---")
        print(prompt2)
        print("------------------------------------\n")

        response2 = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt2}],
            temperature=0.5
        )
        
        final_answer = response2.choices[0].message.content
        print("--- RESPONSE 2 (Final Answer) ---")
        print(final_answer)
        print("---------------------------------\n")

        return final_answer

    except openai.OpenAIError as e:
        return f"An error occurred with the OpenAI API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    # For testing purposes
    cards = get_card_data()
    print("Loaded cards:", list(cards.keys()))
    
    # Test case 1
    test_question_1 = "What is the annual fee for the Axis Bank Atlas Credit Card?"
    print(f"\nQ: {test_question_1}")
    print("A:", get_answer(test_question_1, cards))

    # Test case 2
    test_question_2 = "Tell me about the lounge access on the ICICI Bank Emeralde Private Metal Credit Card"
    print(f"\nQ: {test_question_2}")
    print("A:", get_answer(test_question_2, cards))

    # Test case 3 - for the user's issue
    test_question_3 = "Which MCCs are excluded from reward points on the ICICI card?"
    print(f"\nQ: {test_question_3}")
    print("A:", get_answer(test_question_3, cards))
