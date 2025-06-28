Here is the content as plain text for your technical reference (no Markdown formatting):

---

# Indian Credit Card Terms Q\&A Tool

This is a Streamlit-based natural language search tool that allows users to query structured credit card information extracted from bank-issued Terms and Conditions PDFs (e.g., joining fees, reward structure, lounge access, MCC exclusions, etc.).

---

## Project Overview

In India, each bank issues credit cards with detailed features like:

* Annual fees and waiver rules
* Welcome bonuses and sourcing conditions
* Reward point structures (category-wise rates, caps, exclusions)
* Tier upgrade benefits and thresholds
* Lounge access limits
* Miles transfer partners and caps

These are typically buried in dense PDF documents.

**This tool:**

* Extracts structured JSON from each card's PDF using external tools (NotebookLM or manual).
* Stores one JSON file per credit card.
* Lets users ask natural questions like:

  * “What’s the joining fee for ICICI EPM?”
  * “Does Axis Atlas give international lounge access?”
  * “What are the milestone benefits of HDFC Infinia?”
* Uses OpenAI GPT models to interpret questions and generate human-readable answers from structured data.

---

## Project Structure

.
├── app.py                  # Main Streamlit app
├── data/
│   ├── axis\_atlas.json
│   └── icici\_epm.json      # Card-wise structured JSONs
├── utils/
│   └── qa\_engine.py        # Logic for card selection, intent extraction, answering
├── requirements.txt
└── technical.txt

---

## JSON Format

Each credit card is stored as a JSON file like:

{
"card\_name": "Axis Bank Atlas",
"annual\_fee": { "amount": 5000, "currency": "INR", "notes": "Waived on 5L spend" },
"welcome\_benefit": {
"rules": \[ { "sourcing\_period": "first 30 days", "miles": 5000, "condition": "on first txn" } ],
"credit\_time": "within 60 days",
"encashable": false
},
...
}

As new cards are added, just drop their JSONs into the `/data/` folder. No code changes required.

---

## How It Works

1. User types a question
2. Backend:

   * Uses OpenAI GPT to classify intent & card name
   * Matches the corresponding card JSON
   * Extracts the relevant field from the JSON
   * Formats the response in clear English
3. Displays result in Streamlit interface

---

## Sample Queries to Try

* What is the annual fee for Axis Atlas?
* Does ICICI EPM give a welcome bonus?
* How many free lounge visits are available for silver tier holders?
* Which MCCs are excluded from reward points?

---

## Tech Stack

* OpenAI GPT-4o (via API)
* Python 3.10+
* Streamlit
* Flat JSON files for card data

---

## Setup Instructions

1. Clone the repo:

   git clone [https://github.com/your-username/card-qa-app.git](https://github.com/your-username/card-qa-app.git)
   cd card-qa-app

2. Install dependencies:

   pip install -r requirements.txt

3. Add your OpenAI Key:

   Create a `.env` file:
   OPENAI\_API\_KEY=your-api-key-here

   Or set as environment variable:
   export OPENAI\_API\_KEY=your-api-key-here

4. Run the app:

   streamlit run app.py

---

## Adding New Cards

To add more cards:

* Extract the relevant fields from the PDF
* Use the provided JSON schema (`axis_atlas.json` as a template)
* Save it under the `/data/` directory

No code changes needed.

---

## Future Enhancements

* PDF parsing pipeline using LangChain or Amazon Textract
* Add filtering/comparison UI (e.g., compare Axis Atlas vs HDFC Infinia)
* Export results (CSV or PDF)
* Browser extension to overlay summary on official bank pages

---

## License

MIT License. For educational and non-commercial use only. Always refer to the latest official credit card documentation for final terms.

---

Let me know if you want the starter code (`app.py` and `qa_engine.py`) now.
