#!/usr/bin/env python3
"""
Specific debug script for the coordinate parsing issue
"""

import re
import urllib.parse

def debug_coordinate_parsing():
    """Debug the specific coordinate parsing issue"""
    
    # The problematic URL
    expanded_url = "https://consent.google.com/m?continue=https://www.google.com/maps/search/59.286887,%2B24.648914?entry%3Dtts%26g_ep%3DEgoyMDI1MDcyMy4wIPu8ASoASAFQAw%253D%253D%26skid%3D7cce9fe9-2a17-4387-8239-bbb86210f4c5&gl=EE&m=0&pc=m&uxe=eomtm&cm=2&hl=et&src=1"
    
    print("🔍 Debugging coordinate parsing...")
    print(f"URL: {expanded_url}")
    print("=" * 80)
    
    # Extract continue parameter
    continue_match = re.search(r'continue=([^&]+)', expanded_url)
    if continue_match:
        continue_data = continue_match.group(1)
        print(f"Continue parameter: {continue_data}")
        
        # URL decode
        decoded_continue = urllib.parse.unquote(continue_data)
        print(f"Decoded continue: {decoded_continue}")
        
        # Try different patterns
        patterns = [
            r'(-?\d+\.?\d*),(-?\d+\.?\d*)',  # Standard format
            r'(-?\d+\.?\d*),\+(-?\d+\.?\d*)',  # With plus sign
            r'(-?\d+\.?\d*),%2B(-?\d+\.?\d*)',  # URL encoded plus
        ]
        
        for i, pattern in enumerate(patterns, 1):
            print(f"\nPattern {i}: {pattern}")
            matches = re.findall(pattern, continue_data)
            print(f"Matches in continue_data: {matches}")
            
            # Also try on decoded data
            decoded_matches = re.findall(pattern, decoded_continue)
            print(f"Matches in decoded_continue: {decoded_matches}")
            
            if matches:
                for match in matches:
                    lat, lng = match
                    print(f"  Found: lat={lat}, lng={lng}")
                    try:
                        lat_f, lng_f = float(lat), float(lng)
                        print(f"  Parsed: lat={lat_f}, lng={lng_f}")
                        if -90 <= lat_f <= 90 and -180 <= lng_f <= 180:
                            print(f"  ✅ Valid coordinates: {lat_f}, {lng_f}")
                        else:
                            print(f"  ❌ Invalid coordinate ranges")
                    except ValueError as e:
                        print(f"  ❌ Parse error: {e}")
    
    # Also try to extract from search path
    print("\n" + "=" * 80)
    print("Trying search path extraction...")
    
    search_pattern = r'search/([^?]+)'
    search_match = re.search(search_pattern, expanded_url)
    if search_match:
        search_data = search_match.group(1)
        print(f"Search data: {search_data}")
        
        decoded_search = urllib.parse.unquote(search_data)
        print(f"Decoded search: {decoded_search}")
        
        # Try patterns on search data
        for i, pattern in enumerate(patterns, 1):
            print(f"\nPattern {i} on search data: {pattern}")
            matches = re.findall(pattern, search_data)
            print(f"Matches in search_data: {matches}")
            
            decoded_matches = re.findall(pattern, decoded_search)
            print(f"Matches in decoded_search: {decoded_matches}")

if __name__ == "__main__":
    debug_coordinate_parsing() 