#!/usr/bin/env python3
"""
Secure Bot Statistics Viewer
Usage: python secure_stats_viewer.py [--admin USER_ID] [--public] [--cleanup]
"""

import argparse
import json
import os
from datetime import datetime
from analytics_security import analytics_security

def view_public_stats():
    """View public statistics (no personal data)"""
    stats = analytics_security.get_public_stats()
    
    print("📊 Public Bot Statistics")
    print("=" * 50)
    print(f"📈 Total Requests: {stats['total_requests']:,}")
    print(f"✅ Successful Conversions: {stats['successful_conversions']:,}")
    print(f"📊 Success Rate: {stats['success_rate']}%")
    print(f"🕒 Last Updated: {stats['last_updated'][:19]}")
    
    print("\n🎯 Format Distribution:")
    for format_type, count in stats['format_distribution'].items():
        print(f"• {format_type.replace('_', ' ').title()}: {count:,}")
    
    print("\n🔧 API Usage:")
    for api_type, count in stats['api_usage'].items():
        print(f"• {api_type.replace('_', ' ').title()}: {count:,}")
    
    print("\n⚠️  Note: This is public data. Personal information is not included.")

def view_admin_stats(user_id: str):
    """View full statistics for admin users"""
    if not analytics_security.is_admin(user_id):
        print("❌ Access denied. You are not authorized to view admin statistics.")
        print("💡 Contact the bot owner to get admin access.")
        return
    
    stats = analytics_security.get_admin_stats(user_id)
    if not stats:
        print("❌ Failed to load admin statistics.")
        return
    
    print("🔐 Admin Bot Statistics")
    print("=" * 50)
    print(f"📈 Total Requests: {stats['total_requests']:,}")
    print(f"✅ Successful Conversions: {stats['successful_conversions']:,}")
    print(f"❌ Failed Conversions: {stats['failed_conversions']:,}")
    print(f"📊 Success Rate: {stats['success_rate']}%")
    
    print("\n📅 Recent Activity:")
    for day in stats['daily_stats']:
        print(f"• {day['date']}: {day['requests']} requests ({day['successful']} successful)")
    
    print("\n👥 Top Users:")
    for i, user in enumerate(stats['top_users'][:10], 1):
        success_rate = round((user['successful_requests'] / user['total_requests']) * 100, 2) if user['total_requests'] > 0 else 0
        print(f"{i}. {user['user_name']}: {user['total_requests']} requests ({success_rate}% success)")
    
    if stats['error_distribution']:
        print("\n❌ Error Distribution:")
        for error, count in stats['error_distribution'].items():
            print(f"• {error}: {count}")
    
    print(f"\n🔐 Admin access granted to user: {user_id}")

def export_anonymized_data():
    """Export anonymized data for public sharing"""
    from analytics import analytics
    
    # Get full data
    data = analytics.analytics_data.copy()
    
    # Anonymize user data
    anonymized_data = analytics_security.anonymize_user_data(data)
    
    # Save anonymized data
    with open('anonymized_analytics.json', 'w', encoding='utf-8') as f:
        json.dump(anonymized_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Anonymized data exported to 'anonymized_analytics.json'")
    print("🔒 All personal information has been removed.")

def cleanup_old_data():
    """Clean up old data based on retention policy"""
    analytics_security.cleanup_old_data()

def main():
    parser = argparse.ArgumentParser(description='Secure bot statistics viewer')
    parser.add_argument('--admin', type=str, help='Admin user ID for full access')
    parser.add_argument('--public', action='store_true', help='View public statistics only')
    parser.add_argument('--export-anonymized', action='store_true', help='Export anonymized data')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old data')
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_old_data()
        return
    
    if args.export_anonymized:
        export_anonymized_data()
        return
    
    if args.admin:
        view_admin_stats(args.admin)
    elif args.public:
        view_public_stats()
    else:
        # Default to public view
        view_public_stats()
        print("\n💡 Use --admin USER_ID for full access or --public for public stats only")

if __name__ == "__main__":
    main() 