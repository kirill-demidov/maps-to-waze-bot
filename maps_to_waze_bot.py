import os
import re
import logging
import threading
import requests
from urllib.parse import parse_qs, urlparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler

# Google Maps API
try:
    import googlemaps
    GOOGLE_MAPS_API_AVAILABLE = True
except ImportError:
    GOOGLE_MAPS_API_AVAILABLE = False
    googlemaps = None

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

def expand_short_url(url):
    """Expand short Google Maps URL to get the full URL with coordinates"""
    try:
        # Check if it's a short Google Maps URL
        if 'maps.app.goo.gl' in url or 'goo.gl' in url:
            # Follow redirects to get the final URL
            response = requests.head(url, allow_redirects=True, timeout=10)
            return response.url
        return url
    except Exception as e:
        logger.error(f"Error expanding short URL: {e}")
        return url

def extract_coordinates_from_google_maps_api(url):
    """Extract coordinates from Google Maps URL using Google Maps API"""
    if not GOOGLE_MAPS_API_AVAILABLE:
        return None, None
    
    try:
        # Get API key from environment
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            logger.warning("Google Maps API key not found")
            return None, None
        
        # Initialize Google Maps client
        gmaps = googlemaps.Client(key=api_key)
        
        # First try to extract place ID from URL
        place_id = extract_place_id_from_url(url)
        if place_id:
            try:
                # Get place details by place ID
                place_details = gmaps.place(place_id)
                
                if place_details and 'result' in place_details:
                    location = place_details['result'].get('geometry', {}).get('location', {})
                    if location:
                        lat = location.get('lat')
                        lng = location.get('lng')
                        if lat is not None and lng is not None:
                            return lat, lng
            except Exception as e:
                logger.warning(f"Place ID method failed: {e}")
        
        # If place ID method fails, try text search
        try:
            # Extract location name from URL
            expanded_url = expand_short_url(url)
            
            # Extract location name from the URL path
            location_name = None
            if '/place/' in expanded_url:
                # Extract the place name from the URL
                place_match = re.search(r'/place/([^/]+)', expanded_url)
                if place_match:
                    location_name = place_match.group(1).replace('+', ' ')
            
            if location_name:
                # Search for the location
                search_result = gmaps.places(location_name)
                
                if search_result and 'results' in search_result and search_result['results']:
                    # Get the first result
                    first_result = search_result['results'][0]
                    location = first_result.get('geometry', {}).get('location', {})
                    if location:
                        lat = location.get('lat')
                        lng = location.get('lng')
                        if lat is not None and lng is not None:
                            return lat, lng
        
        except Exception as e:
            logger.warning(f"Text search method failed: {e}")
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error extracting coordinates via Google Maps API: {e}")
        return None, None

def extract_place_id_from_url(url):
    """Extract place ID from Google Maps URL"""
    try:
        # Expand short URL first
        expanded_url = expand_short_url(url)
        
        # Pattern for place ID in URL
        place_patterns = [
            r'1s0x([^:]+):([^!]+)',
            r'1s([^!]+)',
            r'data=!4m2!3m1!1s([^!]+)',
            r'place/([^/]+)',
            r'place_id=([^&]+)',
            r'([^/]+)/data=!4m2!3m1!1s([^!]+)'
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, expanded_url)
            if match:
                if len(match.groups()) == 2:
                    # For patterns with two groups, combine them
                    place_id = f"{match.group(1)}:{match.group(2)}"
                else:
                    place_id = match.group(1)
                
                # Clean up the place ID - remove query parameters and extra data
                place_id = place_id.split('?')[0].split('&')[0].split('!')[0]
                
                # For Google Maps place IDs, we need the hex part
                if '0x' in place_id:
                    # Extract the hex part after 0x
                    hex_match = re.search(r'0x([a-fA-F0-9]+)', place_id)
                    if hex_match:
                        return hex_match.group(1)
                
                return place_id
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting place ID: {e}")
        return None

