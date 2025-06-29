#  Indian Credit Card Q&A Chatbot 🇮🇳💳

A simple, fast, and conversational AI chatbot to answer your questions about the complex terms and conditions of popular Indian credit cards.

This tool uses advanced AI to understand your questions and provide clear, human-readable answers based on structured data extracted from official bank documents. No more digging through dense PDFs!

## ✨ Features

- **Conversational Interface**: A friendly, chat-based UI that feels natural to use.
- **Fast & Accurate**: Get instant answers to your questions.
- **Key Information**: Ask about annual fees, welcome bonuses, reward structures, lounge access, and more.
- **Easily Extensible**: Add new credit cards just by dropping in a new JSON file.

## 🃏 Supported Cards

This chatbot is designed to work with any card defined in a structured JSON format. The initial set includes:

- **Axis Bank Atlas Credit Card**
- **ICICI Bank Emeralde Private Metal Credit Card (EPM)**

It can easily be extended to support other popular cards like the *Axis Magnus*, *HDFC Infinia*, *HDFC DCB*, and more.

## 🚀 Sample Questions

You can ask things like:
- *"What's the joining fee for the ICICI Emeralde card?"*
- *"Tell me about the milestone benefits on the Axis Atlas card."*
- *"Which MCCs are excluded from rewards on the ICICI card?"*
- *"How many lounge visits do I get with Axis Atlas?"*

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** for the user interface
- **OpenAI GPT-3.5-Turbo** for natural language understanding and generation

---

## ⚙️ Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/cc-features-chatbot.git
    cd cc-features-chatbot
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
   pip install -r requirements.txt
    ```

4.  **Add your OpenAI API Key:**
    Create a `.env` file in the root directory and add your key:
    ```
    OPENAI_API_KEY="your-api-key-here"
    ```

5.  **Run the application:**
    ```bash
   streamlit run app.py
    ```

## ➕ How to Add New Cards

1.  Create a new JSON file in the `/data` directory, using `axis-atlas.json` as a template.
2.  Fill in the details for the new card.
3.  Relaunch the app. The new card will be available automatically!

---

## Disclaimer

This tool is for informational and educational purposes only. While it strives for accuracy, always refer to the latest official documentation from the issuing bank for final terms and conditions.
