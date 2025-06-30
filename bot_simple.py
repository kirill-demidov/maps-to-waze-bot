import os
import re
import logging
from urllib.parse import parse_qs, urlparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Same coordinate functions as before
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

def expand_short_url(url):
    """Expand shortened URLs like maps.app.goo.gl"""
    try:
        import requests
        logger.info(f"🔗 Expanding URL: {url}")
        response = requests.head(url, allow_redirects=True, timeout=5)
        expanded = response.url
        logger.info(f"✅ Expanded to: {expanded}")
        return expanded
    except Exception as e:
        logger.error(f"❌ Could not expand URL: {e}")
        return url

def extract_coordinates_from_google_maps(url):
    """Extract latitude and longitude from Google Maps URL"""
    try:
        # Try to expand shortened URLs first
        if 'maps.app.goo.gl' in url or 'goo.gl/maps' in url:
            url = expand_short_url(url)
        
        # Pattern for @lat,lng format
        coords_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'
        match = re.search(coords_pattern, url)
        
        if match:
            lat, lng = match.groups()
            return float(lat), float(lng)
        
        # Pattern for /place/ URLs with !3d and !4d parameters
        place_pattern = r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)'
        match = re.search(place_pattern, url)
        
        if match:
            lat, lng = match.groups()
            logger.info(f"📍 Found place coordinates: {lat}, {lng}")
            return float(lat), float(lng)
        
        # Pattern for /search/ URLs with coordinates
        search_pattern = r'/search/(-?\d+\.?\d*),\+?(-?\d+\.?\d*)'
        match = re.search(search_pattern, url)
        
        if match:
            lat, lng = match.groups()
            logger.info(f"📍 Found search coordinates: {lat}, {lng}")
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

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user.first_name if update.effective_user else "User"
    logger.info(f"👤 /start from {user}")
    
    welcome_message = (
        "Hello! 👋\n\n"
        "I'm a bot for converting Google Maps links to Waze.\n\n"
        "Send me:\n"
        "• Google Maps link\n"
        "• Decimal coordinates (lat, lng)\n"
        "• DMS coordinates\n\n"
        "Examples:\n"
        "• https://maps.google.com/...\n"
        "• https://maps.app.goo.gl/...\n"
        "• 40.7128, -74.0060\n"
        "• 31°44'49.8\"N 35°01'46.6\"E"
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    user = update.effective_user.first_name if update.effective_user else "User"
    logger.info(f"👤 /help from {user}")
    
    help_text = (
        "How to use:\n\n"
        "📝 Send me any of these formats:\n"
        "• https://maps.google.com/...\n"
        "• https://maps.app.goo.gl/...\n"
        "• Decimal: 40.7128, -74.0060\n"
        "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
        "I'll convert them to Waze navigation links!"
    )
    
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and convert coordinates to Waze"""
    user = update.effective_user.first_name if update.effective_user else "User"
    message_text = update.message.text
    
    logger.info(f"👤 Message from {user}: {message_text}")
    
    lat, lng = extract_coordinates_from_input(message_text)
    
    if lat is None or lng is None:
        logger.warning(f"❌ Could not parse: {message_text}")
        
        await update.message.reply_text(
            "Please send:\n"
            "• Google Maps link\n"
            "• Coordinates (40.7128, -74.0060)\n"
            "• DMS (31°44'49.8\"N 35°01'46.6\"E)\n\n"
            "Examples:\n"
            "• https://maps.app.goo.gl/abc123\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        )
        return
    
    waze_url = generate_waze_link(lat, lng)
    
    logger.info(f"✅ Converted for {user}: {lat}, {lng}")
    
    response_message = (
        f"✅ Converted!\n\n"
        f"📍 Coordinates: {lat}, {lng}\n\n"
        f"🚗 Open in Waze:\n{waze_url}"
    )
    
    await update.message.reply_text(response_message)

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: Bot token not found!")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Simple bot started!")
    print("📋 All messages will be logged here")
    application.run_polling()

if __name__ == '__main__':
    main()