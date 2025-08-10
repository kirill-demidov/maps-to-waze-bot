import os
import re
import logging
import threading
import requests
import json
import urllib.parse
import time
from urllib.parse import parse_qs, urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import translations
from translations import get_text, get_button_text, get_language_name, is_valid_language, LANGUAGES

# Import analytics
try:
    from analytics import analytics
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    analytics = None



# Google Maps API
try:
    import googlemaps
    GOOGLE_MAPS_API_AVAILABLE = True
except ImportError:
    GOOGLE_MAPS_API_AVAILABLE = False
    googlemaps = None

# Admin panel settings
ADMIN_USER_IDS = os.getenv('ADMIN_USER_IDS', '').split(',')  # Comma-separated list of admin Telegram user IDs

# Track processed messages to prevent duplicates
processed_messages = set()

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
        # Define headers for HTTP requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Check if it's a short Google Maps URL
        if 'maps.app.goo.gl' in url or 'goo.gl' in url:
            # For maps.app.goo.gl, try to expand first, then fallback
            if 'maps.app.goo.gl' in url:
                # Try to expand the URL first
                try:
                    response = requests.get(url, allow_redirects=True, timeout=1, headers=headers)
                    if response.url != url:
                        logger.info(f"Successfully expanded maps.app.goo.gl: {response.url}")
                        return response.url
                except Exception as e:
                    logger.warning(f"Failed to expand maps.app.goo.gl: {e}")
                
                # Fallback to place ID method
                place_id = url.split('/')[-1].split('?')[0]
                return f"https://www.google.com/maps/place/{place_id}"
            
            # For other short URLs, try GET request with shorter timeout
            try:
                response = requests.get(url, allow_redirects=True, timeout=1, headers=headers)
                if response.url != url:
                    logger.info(f"Successfully expanded URL: {response.url}")
                    return response.url
            except Exception as e:
                logger.warning(f"GET request failed: {e}")
            
        return url
    except Exception as e:
        logger.error(f"Error expanding short URL: {e}")
        return url

def extract_coordinates_from_google_maps_api(url):
    """Extract coordinates from Google Maps URL using Google Maps API"""
    if not GOOGLE_MAPS_API_AVAILABLE:
        logger.warning("Google Maps API not available")
        return None, None
    
    try:
        logger.info(f"Trying to extract coordinates via API for URL: {url}")
        
        # Get API key from environment
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            logger.warning("Google Maps API key not found")
            return None, None
        
        # Initialize Google Maps client with shorter timeout
        gmaps = googlemaps.Client(key=api_key, timeout=2)
        
        # First try to extract place ID from URL
        place_id = extract_place_id_from_url(url)
        logger.info(f"Extracted place ID: {place_id}")
        
        if place_id:
            try:
                # Get place details by place ID
                logger.info(f"Calling Google Maps API with place ID: {place_id}")
                place_details = gmaps.place(place_id)
                
                if place_details and 'result' in place_details:
                    location = place_details['result'].get('geometry', {}).get('location', {})
                    if location:
                        lat = location.get('lat')
                        lng = location.get('lng')
                        if lat is not None and lng is not None:
                            logger.info(f"Found coordinates via place ID: {lat}, {lng}")
                            return lat, lng
                else:
                    logger.warning(f"No place details found for place ID: {place_id}")
            except Exception as e:
                logger.warning(f"Place ID method failed: {e}")
        
        # If place ID method fails, try text search
        try:
            logger.info("Trying text search method...")
            # Extract location name from URL
            expanded_url = expand_short_url(url)
            
            # Extract location name from the URL path
            location_name = None
            if '/place/' in expanded_url:
                # Extract the place name from the URL
                place_match = re.search(r'/place/([^/]+)', expanded_url)
                if place_match:
                    location_name = place_match.group(1).replace('+', ' ')
                    logger.info(f"Extracted location name: {location_name}")
            
            if location_name:
                # Search for the location
                logger.info(f"Searching for location: {location_name}")
                search_result = gmaps.places(location_name)
                
                if search_result and 'results' in search_result and search_result['results']:
                    # Get the first result
                    first_result = search_result['results'][0]
                    location = first_result.get('geometry', {}).get('location', {})
                    if location:
                        lat = location.get('lat')
                        lng = location.get('lng')
                        if lat is not None and lng is not None:
                            logger.info(f"Found coordinates via text search: {lat}, {lng}")
                            return lat, lng
                else:
                    logger.warning(f"No search results found for: {location_name}")
            else:
                logger.warning("Could not extract location name from URL")
        
        except Exception as e:
            logger.warning(f"Text search method failed: {e}")
        
        logger.warning("API method failed to find coordinates")
        
        # Final fallback: try to extract coordinates from URL patterns
        try:
            # Look for coordinates in the URL itself
            coord_patterns = [
                r'@(-?\d+\.?\d*),(-?\d+\.?\d*)',
                r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)',
                r'!1d(-?\d+\.?\d*)!2d(-?\d+\.?\d*)',
                r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)!5d(-?\d+\.?\d*)',
                r'search/(-?\d+\.?\d*),(-?\d+\.?\d*)'
            ]
            
            for pattern in coord_patterns:
                match = re.search(pattern, url)
                if match:
                    if len(match.groups()) >= 2:
                        lat = float(match.group(1))
                        lng = float(match.group(2))
                        logger.info(f"Found coordinates via URL pattern: {lat}, {lng}")
                        return lat, lng
            
            logger.warning("No coordinates found in URL patterns")
        except Exception as e:
            logger.warning(f"URL pattern extraction failed: {e}")
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error extracting coordinates via Google Maps API: {e}")
        return None, None

