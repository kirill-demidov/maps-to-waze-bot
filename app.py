import os
import re
import logging
import threading
from urllib.parse import parse_qs, urlparse
from flask import Flask, render_template_string, send_from_directory, jsonify, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Coordinate conversion functions
def dms_to_decimal(degrees, minutes, seconds, direction):
    """Convert DMS (Degrees, Minutes, Seconds) to decimal degrees"""
    decimal = degrees + minutes/60 + seconds/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_dms_coordinates(text):
    """Parse DMS coordinates like 31°44'49.8"N 35°01'46.6"E"""
    dms_pattern = r'(\d+)°(\d+)\'([\d.]+)"([NSEW])\s*(\d+)°(\d+)\'([\d.]+)"([NSEW])'
    match = re.search(dms_pattern, text)
    
    if match:
        try:
            lat_deg = int(match.group(1))
            lat_min = int(match.group(2))
            lat_sec = float(match.group(3))
            lat_dir = match.group(4)
            
            lng_deg = int(match.group(5))
            lng_min = int(match.group(6))
            lng_sec = float(match.group(7))
            lng_dir = match.group(8)
            
            lat = dms_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
            lng = dms_to_decimal(lng_deg, lng_min, lng_sec, lng_dir)
            
            return lat, lng
        except (ValueError, IndexError):
            pass
    
    return None, None

def extract_coordinates_from_google_maps(url):
    """Extract latitude and longitude from Google Maps URL"""
    try:
        coords_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'
        match = re.search(coords_pattern, url)
        
        if match:
            lat, lng = match.groups()
            return float(lat), float(lng)
        
        parsed_url = urlparse(url)
        if 'll' in parsed_url.query:
            params = parse_qs(parsed_url.query)
            if 'll' in params:
                coords = params['ll'][0].split(',')
                if len(coords) == 2:
                    return float(coords[0]), float(coords[1])
        
        if 'q' in parsed_url.query:
            params = parse_qs(parsed_url.query)
            if 'q' in params:
                q_value = params['q'][0]
                coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', q_value)
                if coords_match:
                    lat, lng = coords_match.groups()
                    return float(lat), float(lng)
        
        return None, None
    except Exception as e:
        logger.error(f"Error extracting coordinates: {e}")
        return None, None

def extract_coordinates_from_input(text):
    """Extract coordinates from text (Google Maps URL or coordinates)"""
    coords = extract_coordinates_from_google_maps(text)
    if coords[0] is not None:
        return coords
    
    coords = parse_dms_coordinates(text)
    if coords[0] is not None:
        return coords
    
    coord_pattern = r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)'
    match = re.search(coord_pattern, text)
    if match:
        try:
            lat, lng = float(match.group(1)), float(match.group(2))
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return lat, lng
        except ValueError:
            pass
    
    return None, None

def generate_waze_link(lat, lng):
    """Generate Waze navigation link from coordinates"""
    return f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"

# Flask routes
@app.route('/')
def index():
    """Serve the Mini App interface"""
    with open('/Users/kirilldemidov/claud-projects/maps-to-waze-bot/index.html', 'r') as f:
        return f.read()

@app.route('/script.js')
def script():
    """Serve the JavaScript file"""
    return send_from_directory('.', 'script.js', mimetype='application/javascript')

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK'

@app.route('/api/convert', methods=['POST'])
def api_convert():
    """API endpoint for coordinate conversion"""
    try:
        data = request.get_json()
        input_text = data.get('input', '').strip()
        
        if not input_text:
            return jsonify({'error': 'Input text is required'}), 400
        
        lat, lng = extract_coordinates_from_input(input_text)
        
        if lat is None or lng is None:
            return jsonify({'error': 'Could not extract valid coordinates from input'}), 400
        
        waze_url = generate_waze_link(lat, lng)
        
        return jsonify({
            'success': True,
            'coordinates': {'lat': lat, 'lng': lng},
            'waze_url': waze_url
        })
        
    except Exception as e:
        logger.error(f"API conversion error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    web_app_url = os.getenv('WEB_APP_URL', 'https://maps-to-waze-bot-16542874441.us-central1.run.app')
    
    keyboard = [
        [InlineKeyboardButton("🚀 Open Mini App", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = (
        "Hello! 👋\n\n"
        "I'm a bot for converting Google Maps links to Waze.\n\n"
        "🚀 **Try the new Mini App** - tap the button below for a better experience!\n\n"
        "Or send me either:\n"
        "• Google Maps link\n"
        "• Decimal coordinates (lat, lng)\n"
        "• DMS coordinates\n\n"
        "Examples:\n"
        "• https://maps.google.com/...\n"
        "• 40.7128, -74.0060\n"
        "• 31°44'49.8\"N 35°01'46.6\"E"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    web_app_url = os.getenv('WEB_APP_URL', 'https://maps-to-waze-bot-16542874441.us-central1.run.app')
    
    keyboard = [
        [InlineKeyboardButton("🚀 Open Mini App", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = (
        "How to use the bot:\n\n"
        "🚀 **Mini App** - Tap the button below for the best experience with:\n"
        "• Beautiful interface\n"
        "• Location detection\n"
        "• Easy sharing\n\n"
        "📝 **Text mode** - Send me:\n"
        "• https://maps.google.com/...\n"
        "• https://www.google.com/maps/...\n"
        "• https://goo.gl/maps/...\n"
        "• Decimal: 40.7128, -74.0060\n"
        "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
        "Commands:\n"
        "/start - Start using the bot\n"
        "/help - Show this message"
    )
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and convert Google Maps links or coordinates to Waze"""
    message_text = update.message.text
    
    lat, lng = extract_coordinates_from_input(message_text)
    
    if lat is None or lng is None:
        web_app_url = os.getenv('WEB_APP_URL', 'https://maps-to-waze-bot-16542874441.us-central1.run.app')
        
        keyboard = [
            [InlineKeyboardButton("🚀 Try Mini App", web_app=WebAppInfo(url=web_app_url))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Please send either:\n\n"
            "• Google Maps link\n"
            "• Decimal coordinates (lat, lng)\n"
            "• DMS coordinates\n\n"
            "Examples:\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E\n\n"
            "💡 Or try our Mini App for a better experience:",
            reply_markup=reply_markup
        )
        return
    
    waze_url = generate_waze_link(lat, lng)
    
    response_message = (
        f"✅ Link converted!\n\n"
        f"📍 Coordinates: {lat}, {lng}\n\n"
        f"🚗 Open in Waze:\n{waze_url}"
    )
    
    await update.message.reply_text(response_message)

def run_telegram_bot():
    """Run the Telegram bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Telegram bot started!")
    application.run_polling()

def main():
    """Start both Flask app and Telegram bot"""
    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🌐 Flask app starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()