def extract_coordinates_from_input(text):
    """Extract coordinates from text (Google Maps URL or coordinates)"""
    # First try to extract from URL using standard methods
    coords = extract_coordinates_from_google_maps(text)
    if coords[0] is not None:
        return coords
    
    # Try to extract using Google Maps API (for place URLs)
    if 'maps.google.com' in text or 'maps.app.goo.gl' in text or 'goo.gl' in text:
        coords = extract_coordinates_from_google_maps_api(text)
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
        # Expand short URLs first
        expanded_url = expand_short_url(url)
        
        # Pattern for @lat,lng format
        coords_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'
        match = re.search(coords_pattern, expanded_url)
        
        if match:
            lat, lng = match.groups()
            return float(lat), float(lng)
        
        # Pattern for @lat,lng,zoom format (with zoom level)
        coords_zoom_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*),(\d+z)'
        match = re.search(coords_zoom_pattern, expanded_url)
        
        if match:
            lat, lng, zoom = match.groups()
            return float(lat), float(lng)
        
        # Pattern for ll parameter
        parsed_url = urlparse(expanded_url)
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
        
        # Pattern for place parameter (newer Google Maps format)
        if 'place' in parsed_url.path:
            # Try to extract coordinates from place path
            place_pattern = r'place/([^/]+)'
            place_match = re.search(place_pattern, expanded_url)
            if place_match:
                place_data = place_match.group(1)
                # Look for coordinates in the place data
                coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', place_data)
                if coords_match:
                    lat, lng = coords_match.groups()
                    return float(lat), float(lng)
        
        # Pattern for search parameter
        if 'search' in parsed_url.path:
            search_pattern = r'search/([^/]+)'
            search_match = re.search(search_pattern, expanded_url)
            if search_match:
                search_data = search_match.group(1)
                coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', search_data)
                if coords_match:
                    lat, lng = coords_match.groups()
                    return float(lat), float(lng)
        
        # Try to extract coordinates from the entire expanded URL
        # This is a fallback for complex URLs
        coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', expanded_url)
        if coords_match:
            lat, lng = coords_match.groups()
            # Validate coordinate ranges
            lat, lng = float(lat), float(lng)
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return lat, lng
        
        # Try to extract from complex query parameters
        # Look for coordinates in various parameter formats
        for param_name in ['q', 'll', 'sll', 'daddr']:
            if param_name in parsed_url.query:
                params = parse_qs(parsed_url.query)
                if param_name in params:
                    param_value = params[param_name][0]
                    # Try to find coordinates in parameter value
                    coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', param_value)
                    if coords_match:
                        lat, lng = coords_match.groups()
                        lat, lng = float(lat), float(lng)
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            return lat, lng
        
        # Try to extract from path segments
        path_segments = parsed_url.path.split('/')
        for segment in path_segments:
            coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', segment)
            if coords_match:
                lat, lng = coords_match.groups()
                lat, lng = float(lat), float(lng)
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    return lat, lng
        
        return None, None
    except Exception as e:
        logger.error(f"Error extracting coordinates: {e}")
        return None, None

def generate_waze_link(lat, lng):
    """Generate Waze navigation link from coordinates"""
    return f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    api_status = "✅ Google Maps API доступен" if GOOGLE_MAPS_API_AVAILABLE else "❌ Google Maps API недоступен"
    
    welcome_message = (
        f"Привет! 👋\n\n"
        f"Я бот для конвертации ссылок Google Maps в Waze.\n\n"
        f"📡 {api_status}\n\n"
        f"Отправьте мне:\n"
        f"• Ссылку Google Maps (любую)\n"
        f"• Координаты в десятичном формате (lat, lng)\n"
        f"• Координаты в формате DMS\n\n"
        f"Примеры:\n"
        f"• https://maps.app.goo.gl/...\n"
        f"• https://maps.google.com/...\n"
        f"• 40.7128, -74.0060\n"
        f"• 31°44'49.8\"N 35°01'46.6\"E"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "Как использовать бота:\n\n"
        "1. Отправьте ссылку Google Maps или координаты\n"
        "2. Получите ссылку для Waze\n\n"
        "Поддерживаемые форматы:\n"
        "• https://maps.app.goo.gl/...\n"
        "• https://maps.google.com/...\n"
        "• https://www.google.com/maps/...\n"
        "• https://goo.gl/maps/...\n"
        "• Десятичные: 40.7128, -74.0060\n"
        "• DMS: 31°44'49.8\"N 35°01'46.6\"E\n\n"
        "Команды:\n"
        "/start - Начать использование бота\n"
        "/help - Показать это сообщение"
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and convert Google Maps links or coordinates to Waze"""
    message_text = update.message.text
    
    # Extract coordinates from input (URL or direct coordinates)
    lat, lng = extract_coordinates_from_input(message_text)
    
    if lat is None or lng is None:
        # Check if it's a Google Maps URL that couldn't be processed
        if 'maps.google.com' in message_text or 'maps.app.goo.gl' in message_text or 'goo.gl' in message_text:
            await update.message.reply_text(
                "❌ Не удалось извлечь координаты из ссылки Google Maps.\n\n"
                "Это может быть ссылка на место без точных координат.\n\n"
                "Попробуйте:\n"
                "• Открыть ссылку в браузере\n"
                "• Нажать на кнопку 'Поделиться'\n"
                "• Выбрать 'Копировать ссылку'\n"
                "• Отправить новую ссылку\n\n"
                "Или отправьте координаты напрямую:\n"
                "• 40.7128, -74.0060\n"
                "• 31°44'49.8\"N 35°01'46.6\"E"
            )
        else:
            await update.message.reply_text(
                "❌ Не удалось извлечь координаты из вашего сообщения.\n\n"
                "Пожалуйста, отправьте:\n"
                "• Ссылку Google Maps (включая короткие ссылки)\n"
                "• Координаты в десятичном формате (lat, lng)\n"
                "• Координаты в формате DMS\n\n"
                "Примеры:\n"
                "• https://maps.app.goo.gl/...\n"
                "• https://maps.google.com/...\n"
                "• 40.7128, -74.0060\n"
                "• 31°44'49.8\"N 35°01'46.6\"E"
            )
        return
    
    # Generate Waze link
    waze_url = generate_waze_link(lat, lng)
    
    response_message = (
        f"✅ Ссылка успешно обработана!\n\n"
        f"📍 Координаты: {lat}, {lng}\n\n"
        f"🚗 Открыть в Waze:\n{waze_url}"
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
    port = int(os.getenv('PORT', 8081))
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