def extract_place_id_from_url(url):
    """Extract place ID from Google Maps URL"""
    try:
        # Expand short URL first
        expanded_url = expand_short_url(url)
        logger.info(f"Expanded URL: {expanded_url}")
        
        # Pattern for place ID in URL - updated for modern Google Maps URLs
        place_patterns = [
            # Modern Google Maps place IDs
            r'place_id=([^&]+)',
            r'place/([^/]+)',
            r'1s0x([^:]+):([^!]+)',
            r'1s([^!]+)',
            r'data=!4m2!3m1!1s([^!]+)',
            r'([^/]+)/data=!4m2!3m1!1s([^!]+)',
            # New patterns for modern URLs
            r'@(-?\d+\.?\d*),(-?\d+\.?\d*)',
            r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)',
            r'!1d(-?\d+\.?\d*)!2d(-?\d+\.?\d*)',
            # Short URL patterns
            r'goo\.gl/maps/([^/?]+)',
            r'maps\.app\.goo\.gl/([^/?]+)'
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, expanded_url)
            if match:
                if len(match.groups()) == 2:
                    # For coordinate patterns, return None (coordinates will be extracted separately)
                    if 'd' in pattern or '@' in pattern:
                        continue
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
    # logger.info(f"Extracting coordinates from input: {text}")  # Removed for speed
    
    # First try direct coordinate parsing (fastest)
    coord_pattern = r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)'
    match = re.search(coord_pattern, text)
    if match:
        try:
            lat, lng = float(match.group(1)), float(match.group(2))
            # Validate coordinate ranges
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                logger.info(f"Found coordinates via direct pattern: {lat}, {lng}")
                return lat, lng
        except ValueError:
            pass
    
    # For Google Maps short URLs, try fast methods first, then API
    if 'maps.app.goo.gl' in text:
        logger.info("Processing short Google Maps URL")
        try:
            # First try to expand the URL to get the full URL
            expanded_url = expand_short_url(text)
            logger.info(f"Expanded URL: {expanded_url}")
            
            # Try to extract coordinates from expanded URL
            coords = extract_coordinates_from_google_maps(expanded_url)
            if coords[0] is not None:
                logger.info(f"Found coordinates from expanded URL: {coords}")
                return coords
            
            # If no coordinates found in expanded URL, try place ID method
            place_id = text.split('/')[-1].split('?')[0]
            fallback_url = f"https://www.google.com/maps/place/{place_id}"
            
            # Try to extract coordinates from fallback URL
            coords = extract_coordinates_from_google_maps(fallback_url)
            if coords[0] is not None:
                logger.info(f"Found coordinates from fallback URL: {coords}")
                return coords
            
            # If no coordinates found, try Google Maps API (slower but more reliable)
            if GOOGLE_MAPS_API_AVAILABLE:
                coords = extract_coordinates_from_google_maps_api(text)
                if coords[0] is not None:
                    logger.info(f"Found coordinates via API: {coords}")
                    return coords
                
                # Try API with expanded URL
                coords = extract_coordinates_from_google_maps_api(expanded_url)
                if coords[0] is not None:
                    logger.info(f"Found coordinates via API with expanded URL: {coords}")
                    return coords
            
            # Final fallback: try to extract coordinates from the short URL itself
            # Some short URLs contain coordinates in the path
            coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', text)
            if coords_match:
                lat, lng = coords_match.groups()
                # Validate coordinate ranges
                lat, lng = float(lat), float(lng)
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    logger.info(f"Found coordinates in short URL: {lat}, {lng}")
                    return lat, lng
            
            logger.warning("Could not extract coordinates from short URL")
        except Exception as e:
            logger.error(f"Error processing short URL: {e}")
    
    # Then try to extract from URL using standard methods (fast and reliable)
    if any(keyword in text.lower() for keyword in ['maps.google.com', 'google.com/maps']):
        coords = extract_coordinates_from_google_maps(text)
        if coords[0] is not None:
            logger.info(f"Found coordinates via standard method: {coords}")
            return coords
        
        # If no coordinates found in URL, don't try API (too slow)
        logger.warning("No coordinates found in Google Maps URL")
    
    # Try to extract DMS coordinates
    coords = parse_dms_coordinates(text)
    if coords[0] is not None:
        logger.info(f"Found coordinates via DMS method: {coords}")
        return coords
    
    logger.warning("No coordinates found in input")
    return None, None

