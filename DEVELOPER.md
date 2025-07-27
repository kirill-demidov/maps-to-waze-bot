# 🛠️ Developer Documentation

Technical documentation for developers who want to deploy or contribute to the Maps to Waze Bot.

## 🔑 API Keys Setup

### Telegram Bot Token

1. **Find @BotFather in Telegram**
2. **Send command:** `/newbot`
3. **Follow instructions:**
   - Enter bot name
   - Enter bot username (must end with `bot`)
4. **Copy the received token**

### Google Maps API Key

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Select or create a project**
3. **Enable Places API:**
   - Go to "APIs & Services" → "Library"
   - Find "Places API"
   - Click "Enable"
4. **Create API key:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the created key
5. **Restrict the key (recommended):**
   - Click on the created key
   - In "Application restrictions" select "HTTP referrers"
   - Add domains: `*.run.app`
   - In "API restrictions" select "Restrict key"
   - Select "Places API"

## 🚀 Local Development

### Requirements
- Python 3.9+
- Telegram bot token
- Google Maps API key (optional)

### Installation
1. **Clone the repository:**
```bash
git clone <repository-url>
cd maps-to-waze-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables:**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
```

4. **Run the bot:**
```bash
python maps_to_waze_bot.py
```

## ☁️ Cloud Deployment

### Quick Deployment
```bash
gcloud run deploy maps-to-waze-bot \
  --source . \
  --port 8081 \
  --allow-unauthenticated \
  --region europe-central2 \
  --set-env-vars TELEGRAM_BOT_TOKEN="your_bot_token",GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
```

### Secure Deployment with Secret Manager
```bash
# Create secrets
echo -n "your_bot_token" | gcloud secrets create telegram-bot-token --data-file=-
echo -n "your_google_maps_api_key" | gcloud secrets create google-maps-api-key --data-file=-

# Deploy with secrets
gcloud run deploy maps-to-waze-bot \
  --source . \
  --port 8081 \
  --allow-unauthenticated \
  --region europe-central2 \
  --set-secrets TELEGRAM_BOT_TOKEN=telegram-bot-token:latest,GOOGLE_MAPS_API_KEY=google-maps-api-key:latest
```

## 🏗️ Architecture

- **maps_to_waze_bot.py** - Main bot logic with coordinate processing
- **Dockerfile** - Container configuration
- **requirements.txt** - Python dependencies

## 📊 Logging

The bot provides detailed logging:
- User interactions
- URL expansion processes
- Coordinate extraction
- Conversion results
- Error handling

## 🔒 Security

- Tokens stored in environment variables
- Recommended to use Google Secret Manager for production
- API keys restricted by domains and APIs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details. 