#!/usr/bin/env python3
"""
Debug script for coordinate extraction with detailed logging
"""

import sys
import os
import logging
import requests
import urllib.parse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from maps_to_waze_bot import (
    extract_coordinates_from_input,
    expand_short_url,
    extract_coordinates_from_google_maps,
    extract_place_id_from_url
)

def debug_url_processing(url):
    """Debug URL processing step by step"""
    print(f"\n🔍 DEBUGGING: {url}")
    print("=" * 60)
    
    # Step 1: Try to expand short URL
    print("1️⃣ Expanding short URL...")
    try:
        expanded_url = expand_short_url(url)
        print(f"   Expanded URL: {expanded_url}")
        if expanded_url != url:
            print("   ✅ URL was expanded")
        else:
            print("   ⚠️  URL was not expanded")
    except Exception as e:
        print(f"   ❌ Error expanding URL: {e}")
        expanded_url = url
    
    # Step 2: Try to extract place ID
    print("\n2️⃣ Extracting place ID...")
    try:
        place_id = extract_place_id_from_url(url)
        print(f"   Place ID: {place_id}")
        if place_id:
            print("   ✅ Place ID found")
        else:
            print("   ⚠️  No place ID found")
    except Exception as e:
        print(f"   ❌ Error extracting place ID: {e}")
    
    # Step 3: Try to extract coordinates from expanded URL
    print("\n3️⃣ Extracting coordinates from expanded URL...")
    try:
        coords = extract_coordinates_from_google_maps(expanded_url)
        print(f"   Coordinates: {coords}")
        if coords[0] is not None:
            print("   ✅ Coordinates found")
        else:
            print("   ⚠️  No coordinates found")
    except Exception as e:
        print(f"   ❌ Error extracting coordinates: {e}")
    
    # Step 4: Try the main extraction function
    print("\n4️⃣ Using main extraction function...")
    try:
        final_coords = extract_coordinates_from_input(url)
        print(f"   Final coordinates: {final_coords}")
        if final_coords[0] is not None:
            print("   ✅ SUCCESS: Coordinates extracted!")
            waze_url = f"https://waze.com/ul?ll={final_coords[0]},{final_coords[1]}&navigate=yes"
            print(f"   🔗 Waze URL: {waze_url}")
        else:
            print("   ❌ FAILED: No coordinates found")
    except Exception as e:
        print(f"   ❌ Error in main extraction: {e}")
    
    print("=" * 60)

def test_problematic_url():
    """Test the problematic URL that was failing"""
    problematic_url = "https://maps.app.goo.gl/7Kbykswh6r89ybX78"
    
    print("🧪 Testing problematic URL...")
    debug_url_processing(problematic_url)

def test_various_formats():
    """Test various URL formats"""
    test_urls = [
        "https://maps.app.goo.gl/7Kbykswh6r89ybX78",
        "40.7128, -74.0060",
        "31°44'49.8\"N 35°01'46.6\"E",
        "https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z",
        "https://maps.google.com/?q=40.7128,-74.0060",
        "https://maps.google.com/maps?ll=40.7128,-74.0060&z=15"
    ]
    
    print("🧪 Testing various URL formats...")
    for url in test_urls:
        debug_url_processing(url)

if __name__ == "__main__":
    print("🐛 Coordinate Extraction Debug Tool")
    print("=" * 60)
    
    # Test the problematic URL
    test_problematic_url()
    
    # Test various formats
    test_various_formats()
    
    print("\n�� Debug completed!") 