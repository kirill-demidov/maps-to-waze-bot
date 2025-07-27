import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

class BotAnalytics:
    def __init__(self, log_file="bot_analytics.json"):
        self.log_file = log_file
        self.analytics_data = self._load_analytics()
        
    def _load_analytics(self):
        """Load existing analytics data"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._create_default_analytics()
        return self._create_default_analytics()
    
    def _create_default_analytics(self):
        """Create default analytics structure"""
        return {
            "total_requests": 0,
            "successful_conversions": 0,
            "failed_conversions": 0,
            "daily_stats": {},
            "user_stats": {},
            "format_stats": {
                "google_maps_links": 0,
                "coordinates": 0,
                "dms_coordinates": 0,
                "unknown_format": 0
            },
            "error_stats": {},
            "api_usage": {
                "google_maps_api_calls": 0,
                "url_expansions": 0
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_analytics(self):
        """Save analytics data to file"""
        self.analytics_data["last_updated"] = datetime.now().isoformat()
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.analytics_data, f, indent=2, ensure_ascii=False)
    
    def log_request(self, user_id, user_name, input_text, success, error_type=None, format_type=None):
        """Log a bot request"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update total requests
        self.analytics_data["total_requests"] += 1
        
        # Update daily stats
        if today not in self.analytics_data["daily_stats"]:
            self.analytics_data["daily_stats"][today] = {
                "requests": 0,
                "successful": 0,
                "failed": 0
            }
        
        self.analytics_data["daily_stats"][today]["requests"] += 1
        
        # Update success/failure stats
        if success:
            self.analytics_data["successful_conversions"] += 1
            self.analytics_data["daily_stats"][today]["successful"] += 1
        else:
            self.analytics_data["failed_conversions"] += 1
            self.analytics_data["daily_stats"][today]["failed"] += 1
            
            # Log error type
            if error_type:
                if error_type not in self.analytics_data["error_stats"]:
                    self.analytics_data["error_stats"][error_type] = 0
                self.analytics_data["error_stats"][error_type] += 1
        
        # Update format stats
        if format_type:
            if format_type in self.analytics_data["format_stats"]:
                self.analytics_data["format_stats"][format_type] += 1
        
        # Update user stats
        user_key = f"{user_id}_{user_name}"
        if user_key not in self.analytics_data["user_stats"]:
            self.analytics_data["user_stats"][user_key] = {
                "user_id": user_id,
                "user_name": user_name,
                "total_requests": 0,
                "successful_requests": 0,
                "last_seen": None
            }
        
        self.analytics_data["user_stats"][user_key]["total_requests"] += 1
        self.analytics_data["user_stats"][user_key]["last_seen"] = datetime.now().isoformat()
        
        if success:
            self.analytics_data["user_stats"][user_key]["successful_requests"] += 1
        
        self._save_analytics()
    
    def log_api_usage(self, api_type):
        """Log API usage"""
        if api_type in self.analytics_data["api_usage"]:
            self.analytics_data["api_usage"][api_type] += 1
            self._save_analytics()
    
    def get_stats(self, days=7):
        """Get analytics statistics"""
        stats = {
            "total_requests": self.analytics_data["total_requests"],
            "successful_conversions": self.analytics_data["successful_conversions"],
            "failed_conversions": self.analytics_data["failed_conversions"],
            "success_rate": 0,
            "daily_stats": {},
            "top_users": [],
            "format_distribution": self.analytics_data["format_stats"],
            "error_distribution": self.analytics_data["error_stats"],
            "api_usage": self.analytics_data["api_usage"]
        }
        
        # Calculate success rate
        if stats["total_requests"] > 0:
            stats["success_rate"] = round((stats["successful_conversions"] / stats["total_requests"]) * 100, 2)
        
        # Get recent daily stats
        recent_days = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.analytics_data["daily_stats"]:
                recent_days.append({
                    "date": date,
                    **self.analytics_data["daily_stats"][date]
                })
        stats["daily_stats"] = recent_days
        
        # Get top users
        users = list(self.analytics_data["user_stats"].values())
        users.sort(key=lambda x: x["total_requests"], reverse=True)
        stats["top_users"] = users[:10]
        
        return stats
    
    def generate_report(self, days=7):
        """Generate a formatted analytics report"""
        stats = self.get_stats(days)
        
        report = f"""
📊 Bot Analytics Report
{'='*50}

📈 Overall Statistics:
• Total Requests: {stats['total_requests']:,}
• Successful Conversions: {stats['successful_conversions']:,}
• Failed Conversions: {stats['failed_conversions']:,}
• Success Rate: {stats['success_rate']}%

📅 Recent Activity ({days} days):
"""
        
        for day in stats['daily_stats']:
            report += f"• {day['date']}: {day['requests']} requests ({day['successful']} successful)\n"
        
        report += f"""
🎯 Format Distribution:
• Google Maps Links: {stats['format_distribution']['google_maps_links']:,}
• Coordinates: {stats['format_distribution']['coordinates']:,}
• DMS Coordinates: {stats['format_distribution']['dms_coordinates']:,}
• Unknown Format: {stats['format_distribution']['unknown_format']:,}

🔧 API Usage:
• Google Maps API Calls: {stats['api_usage']['google_maps_api_calls']:,}
• URL Expansions: {stats['api_usage']['url_expansions']:,}

👥 Top Users:
"""
        
        for i, user in enumerate(stats['top_users'][:5], 1):
            success_rate = round((user['successful_requests'] / user['total_requests']) * 100, 2) if user['total_requests'] > 0 else 0
            report += f"• {user['user_name']}: {user['total_requests']} requests ({success_rate}% success)\n"
        
        if stats['error_distribution']:
            report += "\n❌ Error Distribution:\n"
            for error, count in stats['error_distribution'].items():
                report += f"• {error}: {count}\n"
        
        return report

# Global analytics instance
analytics = BotAnalytics() 