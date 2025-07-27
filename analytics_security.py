import os
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

class AnalyticsSecurity:
    def __init__(self):
        self.admin_users = self._load_admin_users()
        self.public_stats_enabled = False
        self.data_retention_days = 90  # Keep data for 90 days
        
    def _load_admin_users(self) -> List[str]:
        """Load admin users from environment or config"""
        admin_users = os.getenv('ANALYTICS_ADMIN_USERS', '')
        if admin_users:
            return [user.strip() for user in admin_users.split(',')]
        return []
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_users
    
    def get_public_stats(self) -> Dict:
        """Get public statistics (no personal data)"""
        from analytics import analytics
        
        stats = analytics.get_stats()
        
        # Return only public data
        public_data = {
            "total_requests": stats["total_requests"],
            "successful_conversions": stats["successful_conversions"],
            "success_rate": stats["success_rate"],
            "format_distribution": stats["format_distribution"],
            "api_usage": stats["api_usage"],
            "last_updated": datetime.now().isoformat()
        }
        
        return public_data
    
    def get_admin_stats(self, user_id: str) -> Optional[Dict]:
        """Get full statistics for admin users"""
        if not self.is_admin(user_id):
            return None
            
        from analytics import analytics
        return analytics.get_stats()
    
    def anonymize_user_data(self, data: Dict) -> Dict:
        """Anonymize user data for public viewing"""
        if "user_stats" in data:
            # Replace usernames with hashes
            for user_key, user_data in data["user_stats"].items():
                if "user_name" in user_data:
                    # Create hash of username
                    hash_name = hashlib.md5(user_data["user_name"].encode()).hexdigest()[:8]
                    user_data["user_name"] = f"User_{hash_name}"
                    user_data["user_id"] = "***"  # Hide user ID
        
        return data
    
    def cleanup_old_data(self):
        """Remove data older than retention period"""
        from analytics import analytics
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        
        # Clean up old daily stats
        old_dates = []
        for date_str in analytics.analytics_data["daily_stats"]:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj < cutoff_date:
                    old_dates.append(date_str)
            except:
                pass
        
        for old_date in old_dates:
            del analytics.analytics_data["daily_stats"][old_date]
        
        # Clean up old user data
        old_users = []
        for user_key, user_data in analytics.analytics_data["user_stats"].items():
            if "last_seen" in user_data:
                try:
                    last_seen = datetime.fromisoformat(user_data["last_seen"])
                    if last_seen < cutoff_date:
                        old_users.append(user_key)
                except:
                    pass
        
        for old_user in old_users:
            del analytics.analytics_data["user_stats"][old_user]
        
        analytics._save_analytics()
        print(f"🧹 Cleaned up data older than {self.data_retention_days} days")

# Global security instance
analytics_security = AnalyticsSecurity() 