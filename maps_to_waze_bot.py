import os
import re
import logging
import threading
from urllib.parse import parse_qs, urlparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def dms_to_decimal(degrees, minutes, seconds, direction):
    """Convert DMS (Degrees, Minutes, Seconds) to decimal degrees"""
    decimal = degrees + minutes/60 + seconds/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def parse_dms_coordinates(text):
    """Parse DMS coordinates like 31°44'49.8"N 35°01'46.6"E"""
    # Pattern for DMS format: degrees°minutes'seconds"direction
    dms_pattern = r'(\d+)°(\d+)\'([\d.]+)"([NSEW])\s*(\d+)°(\d+)\'([\d.]+)"([NSEW])'
    match = re.search(dms_pattern, text)
    
    if match:
        try:
            # First coordinate (latitude)
            lat_deg = int(match.group(1))
            lat_min = int(match.group(2))
            lat_sec = float(match.group(3))
            lat_dir = match.group(4)
            
            # Second coordinate (longitude)
            lng_deg = int(match.group(5))
            lng_min = int(match.group(6))
            lng_sec = float(match.group(7))
            lng_dir = match.group(8)
            
            # Convert to decimal
            lat = dms_to_decimal(lat_deg, lat_min, lat_sec, lat_dir)
            lng = dms_to_decimal(lng_deg, lng_min, lng_sec, lng_dir)
            
            return lat, lng
        except (ValueError, IndexError):
            pass
    
    return None, None

def extract_coordinates_from_input(text):
    """Extract coordinates from text (Google Maps URL or coordinates)"""
    # First try to extract from URL
    coords = extract_coordinates_from_google_maps(text)
    if coords[0] is not None:
        return coords
    
    # Try to extract DMS coordinates
    coords = parse_dms_coordinates(text)
    if coords[0] is not None:
        return coords
    
    # Try to extract direct coordinates (lat,lng format)
    coord_pattern = r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)'
    match = re.search(coord_pattern, text)
    if match:
        try:
            lat, lng = float(match.group(1)), float(match.group(2))
            # Validate coordinate ranges
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return lat, lng
        except ValueError:
            pass
    
    return None, None

def extract_coordinates_from_google_maps(url):
    """Extract latitude and longitude from Google Maps URL"""
    try:
        # Pattern for @lat,lng format
        coords_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'
        match = re.search(coords_pattern, url)
        
        if match:
            lat, lng = match.groups()
            return float(lat), float(lng)
        
        # Pattern for ll parameter
        parsed_url = urlparse(url)
        if 'll' in parsed_url.query:
            params = parse_qs(parsed_url.query)
            if 'll' in params:
                coords = params['ll'][0].split(',')
                if len(coords) == 2:
                    return float(coords[0]), float(coords[1])
        
        # Pattern for q parameter with coordinates
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

def generate_waze_link(lat, lng):
    """Generate Waze navigation link from coordinates"""
    return f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "Hello! 👋\n\n"
        "I'm a bot for converting Google Maps links to Waze.\n\n"
        "Send me either:\n"
        "• Google Maps link\n"
        "• Decimal coordinates (lat, lng)\n"
        "• DMS coordinates\n\n"
        "Examples:\n"
        "• https://maps.google.com/...\n"
        "• 40.7128, -74.0060\n"
        "• 31°44'49.8\"N 35°01'46.6\"E"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "How to use the bot:\n\n"
        "1. Send a Google Maps link or coordinates\n"
        "2. Get a Waze link\n\n"
        "Supported formats:\n"
        "• https://maps.google.com/...\n"
        "• https://www.google.com/maps/...\n"
        "• https://goo.gl/maps/...\n"
        "• Decimal: 40.7128, -74.0060\n"
        "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
        "Commands:\n"
        "/start - Start using the bot\n"
        "/help - Show this message"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and convert Google Maps links or coordinates to Waze"""
    message_text = update.message.text
    
    # Extract coordinates from input (URL or direct coordinates)
    lat, lng = extract_coordinates_from_input(message_text)
    
    if lat is None or lng is None:
        await update.message.reply_text(
            "Please send either:\n\n"
            "• Google Maps link\n"
            "• Decimal coordinates (lat, lng)\n"
            "• DMS coordinates\n\n"
            "Examples:\n"
            "• https://maps.google.com/...\n"
            "• 40.7128, -74.0060\n"
            "• 31°44'49.8\"N 35°01'46.6\"E"
        )
        return
    
    # Generate Waze link
    waze_url = generate_waze_link(lat, lng)
    
    response_message = (
        f"✅ Link converted!\n\n"
        f"📍 Coordinates: {lat}, {lng}\n\n"
        f"🚗 Open in Waze:\n{waze_url}"
    )
    
    await update.message.reply_text(response_message)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

def run_http_server():
    """Run HTTP server for health checks"""
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('', port), HealthCheckHandler)
    print(f"🌐 HTTP server started on port {port}")
    server.serve_forever()

def main():
    """Start the bot"""
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: Bot token not found!")
        print("Set the TELEGRAM_BOT_TOKEN environment variable")
        print("Example: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
    
    # Start HTTP server in a separate thread for Cloud Run health checks
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run the bot
    print("🤖 Bot started!")
    application.run_polling()

if __name__ == '__main__':
    main()