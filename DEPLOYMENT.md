# 🚀 Deployment Instructions

## Local Setup

1. **Install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Set bot token:**
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token'
```

3. **Run the bot:**
```bash
python maps_to_waze_bot.py
```

## Google Cloud Run Deployment

1. **Install Google Cloud CLI**

2. **Login to account:**
```bash
gcloud auth login
```

3. **Set environment variables:**
```bash
gcloud run services update maps-to-waze-bot \
  --set-env-vars TELEGRAM_BOT_TOKEN=your_bot_token
```

4. **Deploy the application:**
```bash
gcloud run deploy maps-to-waze-bot --source .
```

## Getting Bot Token

1. Find @BotFather in Telegram
2. Send `/newbot`
3. Follow the instructions
4. Copy the received token

## Testing

The bot supports the following formats:
- ✅ Google Maps links with coordinates
- ✅ Direct coordinates (40.7128, -74.0060)
- ✅ DMS coordinates (31°44'49.8"N 35°01'46.6"E)
- ❌ Short place links without coordinates

## Port

The bot runs on port 8081 (as specified in project memory). 