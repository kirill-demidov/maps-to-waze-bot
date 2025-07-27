#!/usr/bin/env python3
"""
Main entry point for Cloud Run deployment
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the bot
from maps_to_waze_bot import main

if __name__ == "__main__":
    main() 