def extract_coordinates_from_google_maps(url):
    """Extract latitude and longitude from Google Maps URL"""
    import urllib.parse
    try:
        expanded_url = url
        # Если это consent.google.com, ищем только в параметре continue
        if 'consent.google.com' in expanded_url:
            continue_match = re.search(r'continue=([^&]+)', expanded_url)
            if continue_match:
                continue_data = urllib.parse.unquote(continue_match.group(1))
                # Сначала ищем паттерн с плюсом
                match = re.search(r'(-?\d+\.?\d*),\+(-?\d+\.?\d*)', continue_data)
                if match:
                    lat, lng = match.groups()
                    logger.info(f"Found coordinates via consent continue +: {lat}, {lng}")
                    return float(lat), float(lng)
                # Потом обычный паттерн
                match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', continue_data)
                if match:
                    lat, lng = match.groups()
                    logger.info(f"Found coordinates via consent continue: {lat}, {lng}")
                    return float(lat), float(lng)
                # Ищем паттерн !3d и !4d (для place ссылок)
                match = re.search(r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)', continue_data)
                if match:
                    lat, lng = match.groups()
                    logger.info(f"Found coordinates via consent continue !3d!4d: {lat}, {lng}")
                    return float(lat), float(lng)
            return None, None
        # Pattern for @lat,lng format
        coords_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'
        match = re.search(coords_pattern, expanded_url)
        
        if match:
            lat, lng = match.groups()
            logger.info(f"Found coordinates via @ pattern: {lat}, {lng}")
            return float(lat), float(lng)
        
        # Pattern for @lat,lng,zoom format (with zoom level)
        coords_zoom_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*),(\d+z)'
        match = re.search(coords_zoom_pattern, expanded_url)
        
        if match:
            lat, lng, zoom = match.groups()
            logger.info(f"Found coordinates via @zoom pattern: {lat}, {lng}")
            return float(lat), float(lng)
        
        # Pattern for !3d and !4d format (newer Google Maps)
        coords_3d4d_pattern = r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)'
        match = re.search(coords_3d4d_pattern, expanded_url)
        
        if match:
            lat, lng = match.groups()
            logger.info(f"Found coordinates via !3d!4d pattern: {lat}, {lng}")
            return float(lat), float(lng)
        
        # Pattern for !1d and !2d format (alternative)
        coords_1d2d_pattern = r'!1d(-?\d+\.?\d*)!2d(-?\d+\.?\d*)'
        match = re.search(coords_1d2d_pattern, expanded_url)
        
        if match:
            lat, lng = match.groups()
            logger.info(f"Found coordinates via !1d!2d pattern: {lat}, {lng}")
            return float(lat), float(lng)
        
        # Pattern for ll parameter
        parsed_url = urlparse(expanded_url)
        if 'll' in parsed_url.query:
            params = parse_qs(parsed_url.query)
            if 'll' in params:
                coords = params['ll'][0].split(',')
                if len(coords) == 2:
                    logger.info(f"Found coordinates via ll parameter: {coords[0]}, {coords[1]}")
                    return float(coords[0]), float(coords[1])
        
        # Pattern for q parameter with coordinates
        if 'q' in parsed_url.query:
            params = parse_qs(parsed_url.query)
            if 'q' in params:
                q_value = params['q'][0]
                coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', q_value)
                if coords_match:
                    lat, lng = coords_match.groups()
                    logger.info(f"Found coordinates via q parameter: {lat}, {lng}")
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
                    logger.info(f"Found coordinates via place path: {lat}, {lng}")
                    return float(lat), float(lng)
        
        # Pattern for search parameter with coordinates
        if 'search' in parsed_url.path:
            search_pattern = r'search/([^/]+)'
            search_match = re.search(search_pattern, expanded_url)
            if search_match:
                search_data = search_match.group(1)
                # Look for coordinates in the search data
                coords_match = re.search(r'(-?\d+\.?\d*),\+(-?\d+\.?\d*)', search_data)
                if coords_match:
                    lat, lng = coords_match.groups()
                    logger.info(f"Found coordinates via search path with +: {lat}, {lng}")
                    return float(lat), float(lng)
                # Also try without +
                coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', search_data)
                if coords_match:
                    lat, lng = coords_match.groups()
                    logger.info(f"Found coordinates via search path: {lat}, {lng}")
                    return float(lat), float(lng)
                coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', search_data)
                if coords_match:
                    lat, lng = coords_match.groups()
                    logger.info(f"Found coordinates via search path: {lat}, {lng}")
                    return float(lat), float(lng)
        
        # Try to extract coordinates from the entire expanded URL
        # This is a fallback for complex URLs
        # URL decode first to handle encoded coordinates
        import urllib.parse
        decoded_url = urllib.parse.unquote(expanded_url)
        coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', decoded_url)
        if coords_match:
            lat, lng = coords_match.groups()
            # Validate coordinate ranges
            lat, lng = float(lat), float(lng)
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                logger.info(f"Found coordinates via fallback pattern: {lat}, {lng}")
                return lat, lng
        
        # Try to extract coordinates from /search/ path in Google Maps URL
        search_pattern = r'/search/(-?\d+\.?\d*),?\s*(-?\d+\.?\d*)'
        search_match = re.search(search_pattern, expanded_url)
        if search_match:
            lat, lng = search_match.groups()
            # Validate coordinate ranges
            lat, lng = float(lat), float(lng)
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                logger.info(f"Found coordinates via search path pattern: {lat}, {lng}")
                return lat, lng
        
        # Try to extract from the continue parameter in consent URLs (check this first)
        continue_match = re.search(r'continue=([^&]+)', expanded_url)
        if continue_match:
            continue_data = urllib.parse.unquote(continue_match.group(1))
            logger.info(f"Continue data: {continue_data}")
            
            # Look for coordinates in continue data
            # Try different patterns for coordinates
            coord_patterns = [
                r'(-?\d+\.?\d*),(-?\d+\.?\d*)',  # Standard format
                r'(-?\d+\.?\d*),\+(-?\d+\.?\d*)',  # With plus sign
                r'(-?\d+\.?\d*),%2B(-?\d+\.?\d*)',  # URL encoded plus
            ]
            
            for pattern in coord_patterns:
                coords_match = re.search(pattern, continue_data)
                if coords_match:
                    lat, lng = coords_match.groups()
                    # Validate coordinate ranges
                    lat, lng = float(lat), float(lng)
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        logger.info(f"Found coordinates via continue parameter: {lat}, {lng}")
                        return lat, lng
            
            # Also try the original encoded continue data
            original_continue = continue_match.group(1)
            for pattern in coord_patterns:
                coords_match = re.search(pattern, original_continue)
                if coords_match:
                    lat, lng = coords_match.groups()
                    # Validate coordinate ranges
                    lat, lng = float(lat), float(lng)
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        logger.info(f"Found coordinates via original continue parameter: {lat}, {lng}")
                        return lat, lng
        
        # Try to extract coordinates from search path (new pattern) - but only if it's not a consent URL
        if 'consent.google.com' not in expanded_url:
            search_coords_pattern = r'search/([^?]+)'
            search_match = re.search(search_coords_pattern, expanded_url)
            if search_match:
                search_data = search_match.group(1)
                # URL decode the search data first
                import urllib.parse
                decoded_data = urllib.parse.unquote(search_data)
                logger.info(f"Decoded search data: {decoded_data}")
                
                # Try to find coordinates in decoded data with different patterns
                coord_patterns = [
                    r'(-?\d+\.?\d*),\+(-?\d+\.?\d*)',  # With plus sign
                    r'(-?\d+\.?\d*),(-?\d+\.?\d*)',   # Standard format
                    r'(-?\d+\.?\d*),%2B(-?\d+\.?\d*)', # URL encoded plus
                ]
                
                for pattern in coord_patterns:
                    coords_match = re.search(pattern, decoded_data)
                    if coords_match:
                        lat, lng = coords_match.groups()
                        # Validate coordinate ranges
                        lat, lng = float(lat), float(lng)
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            logger.info(f"Found coordinates via search path pattern: {lat}, {lng}")
                            return lat, lng
                
                # Also try in the original search_data (before decoding)
                for pattern in coord_patterns:
                    coords_match = re.search(pattern, search_data)
                    if coords_match:
                        lat, lng = coords_match.groups()
                        # Validate coordinate ranges
                        lat, lng = float(lat), float(lng)
                        if -90 <= lat <= 90 and -180 <= lng <= 180:
                            logger.info(f"Found coordinates via original search data: {lat}, {lng}")
                            return lat, lng
        else:
            # For consent URLs, skip search path extraction and go directly to continue parameter
            logger.info("Skipping search path extraction for consent URL")
            # Don't return here, continue to the next checks
            pass
        
        # Try to extract coordinates from place path (modern Google Maps format)
        place_coords_pattern = r'place/([^/]+)'
        place_match = re.search(place_coords_pattern, expanded_url)
        if place_match:
            place_data = place_match.group(1)
            # Look for coordinates in the place data
            coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', place_data)
            if coords_match:
                lat, lng = coords_match.groups()
                # Validate coordinate ranges
                lat, lng = float(lat), float(lng)
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    logger.info(f"Found coordinates via place path: {lat}, {lng}")
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

