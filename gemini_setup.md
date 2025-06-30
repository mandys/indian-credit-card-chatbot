# Google Gemini API Setup Guide

Google Gemini is an excellent alternative to OpenAI and DeepSeek for our credit card chatbot. It's fast, cost-effective, and **works great in India** with easy payment options.

## Why Google Gemini?

### 🌟 **Advantages for Indian Users**
- ✅ **India-friendly**: Full support for Indian users and payment methods
- ✅ **Cost-effective**: Much cheaper than OpenAI GPT-4/GPT-3.5
- ✅ **Fast responses**: Quick inference times
- ✅ **Easy setup**: Simple Google account-based registration
- ✅ **Good quality**: High-quality responses for our use case
- ✅ **Generous free tier**: 15 requests per minute free tier

### 💰 **Pricing Comparison**
| Provider | Model | Price per 1M input tokens | Price per 1M output tokens |
|----------|-------|---------------------------|----------------------------|
| **Google Gemini** | gemini-1.5-flash | **$0.075** | **$0.30** |
| OpenAI | gpt-3.5-turbo | $0.50 | $1.50 |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 |

**Gemini is ~85% cheaper than GPT-3.5-turbo!** 🎉

## Step-by-Step Setup

### 1. Get Your Google API Key

1. **Go to Google AI Studio**
   - Visit: https://aistudio.google.com/
   - Sign in with your Google account

2. **Create API Key**
   - Click on "Get API key" in the left sidebar
   - Click "Create API key"
   - Choose "Create API key in new project" (recommended)
   - Copy your API key (it starts with `AIza...`)

3. **Enable Billing (for production use)**
   - Go to: https://console.cloud.google.com/
   - Select your project
   - Navigate to "Billing" 
   - Add your payment method (supports Indian cards/UPI)

### 2. Install Required Package

```bash
pip install google-generativeai
```

### 3. Configure Your Environment

Add your API key to your `.env` file:

```bash
# Add this line to your .env file
GOOGLE_API_KEY=AIza_your_actual_api_key_here
```

### 4. Test Your Setup

Create a test file `test_gemini.py`:

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Test query
response = model.generate_content("What are the benefits of credit cards?")
print("✅ Gemini is working!")
print(f"Response: {response.text}")
```

Run the test:
```bash
python test_gemini.py
```

## Usage in Our Chatbot

The chatbot automatically detects available API keys in this priority order:
1. **Google Gemini** (if `GOOGLE_API_KEY` is set)
2. DeepSeek (if `DEEPSEEK_API_KEY` is set)  
3. OpenAI (if `OPENAI_API_KEY` is set)

### API Key Priority
```bash
# .env file example - Gemini will be used first
GOOGLE_API_KEY=AIza_your_gemini_key
DEEPSEEK_API_KEY=sk-your_deepseek_key  # Fallback
OPENAI_API_KEY=sk-your_openai_key      # Final fallback
```

## Free Tier Limits

### Google Gemini Free Tier
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per day**

This is perfect for development and testing!

## Production Considerations

### For Heavy Usage
1. **Enable billing** for higher rate limits
2. **Paid tier limits**: 1,000 requests per minute
3. **Cost monitoring**: Set up billing alerts in Google Cloud Console

### Monitoring Usage
- Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
- Monitor your API quota and usage

## Troubleshooting

### Common Issues

1. **"API key not valid"**
   - Verify your API key is correct
   - Make sure you copied the full key (starts with `AIza`)

2. **"Quota exceeded"**
   - You've hit the free tier limit
   - Wait for quota reset or enable billing

3. **"Permission denied"**
   - Enable the Generative Language API in Google Cloud Console
   - Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/

4. **Import error for google.generativeai**
   ```bash
   pip install --upgrade google-generativeai
   ```

### Getting Help
- Google AI documentation: https://ai.google.dev/docs
- Google Cloud support: https://cloud.google.com/support

## Comparison with Other Providers

| Feature | Google Gemini | DeepSeek | OpenAI |
|---------|---------------|----------|---------|
| **India Support** | ✅ Excellent | ❌ Limited payment | ✅ Good |
| **Cost** | ✅ Very cheap | ✅ Cheapest | ❌ Expensive |
| **Quality** | ✅ High | ✅ Good | ✅ High |
| **Speed** | ✅ Fast | ✅ Fast | ⚠️ Moderate |
| **Free Tier** | ✅ Generous | ⚠️ Limited | ⚠️ Small |
| **Setup Ease** | ✅ Simple | ⚠️ Moderate | ✅ Simple |

## Recommendations

### For Indian Users:
1. **Primary**: Google Gemini (best overall for India)
2. **Fallback**: OpenAI (if Gemini fails)
3. **Skip**: DeepSeek (payment issues in India)

### For Development:
- Start with Gemini free tier
- Monitor usage and upgrade when needed
- Keep OpenAI as fallback for reliability

---

**🚀 Ready to use Google Gemini!** Your chatbot will automatically use Gemini if the API key is configured, providing fast and cost-effective responses for your credit card queries. 