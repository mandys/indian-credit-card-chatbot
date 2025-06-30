# 🔥 DeepSeek API Setup Guide

## Why DeepSeek?
- **95% cheaper** than OpenAI (₹0.14 vs ₹2.00 per 1M tokens)
- **Same performance** as GPT-3.5, often better
- **Same API format** - easy to switch
- **Great for Indian context** - understands currencies, terms

## ✅ Current Status
Your bot is configured to:
1. ✅ **Try DeepSeek first** (if credits available)
2. ✅ **Fallback to OpenAI** (if DeepSeek fails)
3. ✅ **Show clear messages** about which API is being used

## 🚀 Getting DeepSeek Credits

### Step 1: Sign up
1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Sign up with email or GitHub
3. Verify your account

### Step 2: Add credits
1. Go to "Billing" section
2. Add $5-10 (will last months with your usage)
3. Payment via card or other methods

### Step 3: Get API key
1. Go to "API Keys" 
2. Create new key
3. Copy the key (starts with `sk-`)

### Step 4: Update your .env file
```bash
# Replace your existing key with the new one
DEEPSEEK_API_KEY="sk-your-new-key-here"
```

## 🧪 Testing
```bash
# Test the integration
python -c "
from utils.qa_engine import RichDataCreditCardBot
bot = RichDataCreditCardBot(data_files=['data/axis-atlas.json', 'data/icici-epm.json'])
print(bot.get_answer('What are the joining fees?'))
"
```

## 💰 Cost Comparison
Based on your current usage:

| API | Cost per 1K queries* | Monthly cost** |
|-----|---------------------|----------------|
| OpenAI GPT-3.5 | ~$2.00 | ~$60 |
| DeepSeek | ~$0.10 | ~$3 | 
| **Savings** | **95%** | **$57/month** |

*Estimated based on average query length
**Assuming 1K queries per month

## 🔧 Troubleshooting

### "Insufficient Balance" Error
- Your DeepSeek account is out of credits
- Add credits at platform.deepseek.com
- Bot will automatically use OpenAI as fallback

### "Invalid API Key" Error
- Check your .env file has correct key
- Make sure no extra spaces or quotes
- Key should start with `sk-`

### "Rate Limited" Error
- DeepSeek has generous rate limits
- Wait a few seconds and try again
- Consider upgrading DeepSeek plan if needed

## 🎯 Alternative: Local Models (Free)

If you want zero ongoing costs:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a good model for credit cards
ollama pull qwen2:7b

# Test it
ollama run qwen2:7b "What are credit card rewards?"
```

## 🤝 Next Steps

1. **Immediate**: Add $5-10 credits to DeepSeek
2. **This week**: Monitor cost savings in dashboard
3. **Next month**: Consider local models for development
4. **Future**: Hybrid approach (local + cloud)

## 📊 Monitoring Usage

Your test runner will show which API is being used:
- 🔥 = DeepSeek (saving money!)
- 🤖 = OpenAI (fallback)
- ⚠️ = Fallback occurred

Track your savings and adjust accordingly! 