def is_admin_user(user_id: int) -> bool:
    """Check if user is admin"""
    return str(user_id) in ADMIN_USER_IDS

def get_user_language(user_id: int) -> str:
    """Get user's preferred language"""
    try:
        # Try to load user preferences from file
        with open('user_preferences.json', 'r', encoding='utf-8') as f:
            preferences = json.load(f)
            return preferences.get(str(user_id), 'en')
    except (FileNotFoundError, json.JSONDecodeError):
        return 'en'

def save_user_language(user_id: int, language: str):
    """Save user's language preference"""
    try:
        # Load existing preferences
        try:
            with open('user_preferences.json', 'r', encoding='utf-8') as f:
                preferences = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            preferences = {}
        
        # Update user preference
        preferences[str(user_id)] = language
        
        # Save preferences
        with open('user_preferences.json', 'w', encoding='utf-8') as f:
            json.dump(preferences, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving user language: {e}")

def create_menu_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                get_button_text('help', lang),
                callback_data='help'
            )
        ],
        [
            InlineKeyboardButton(
                get_button_text('language', lang),
                callback_data='language'
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create language selection keyboard"""
    keyboard = []
    row = []
    for lang_code, lang_name in LANGUAGES.items():
        row.append(InlineKeyboardButton(
            get_button_text(lang_code, lang_code),
            callback_data=f'lang_{lang_code}'
        ))
        if len(row) == 2:  # 2 buttons per row
            keyboard.append(row)
            row = []
    
    if row:  # Add remaining buttons
        keyboard.append(row)
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton(
            get_button_text('back', 'en'),  # Default to English for back button
            callback_data='menu'
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    message_id = update.message.message_id
    chat_id = update.effective_chat.id
    
    # Create unique message identifier
    message_key = f"{chat_id}_{message_id}_start"
    
    # Check if message was already processed
    if message_key in processed_messages:
        print(f"⚠️ DUPLICATE START command detected: {message_key}")
        return
    
    # Add to processed messages
    processed_messages.add(message_key)
    
    print(f"🔍 START command received from user {user_id}")
    
    # Track analytics
    if ANALYTICS_AVAILABLE and analytics:
        analytics.track_user_interaction(user_id, "start_command", True)
    
    api_status = get_text('api_available', lang) if GOOGLE_MAPS_API_AVAILABLE else get_text('api_unavailable', lang)
    welcome_message = get_text('welcome', lang, api_status=api_status)
    
    print(f"📤 Sending welcome message to user {user_id}")
    await update.message.reply_text(
        welcome_message,
        reply_markup=create_menu_keyboard(lang)
    )
    print(f"✅ Welcome message sent to user {user_id}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    help_text = get_text('help', lang)
    await update.message.reply_text(
        help_text,
        reply_markup=create_menu_keyboard(lang)
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send menu when the command /menu is issued."""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    menu_text = get_text('menu', lang)
    await update.message.reply_text(
        menu_text,
        reply_markup=create_menu_keyboard(lang)
    )

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send language selection when the command /language is issued."""
    lang = get_user_language(update.effective_user.id)
    
    language_text = get_text('language_menu', lang)
    await update.message.reply_text(
        language_text,
        reply_markup=create_language_keyboard()
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel command"""
    user_id = update.effective_user.id
    
    if not is_admin_user(user_id):
        await update.message.reply_text("❌ Access denied. You are not an admin.")
        return
    
    # Get the bot's URL from environment or construct it
    bot_url = os.getenv('BOT_URL', 'http://159.223.0.234:8080')
    admin_url = f"{bot_url}/admin?user_id={user_id}"
    
    admin_message = (
        f"🔐 Admin Panel\n\n"
        f"🌐 Analytics Dashboard: {admin_url}\n\n"
        f"📊 Available features:\n"
        f"• Real-time bot statistics\n"
        f"• User activity tracking\n"
        f"• Link processing analytics\n"
        f"• Language usage statistics\n"
        f"• User search by ID\n\n"
        f"⚠️ Security: Only you can access this panel"
    )
    
    await update.message.reply_text(admin_message)

async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's Telegram ID"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "No username"
    first_name = update.effective_user.first_name or "Unknown"
    
    message = (
        f"👤 Your Telegram Info:\n\n"
        f"🆔 User ID: {user_id}\n"
        f"👤 Username: @{username}\n"
        f"📝 Name: {first_name}\n\n"
        f"💡 To become admin, add this User ID to ADMIN_USER_IDS"
    )
    
    await update.message.reply_text(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and convert Google Maps links or coordinates to Waze"""
    global processed_messages
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    message_text = update.message.text
    
    # Add unique message ID to prevent duplicates
    message_id = update.message.message_id
    chat_id = update.effective_chat.id
    
    # Create unique message identifier with timestamp
    import time
    current_time = int(time.time())
    message_key = f"{chat_id}_{message_id}_{current_time}"
    
    # Check if message was already processed (within last 60 seconds)
    for old_key in list(processed_messages):
        if old_key.startswith(f"{chat_id}_{message_id}_"):
            old_time = int(old_key.split('_')[-1])
            if current_time - old_time < 60:  # Within 60 seconds
                print(f"⚠️ DUPLICATE message detected: {message_key}")
                return
    
    # Add to processed messages
    processed_messages.add(message_key)
    
    # Clean up old messages (keep only last 500 and remove old ones)
    if len(processed_messages) > 500:
        # Remove messages older than 5 minutes
        current_time = int(time.time())
        processed_messages = {key for key in processed_messages 
                           if current_time - int(key.split('_')[-1]) < 300}
    
    print(f"🔍 MESSAGE received from user {user_id} (msg_id: {message_id}): {message_text[:50]}...")
    
    # Get user info for analytics
    user_info = {
        "username": update.effective_user.username,
        "first_name": update.effective_user.first_name,
        "last_name": update.effective_user.last_name,
        "is_bot": update.effective_user.is_bot
    }
    
    # Track request with timing
    start_time = time.time()
    
    # Track analytics
    if ANALYTICS_AVAILABLE and analytics:
        analytics.track_user_interaction(user_id, "message_received", True, {"message_length": len(message_text)}, user_info)
    
    # Send initial "typing" indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Initialize processing message variable
    processing_msg = None
    
    # Send processing message for longer operations
    if any(keyword in message_text.lower() for keyword in ['maps.google.com', 'goo.gl', 'maps.app.goo.gl']):
        processing_msg = await update.message.reply_text(get_text('processing', lang))
    
    # Extract coordinates from input (URL or direct coordinates)
    lat, lng = extract_coordinates_from_input(message_text)
    
    print(f"🔍 EXTRACTED coordinates: lat={lat}, lng={lng}")
    
    if lat is None or lng is None:
        # Track failed processing
        if ANALYTICS_AVAILABLE and analytics:
            analytics.track_link_processing(user_id, message_text, False, error="No coordinates found")
        
        # Track failed request
        if ANALYTICS_AVAILABLE and analytics:
            response_time = time.time() - start_time
            analytics.track_request(user_id, "coordinate_extraction", message_text, response_time, False, user_info)
        
        # Check if it's a Google Maps URL that couldn't be processed
        if 'maps.google.com' in message_text or 'goo.gl' in message_text or 'maps.app.goo.gl' in message_text:
            error_message = get_text('error_google_maps', lang)
        else:
            error_message = get_text('error_general', lang)
        
        # Edit processing message if it was sent, otherwise send new message
        if processing_msg is not None:
            try:
                await processing_msg.edit_text(error_message)
            except:
                # Fallback to sending new message if edit fails
                await update.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)
        return
    
    # Track successful processing
    if ANALYTICS_AVAILABLE and analytics:
        analytics.track_link_processing(user_id, message_text, True, coordinates=(lat, lng))
    
    # Generate Waze link
    waze_url = generate_waze_link(lat, lng)
    
    response_message = get_text('coordinates_extracted', lang, lat=lat, lng=lng, waze_url=waze_url)
    
    # Edit processing message if it was sent, otherwise send new message
    if processing_msg is not None:
        try:
            await processing_msg.edit_text(response_message)
        except:
            # Fallback to sending new message if edit fails
            await update.message.reply_text(response_message)
    else:
        await update.message.reply_text(response_message)
    
    # Track request completion
    if ANALYTICS_AVAILABLE and analytics:
        response_time = time.time() - start_time
        analytics.track_request(user_id, "coordinate_extraction", message_text, response_time, True, user_info)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle health check requests and analytics"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == "/" or path == "/health":
                # Health check
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
            elif path == "/admin":
                # Admin panel - check user ID from query parameter
                self.handle_admin_access(parsed_path.query)
            elif path == "/admin/api/stats":
                # Admin API - check user ID from query parameter
                self.handle_admin_api_access(parsed_path.query, "stats")
            elif path == "/admin/api/user":
                # Admin API - check user ID from query parameter
                self.handle_admin_api_access(parsed_path.query, "user")
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def do_POST(self):
        """Handle webhook POST requests from Telegram"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == "/webhook":
                # Handle Telegram webhook
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # Process the update
                import json
                update_data = json.loads(post_data.decode('utf-8'))
                
                # Create Update object and process it
                from telegram import Update
                update = Update.de_json(update_data, application.bot)
                
                # Process the update asynchronously
                import asyncio
                asyncio.run(application.process_update(update))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            self.send_error(500, f"Webhook Error: {str(e)}")
    

    
    def handle_admin_access(self, query):
        """Handle admin panel access with user ID verification"""
        try:
            params = urllib.parse.parse_qs(query)
            user_id = params.get('user_id', [None])[0]
            
            if not user_id or not is_admin_user(int(user_id)):
                self.send_error(403, "Access denied. Admin privileges required.")
                return
            
            self.send_analytics_page()
            
        except Exception as e:
            self.send_error(500, f"Error accessing admin panel: {str(e)}")
    
    def handle_admin_api_access(self, query, api_type):
        """Handle admin API access with user ID verification"""
        try:
            params = urllib.parse.parse_qs(query)
            user_id = params.get('user_id', [None])[0]
            
            if not user_id or not is_admin_user(int(user_id)):
                self.send_error(403, "Access denied. Admin privileges required.")
                return
            
            if api_type == "stats":
                self.send_json_stats()
            elif api_type == "user":
                self.send_user_stats(query)
            else:
                self.send_error(404, "API endpoint not found")
                
        except Exception as e:
            self.send_error(500, f"Error accessing admin API: {str(e)}")
    
    def send_analytics_page(self):
        """Send the analytics HTML page"""
        try:
            # Import the HTML content directly
            html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bot Analytics Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .content {
            padding: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-2px);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .user-search {
            margin-bottom: 20px;
        }
        .user-search input {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            width: 200px;
            margin-right: 10px;
        }
        .user-search button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .back-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
        }
        .back-btn:hover {
            background: #5a6268;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Admin Analytics Dashboard</h1>
            <p>Secure admin panel - Real-time statistics and insights</p>
        </div>
        
        <div class="content">
            <button class="back-btn" onclick="window.close()">🔙 Close</button>
            <button class="refresh-btn" onclick="loadStats()">🔄 Refresh Data</button>
            
            <div class="user-search">
                <input type="number" id="userSearch" placeholder="Enter User ID">
                <button onclick="loadUserStats()">Search User</button>
            </div>
            
            <div id="statsContainer">
                <div class="loading">Loading statistics...</div>
            </div>
        </div>
    </div>

    <script>
        function loadStats() {
            document.getElementById('statsContainer').innerHTML = '<div class="loading">Loading statistics...</div>';
            
            // Get user_id from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const userId = urlParams.get('user_id');
            
            fetch('/admin/api/stats?user_id=' + userId)
                .then(response => response.json())
                .then(data => {
                    displayStats(data);
                })
                .catch(error => {
                    document.getElementById('statsContainer').innerHTML = 
                        '<div class="error">Error loading statistics: ' + error.message + '</div>';
                });
        }
        
        function loadUserStats() {
            const searchUserId = document.getElementById('userSearch').value;
            if (!searchUserId) {
                alert('Please enter a User ID');
                return;
            }
            
            // Get admin user_id from URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const adminUserId = urlParams.get('user_id');
            
            fetch('/admin/api/user?user_id=' + adminUserId + '&search_user_id=' + searchUserId)
                .then(response => response.json())
                .then(data => {
                    displayUserStats(data);
                })
                .catch(error => {
                    alert('Error loading user statistics: ' + error.message);
                });
        }
        
        function displayStats(data) {
            const container = document.getElementById('statsContainer');
            
            let html = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${data.total_users || 0}</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.total_interactions || 0}</div>
                        <div class="stat-label">Total Interactions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.request_stats?.total_requests || 0}</div>
                        <div class="stat-label">Total Requests</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.success_rate || 0}%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.request_stats?.avg_response_time || 0}s</div>
                        <div class="stat-label">Avg Response Time</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${data.uptime || 'Unknown'}</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Link Processing Statistics</div>
                    <p><strong>Total:</strong> ${data.link_processing?.total || 0}</p>
                    <p><strong>Successful:</strong> ${data.link_processing?.successful || 0}</p>
                    <p><strong>Failed:</strong> ${data.link_processing?.failed || 0}</p>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Request Statistics</div>
                    <p><strong>Total Requests:</strong> ${data.request_stats?.total_requests || 0}</p>
                    <p><strong>Average Response Time:</strong> ${data.request_stats?.avg_response_time || 0}s</p>
                    <h4>Requests by Type:</h4>
                    <ul>
                        ${Object.entries(data.request_stats?.by_type || {}).map(([type, stats]) => 
                            `<li><strong>${type}:</strong> ${stats.count} (${stats.successful} successful, ${stats.failed} failed, avg: ${stats.avg_response_time}s)</li>`
                        ).join('')}
                    </ul>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Top Commands</div>
                    <ul>
            `;
            
            if (data.top_commands) {
                for (const [command, count] of Object.entries(data.top_commands)) {
                    html += `<li><strong>${command}:</strong> ${count}</li>`;
                }
            }
            
            html += `
                    </ul>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Language Distribution</div>
                    <ul>
            `;
            
            if (data.language_distribution) {
                for (const [lang, count] of Object.entries(data.language_distribution)) {
                    html += `<li><strong>${lang}:</strong> ${count}</li>`;
                }
            }
            
            html += `
                    </ul>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Recent Activity (Last 7 Days)</div>
            `;
            
            if (data.recent_activity) {
                for (const day of data.recent_activity) {
                    html += `
                        <p><strong>${day.date}:</strong> ${day.stats.total_interactions} interactions, 
                        ${day.stats.unique_users.length} unique users</p>
                    `;
                }
            }
            
            html += '</div>';
            
            container.innerHTML = html;
        }
        
        function displayUserStats(userData) {
            if (!userData) {
                alert('User not found');
                return;
            }
            
            const container = document.getElementById('statsContainer');
            container.innerHTML = `
                <div class="chart-container">
                    <div class="chart-title">User Statistics</div>
                    <p><strong>User ID:</strong> ${searchUserId}</p>
                    <p><strong>Username:</strong> ${userData.user_info?.username || 'N/A'}</p>
                    <p><strong>Name:</strong> ${userData.user_info?.first_name || ''} ${userData.user_info?.last_name || ''}</p>
                    <p><strong>First Seen:</strong> ${userData.first_seen}</p>
                    <p><strong>Last Seen:</strong> ${userData.last_seen}</p>
                    <p><strong>Total Interactions:</strong> ${userData.total_interactions}</p>
                    <p><strong>Successful Interactions:</strong> ${userData.successful_interactions}</p>
                    <p><strong>Failed Interactions:</strong> ${userData.failed_interactions}</p>
                    <p><strong>Language:</strong> ${userData.language}</p>
                    
                    <h3>Actions:</h3>
                    <ul>
                        ${Object.entries(userData.actions || {}).map(([action, count]) => 
                            `<li><strong>${action}:</strong> ${count}</li>`
                        ).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Load stats on page load
        window.onload = loadStats;
    </script>
</body>
</html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error loading analytics: {str(e)}")
    
    def send_json_stats(self):
        """Send JSON statistics"""
        try:
            from analytics import BotAnalytics
            analytics = BotAnalytics()
            stats = analytics.get_global_stats()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error getting stats: {str(e)}")
    
    def send_user_stats(self, query):
        """Send user-specific statistics"""
        try:
            from analytics import BotAnalytics
            params = urllib.parse.parse_qs(query)
            search_user_id = params.get('search_user_id', [None])[0]
            
            if not search_user_id:
                self.send_error(400, "Search User ID required")
                return
            
            analytics = BotAnalytics()
            user_stats = analytics.get_user_stats(int(search_user_id))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(user_stats, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error getting user stats: {str(e)}")
    

    
    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

def run_http_server():
    """Run HTTP server for health checks and analytics"""
    port = int(os.getenv('PORT', 8081))
    server = HTTPServer(('', port), HealthCheckHandler)
    print(f"🌐 HTTP server started on port {port}")
    
    # Start a background thread to ping health check periodically
    def ping_health_check():
        import time
        import requests
        while True:
            try:
                requests.get(f'http://localhost:{port}/health', timeout=5)
                print(f"💓 Internal health check ping at {time.strftime('%H:%M:%S')}")
                time.sleep(15)  # Ping every 15 seconds for more aggressive keep-alive
            except Exception as e:
                print(f"⚠️ Internal health check failed: {e}")
                time.sleep(15)
    
    # Start a background thread to ping external health check (disabled due to SSL issues)
    def ping_external_health():
        import time
        while True:
            try:
                # Just log that we're alive, don't make external requests
                print(f"💚 Bot is alive at {time.strftime('%H:%M:%S')}")
                time.sleep(60)  # Log every minute
            except Exception as e:
                print(f"⚠️ Health check error: {e}")
                time.sleep(60)
    
    import threading
    ping_thread = threading.Thread(target=ping_health_check, daemon=True)
    ping_thread.start()
    
    external_ping_thread = threading.Thread(target=ping_external_health, daemon=True)
    external_ping_thread.start()
    
    server.serve_forever()

def main():
    """Start the bot"""
    import signal
    import sys
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Received shutdown signal. Stopping bot gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: Bot token not found!")
        print("Set the TELEGRAM_BOT_TOKEN environment variable")
        print("Example: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        # For Cloud Run, just start the HTTP server without the bot
        print("Starting HTTP server only for Cloud Run health checks...")
        run_http_server()
        return
    
    # Start HTTP server in a separate thread for Cloud Run health checks (only if not in production)
    if os.getenv('ENVIRONMENT') != 'production':
        http_thread = threading.Thread(target=run_http_server, daemon=True)
        http_thread.start()
    
    # Create the Application with better error handling and unique identifier
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Use polling for both local and Cloud Run (simpler and more reliable)
    print("🤖 Bot started with polling!")
    
    # Add a small delay to reduce conflicts between instances
    import time
    import random
    time.sleep(random.uniform(0, 2))
    
    # Set bot name (skip for now to avoid conflicts)
    print("🤖 Bot name will be set during polling")
    
    # Clear any existing webhook to avoid conflicts
    print("🔄 Webhook will be cleared during polling")
    
    # Start polling with simple approach
    print("🚀 Starting bot polling...")
    
    # Use polling for stable operation
    print("🔄 Starting bot with polling...")
    
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
            bootstrap_retries=3,
            read_timeout=10,
            write_timeout=10,
            connect_timeout=10,
            pool_timeout=10,
            poll_interval=1.0,
            timeout=10
        )
    except Exception as e:
        print(f"❌ Polling failed: {e}")
        print("🔄 Starting HTTP server only...")
        run_http_server()

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    lang = get_user_language(user_id)
    
    # Create unique callback identifier to prevent duplicates
    callback_id = f"{user_id}_{query.id}_{query.data}"
    
    print(f"🔘 BUTTON callback received: {query.data} from user {user_id} (id: {query.id})")
    
    # Check if this callback was already processed
    if hasattr(context, 'processed_callbacks'):
        if callback_id in context.processed_callbacks:
            print(f"⚠️ DUPLICATE callback detected: {callback_id}")
            return
    else:
        context.processed_callbacks = set()
    
    # Add to processed callbacks
    context.processed_callbacks.add(callback_id)
    
    # Clean up old callbacks (keep only last 50)
    if len(context.processed_callbacks) > 50:
        context.processed_callbacks = set(list(context.processed_callbacks)[-25:])
    
    # Try to answer callback query, but don't fail if it's too old
    try:
        await query.answer()
    except Exception as e:
        print(f"⚠️ Could not answer callback query: {e}")
        # If callback is too old or invalid, ignore it completely
        if "Query is too old" in str(e) or "400 Bad Request" in str(e):
            print(f"⚠️ Ignoring old/invalid callback: {callback_id}")
            return
    
    # Track analytics
    if ANALYTICS_AVAILABLE and analytics:
        analytics.track_user_interaction(user_id, f"button_{query.data}", True)
    
    # Process the callback based on data
    try:
        if query.data == 'menu':
            menu_text = get_text('menu', lang)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=menu_text,
                reply_markup=create_menu_keyboard(lang)
            )
            print(f"✅ Menu sent for user {user_id}")
        
        elif query.data == 'help':
            help_text = get_text('help', lang)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=help_text,
                reply_markup=create_menu_keyboard(lang)
            )
            print(f"✅ Help sent for user {user_id}")
        
        elif query.data == 'language':
            language_text = get_text('language_menu', lang)
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=language_text,
                reply_markup=create_language_keyboard()
            )
            print(f"✅ Language menu sent for user {user_id}")
        
        elif query.data.startswith('lang_'):
            selected_lang = query.data.replace('lang_', '')
            if is_valid_language(selected_lang):
                save_user_language(user_id, selected_lang)
                
                # Track language change
                if ANALYTICS_AVAILABLE and analytics:
                    analytics.track_language_change(user_id, selected_lang)
                
                language_name = get_language_name(selected_lang)
                success_message = get_text('language_changed', selected_lang, language=language_name)
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=success_message,
                    reply_markup=create_menu_keyboard(selected_lang)
                )
                print(f"✅ Language changed to {selected_lang} for user {user_id}")
    
    except Exception as e:
        print(f"❌ Error processing button callback: {e}")
        print(f"❌ Callback data: {query.data}")
        print(f"❌ User ID: {user_id}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    print(f"❌ Error: {context.error}")
    print(f"❌ Error type: {type(context.error)}")
    print(f"❌ Update: {update}")
    
    # Handle different types of updates
    if update and hasattr(update, 'message') and update.message:
        user_id = update.message.from_user.id
        lang = get_user_language(user_id)
        error_message = get_text('error_processing', lang)
        await update.message.reply_text(error_message)
    elif update and hasattr(update, 'callback_query') and update.callback_query:
        user_id = update.callback_query.from_user.id
        lang = get_user_language(user_id)
        error_message = get_text('error_processing', lang)
        try:
            await update.callback_query.message.reply_text(error_message)
        except Exception as e:
            print(f"❌ Could not send error message to callback query: {e}")

if __name__ == '__main__':
    main()