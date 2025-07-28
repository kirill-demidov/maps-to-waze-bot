#!/usr/bin/env python3
"""
Development script for running the bot locally
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from env.local file
load_dotenv('env.local')

# Set default values for development
if not os.getenv('TELEGRAM_BOT_TOKEN'):
    print("⚠️  Warning: TELEGRAM_BOT_TOKEN not set!")
    print("Please set your bot token in env.local file")
    print("You can get it from @BotFather on Telegram")
    sys.exit(1)

if not os.getenv('ADMIN_USER_IDS'):
    print("⚠️  Warning: ADMIN_USER_IDS not set!")
    print("Please set your Telegram user ID in env.local file")
    print("You can get it by sending /myid to the bot")

# Set development port
os.environ['PORT'] = '8081'

print("🚀 Starting bot in development mode...")
print(f"📱 Bot Token: {'*' * 10}{os.getenv('TELEGRAM_BOT_TOKEN')[-4:]}")
print(f"🔧 Admin IDs: {os.getenv('ADMIN_USER_IDS', 'Not set')}")
print(f"🌐 HTTP Port: {os.getenv('PORT', '8081')}")
print(f"🗺️  Google Maps API: {'Available' if os.getenv('GOOGLE_MAPS_API_KEY') else 'Not configured'}")

# Import and run the bot
from maps_to_waze_bot import main

if __name__ == "__main__":
    main() 