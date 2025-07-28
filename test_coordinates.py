#!/usr/bin/env python3
"""
Test script for coordinate extraction from Google Maps URLs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from maps_to_waze_bot import extract_coordinates_from_input

def test_coordinate_extraction():
    """Test coordinate extraction from various URL formats"""
    
    test_urls = [
        "https://maps.app.goo.gl/7Kbykswh6r89ybX78",
        "40.7128, -74.0060",
        "31°44'49.8\"N 35°01'46.6\"E",
        "https://www.google.com/maps/place/New+York+City,+NY,+USA/@40.7128,-74.0060,15z",
        "https://maps.google.com/?q=40.7128,-74.0060",
        "https://maps.google.com/maps?ll=40.7128,-74.0060&z=15"
    ]
    
    print("🧪 Testing coordinate extraction...")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        try:
            lat, lng = extract_coordinates_from_input(url)
            if lat is not None and lng is not None:
                print(f"✅ SUCCESS: {lat}, {lng}")
                waze_url = f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"
                print(f"🔗 Waze URL: {waze_url}")
            else:
                print("❌ FAILED: No coordinates found")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    test_coordinate_extraction() 