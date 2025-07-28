#!/usr/bin/env python3
"""
Step-by-step debug script for coordinate extraction
"""

import sys
import os
import re
import urllib.parse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from maps_to_waze_bot import extract_coordinates_from_google_maps

def debug_step_by_step():
    """Debug coordinate extraction step by step"""
    
    # The problematic URL
    expanded_url = "https://consent.google.com/m?continue=https://www.google.com/maps/search/59.286887,%2B24.648914?entry%3Dtts%26g_ep%3DEgoyMDI1MDcyMy4wIPu8ASoASAFQAw%253D%253D%26skid%3D7cce9fe9-2a17-4387-8239-bbb86210f4c5&gl=EE&m=0&pc=m&uxe=eomtm&cm=2&hl=et&src=1"
    
    print("🔍 Step-by-step debugging...")
    print(f"URL: {expanded_url}")
    print("=" * 80)
    
    # Step 1: Check @ pattern
    print("1️⃣ Checking @ pattern...")
    coords_pattern = r'@(-?\d+\.?\d*),(-?\d+\.?\d*)'
    match = re.search(coords_pattern, expanded_url)
    if match:
        lat, lng = match.groups()
        print(f"   Found: {lat}, {lng}")
    else:
        print("   No @ pattern found")
    
    # Step 2: Check !3d!4d pattern
    print("\n2️⃣ Checking !3d!4d pattern...")
    coords_3d4d_pattern = r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)'
    match = re.search(coords_3d4d_pattern, expanded_url)
    if match:
        lat, lng = match.groups()
        print(f"   Found: {lat}, {lng}")
    else:
        print("   No !3d!4d pattern found")
    
    # Step 3: Check search path
    print("\n3️⃣ Checking search path...")
    search_coords_pattern = r'search/([^?]+)'
    search_match = re.search(search_coords_pattern, expanded_url)
    if search_match:
        search_data = search_match.group(1)
        print(f"   Search data: {search_data}")
        
        decoded_data = urllib.parse.unquote(search_data)
        print(f"   Decoded search: {decoded_data}")
        
        coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', decoded_data)
        if coords_match:
            lat, lng = coords_match.groups()
            print(f"   Found in decoded: {lat}, {lng}")
        else:
            print("   No coordinates in decoded search")
    else:
        print("   No search path found")
    
    # Step 4: Check continue parameter
    print("\n4️⃣ Checking continue parameter...")
    continue_match = re.search(r'continue=([^&]+)', expanded_url)
    if continue_match:
        continue_data = continue_match.group(1)
        print(f"   Continue data: {continue_data}")
        
        decoded_continue = urllib.parse.unquote(continue_data)
        print(f"   Decoded continue: {decoded_continue}")
        
        # Try different patterns
        patterns = [
            r'(-?\d+\.?\d*),(-?\d+\.?\d*)',  # Standard
            r'(-?\d+\.?\d*),\+(-?\d+\.?\d*)',  # With plus
            r'(-?\d+\.?\d*),%2B(-?\d+\.?\d*)',  # URL encoded plus
        ]
        
        for i, pattern in enumerate(patterns, 1):
            coords_match = re.search(pattern, continue_data)
            if coords_match:
                lat, lng = coords_match.groups()
                print(f"   Pattern {i} in continue_data: {lat}, {lng}")
            
            coords_match = re.search(pattern, decoded_continue)
            if coords_match:
                lat, lng = coords_match.groups()
                print(f"   Pattern {i} in decoded_continue: {lat}, {lng}")
    else:
        print("   No continue parameter found")
    
    # Step 5: Check fallback pattern
    print("\n5️⃣ Checking fallback pattern...")
    coords_match = re.search(r'(-?\d+\.?\d*),(-?\d+\.?\d*)', expanded_url)
    if coords_match:
        lat, lng = coords_match.groups()
        print(f"   Found: {lat}, {lng}")
    else:
        print("   No fallback pattern found")
    
    # Step 6: Test the actual function
    print("\n6️⃣ Testing actual function...")
    result = extract_coordinates_from_google_maps(expanded_url)
    print(f"   Function result: {result}")

if __name__ == "__main__":
    debug_step_by_step() 