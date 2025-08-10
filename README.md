# Maps to Waze Telegram Bot

A Telegram bot that converts Google Maps links and coordinates to Waze navigation links.

## Features

- ✅ Convert Google Maps links to Waze links
- ✅ Support for shortened Google Maps URLs (maps.app.goo.gl)
- ✅ Parse decimal coordinates (40.7128, -74.0060)
- ✅ Parse DMS coordinates (31°44'49.8"N 35°01'46.6"E)
- ✅ Automatic URL expansion for short links
- ✅ Multi-language support (English, Russian)
- ✅ Interactive buttons and menus
- ✅ User language preferences
- ✅ Admin commands and analytics
- ✅ Docker deployment ready
- ✅ Fast polling (1 second intervals)

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
- Docker (optional, for containerized development)
- Telegram bot token from [@BotFather](https://t.me/botfather)

### Installation

#### Option 1: Direct Python Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd maps-to-waze-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
cp env.example env.local
# Edit env.local with your bot token
```

5. Run the bot:
```bash
python main.py
```

#### Option 2: Docker Development
1. Clone and setup as above
2. Run with Docker:
```bash
./run_local_docker.sh
```

3. Stop Docker container:
```bash
./stop_local_docker.sh
```

## Production Deployment

### DigitalOcean Deployment
```bash
# Deploy to DigitalOcean server
./deploy.sh
```

### Manual Docker Deployment
```bash
# Build and run production container
docker-compose up -d --build
```

## Environment Variables

Create `.env` file or set environment variables:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_user_id_here
PORT=8081
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here  # Optional
ENVIRONMENT=production  # For production deployment
```

## Bot Commands

- `/start` - Show welcome message and main menu
- `/help` - Display help information
- `/menu` - Show main menu
- `/language` - Change bot language
- `/admin` - Admin panel (admin users only)
- `/myid` - Get your user ID

## Interactive Features

- **Language Selection**: Choose between English and Russian
- **Menu Navigation**: Interactive buttons for easy navigation
- **User Preferences**: Bot remembers your language choice
- **Admin Panel**: Analytics and management tools

## Architecture

- **maps_to_waze_bot.py** - Main bot logic with all handlers
- **main.py** - Entry point
- **translations.py** - Multi-language support
- **Dockerfile** - Container configuration
- **docker-compose.yml** - Production deployment
- **docker-compose.local.yml** - Local development
- **requirements.txt** - Python dependencies

## File Structure

```
maps-to-waze-bot/
├── maps_to_waze_bot.py      # Main bot logic
├── main.py                  # Entry point
├── translations.py          # Language translations
├── requirements.txt         # Dependencies
├── Dockerfile              # Container config
├── docker-compose.yml      # Production deployment
├── docker-compose.local.yml # Local development
├── deploy.sh               # Deployment script
├── run_local_docker.sh     # Local Docker runner
├── stop_local_docker.sh    # Docker cleanup
├── env.example             # Environment template
├── env.local               # Local environment (gitignored)
├── env-cloud.yaml          # Cloud environment (gitignored)
├── user_preferences.json   # User settings
└── waze_bot_icon.png       # Bot icon
```

## Performance Features

- **Fast Response**: 1-second polling intervals
- **Conflict Prevention**: Duplicate callback handling
- **Error Recovery**: Graceful error handling
- **Memory Efficient**: Cleanup of old callbacks
- **Production Ready**: HTTP server disabled in production

## Logging

The bot provides detailed logging including:
- User interactions and button clicks
- URL expansion processes
- Coordinate extraction and conversion
- Error handling and recovery
- Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (use Docker for consistency)
5. Submit a pull request

## License

MIT License - see LICENSE file for details.