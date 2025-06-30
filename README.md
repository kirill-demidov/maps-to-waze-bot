# Maps to Waze Telegram Bot

A Telegram bot that converts Google Maps links and coordinates to Waze navigation links.

## Features

- ✅ Convert Google Maps links to Waze links
- ✅ Support for shortened Google Maps URLs (maps.app.goo.gl)
- ✅ Parse decimal coordinates (40.7128, -74.0060)
- ✅ Parse DMS coordinates (31°44'49.8"N 35°01'46.6"E)
- ✅ Automatic URL expansion for short links
- ✅ Detailed logging
- ✅ Cloud deployment ready

## Supported Input Formats

### Google Maps URLs
- `https://maps.google.com/...`
- `https://www.google.com/maps/...`
- `https://goo.gl/maps/...`
- `https://maps.app.goo.gl/...`

### Coordinates
- **Decimal**: `40.7128, -74.0060`
- **DMS**: `31°44'49.8"N 35°01'46.6"E`

## Local Development

### Prerequisites
- Python 3.9+
- Telegram bot token from [@BotFather](https://t.me/botfather)

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd maps-to-waze-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

4. Run the bot:
```bash
python main.py
```

## Cloud Deployment (Google Cloud Run)

### Build and Deploy
```bash
# Build Docker image
docker build --platform linux/amd64 -t gcr.io/YOUR_PROJECT/maps-to-waze-bot .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT/maps-to-waze-bot

# Deploy to Cloud Run
gcloud run deploy maps-to-waze-bot \
  --image gcr.io/YOUR_PROJECT/maps-to-waze-bot \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN="your_bot_token_here" \
  --allow-unauthenticated
```

## Bot Commands

- `/start` - Show welcome message and usage instructions
- `/help` - Display help information

## Architecture

- **bot_simple.py** - Main bot logic with coordinate parsing
- **main.py** - Entry point
- **Dockerfile** - Container configuration
- **requirements.txt** - Python dependencies

## Logging

The bot provides detailed logging including:
- User interactions
- URL expansion processes
- Coordinate extraction
- Conversion results
- Error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.