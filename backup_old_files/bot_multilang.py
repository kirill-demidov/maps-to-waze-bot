import os
import re
import logging
from urllib.parse import parse_qs, urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from translations import get_text, set_user_language, get_user_language, detect_language_from_text

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)  # Reduce HTTP logs
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
        logger.info(f"🔗 {get_text(None, 'expanding_url')}: {url}")
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
            logger.info(f"📍 {get_text(None, 'found_coordinates')}: {lat}, {lng}")
            return float(lat), float(lng)
        
        # Pattern for /search/ URLs with coordinates
        search_pattern = r'/search/(-?\d+\.?\d*),\+?(-?\d+\.?\d*)'
        match = re.search(search_pattern, url)
        
        if match:
            lat, lng = match.groups()
            logger.info(f"📍 {get_text(None, 'found_coordinates')}: {lat}, {lng}")
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
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name if user else "User"
    
    # Auto-detect language from user's language setting
    if user.language_code:
        if user.language_code.startswith('ru'):
            set_user_language(user_id, 'ru')
        elif user.language_code.startswith('he'):
            set_user_language(user_id, 'he')
        else:
            set_user_language(user_id, 'en')
    
    logger.info(f"👤 /start from {user_name} (lang: {get_user_language(user_id)})")
    
    welcome_message = get_text(user_id, 'welcome')
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name if user else "User"
    
    logger.info(f"👤 /help from {user_name} (lang: {get_user_language(user_id)})")
    
    help_text = get_text(user_id, 'help')
    await update.message.reply_text(help_text)

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇮🇱 עברית", callback_data="lang_he")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    language_text = get_text(user_id, 'language_select')
    await update.message.reply_text(language_text, reply_markup=reply_markup)

async def handle_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_name = query.from_user.first_name if query.from_user else "User"
    
    language_code = query.data.split("_")[1]  # Extract 'en', 'ru', or 'he'
    
    if set_user_language(user_id, language_code):
        logger.info(f"👤 {user_name} changed language to {language_code}")
        
        success_message = get_text(user_id, 'language_changed')
        await query.edit_message_text(success_message)
        
        # Send welcome message in new language
        welcome_message = get_text(user_id, 'welcome')
        await context.bot.send_message(chat_id=user_id, text=welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and convert coordinates to Waze"""
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name if user else "User"
    message_text = update.message.text
    
    # Auto-detect language from message if not set
    if get_user_language(user_id) == 'en':
        detected_lang = detect_language_from_text(message_text)
        if detected_lang != 'en':
            set_user_language(user_id, detected_lang)
    
    logger.info(f"👤 Message from {user_name} ({get_user_language(user_id)}): {message_text}")
    
    lat, lng = extract_coordinates_from_input(message_text)
    
    if lat is None or lng is None:
        logger.warning(f"❌ Could not parse: {message_text}")
        
        invalid_message = get_text(user_id, 'invalid_input')
        await update.message.reply_text(invalid_message)
        return
    
    waze_url = generate_waze_link(lat, lng)
    
    logger.info(f"✅ {get_text(user_id, 'converted_for_user')} {user_name}: {lat}, {lng}")
    
    response_message = (
        f"{get_text(user_id, 'converted')}\n\n"
        f"{get_text(user_id, 'coordinates')}: {lat}, {lng}\n\n"
        f"{get_text(user_id, 'open_waze')}\n{waze_url}"
    )
    
    await update.message.reply_text(response_message)

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: Bot token not found!")
        print("Set the TELEGRAM_BOT_TOKEN environment variable")
        print("Example: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("lang", lang_command))
    application.add_handler(CallbackQueryHandler(handle_language_callback, pattern=r"^lang_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Multi-language bot started!")
    print("🌐 Supported languages: English, Русский, עברית")
    print("📋 All messages will be logged here")
    application.run_polling()

if __name__ == '__main__':
    main()