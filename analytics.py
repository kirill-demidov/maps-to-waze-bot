#!/usr/bin/env python3
"""
Analytics system for the Telegram bot
Tracks user interactions, link processing, and usage statistics
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class BotAnalytics:
    def __init__(self, data_file: str = "analytics_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
        
    def _load_data(self) -> Dict[str, Any]:
        """Load analytics data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
        
        # Return default structure
        return {
            "users": {},
            "daily_stats": {},
            "link_processing": {
                "successful": 0,
                "failed": 0,
                "total": 0
            },
            "commands": {},
            "languages": {},
            "start_time": datetime.now().isoformat()
        }
    
    def _save_data(self):
        """Save analytics data to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
    
    def track_user_interaction(self, user_id: int, action: str, success: bool = True, 
                             additional_data: Optional[Dict] = None, user_info: Optional[Dict] = None):
        """Track user interaction"""
        try:
            user_id_str = str(user_id)
            current_time = datetime.now().isoformat()
            
            # Initialize user data if not exists
            if user_id_str not in self.data["users"]:
                self.data["users"][user_id_str] = {
                    "first_seen": current_time,
                    "last_seen": current_time,
                    "total_interactions": 0,
                    "successful_interactions": 0,
                    "failed_interactions": 0,
                    "actions": {},
                    "language": "en",
                    "user_info": {}
                }
            
            # Update user info if provided
            if user_info:
                self.data["users"][user_id_str]["user_info"].update(user_info)
            
            # Update user stats
            user_data = self.data["users"][user_id_str]
            user_data["last_seen"] = current_time
            user_data["total_interactions"] += 1
            
            if success:
                user_data["successful_interactions"] += 1
            else:
                user_data["failed_interactions"] += 1
            
            # Track action
            if action not in user_data["actions"]:
                user_data["actions"][action] = 0
            user_data["actions"][action] += 1
            
            # Track command globally
            if action not in self.data["commands"]:
                self.data["commands"][action] = 0
            self.data["commands"][action] += 1
            
            # Track daily stats
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in self.data["daily_stats"]:
                self.data["daily_stats"][today] = {
                    "total_interactions": 0,
                    "unique_users": set(),
                    "successful_links": 0,
                    "failed_links": 0
                }
            
            self.data["daily_stats"][today]["total_interactions"] += 1
            self.data["daily_stats"][today]["unique_users"].add(user_id_str)
            
            # Convert set to list for JSON serialization
            self.data["daily_stats"][today]["unique_users"] = list(
                self.data["daily_stats"][today]["unique_users"]
            )
            
            # Store additional data if provided
            if additional_data:
                if "additional_data" not in user_data:
                    user_data["additional_data"] = []
                user_data["additional_data"].append({
                    "timestamp": current_time,
                    "action": action,
                    "data": additional_data
                })
            
            self._save_data()
            
        except Exception as e:
            logger.error(f"Error tracking user interaction: {e}")
    
    def track_link_processing(self, user_id: int, url: str, success: bool, 
                            coordinates: Optional[tuple] = None, error: Optional[str] = None):
        """Track link processing attempts"""
        try:
            # Track basic interaction
            action = "link_processing_success" if success else "link_processing_failed"
            additional_data = {
                "url": url,
                "coordinates": coordinates,
                "error": error
            }
            
            self.track_user_interaction(user_id, action, success, additional_data)
            
            # Update global link processing stats
            self.data["link_processing"]["total"] += 1
            if success:
                self.data["link_processing"]["successful"] += 1
                # Update daily stats
                today = datetime.now().strftime("%Y-%m-%d")
                if today in self.data["daily_stats"]:
                    self.data["daily_stats"][today]["successful_links"] += 1
            else:
                self.data["link_processing"]["failed"] += 1
                # Update daily stats
                today = datetime.now().strftime("%Y-%m-%d")
                if today in self.data["daily_stats"]:
                    self.data["daily_stats"][today]["failed_links"] += 1
            
            self._save_data()
            
        except Exception as e:
            logger.error(f"Error tracking link processing: {e}")
    
    def track_language_change(self, user_id: int, language: str):
        """Track language preference changes"""
        try:
            user_id_str = str(user_id)
            
            # Update user language
            if user_id_str in self.data["users"]:
                self.data["users"][user_id_str]["language"] = language
            
            # Track global language usage
            if language not in self.data["languages"]:
                self.data["languages"][language] = 0
            self.data["languages"][language] += 1
            
            self.track_user_interaction(user_id, "language_change", True, {"language": language})
            
        except Exception as e:
            logger.error(f"Error tracking language change: {e}")
    
    def track_request(self, user_id: int, request_type: str, request_data: str, 
                     response_time: float = None, success: bool = True, user_info: Optional[Dict] = None):
        """Track individual requests with detailed information"""
        try:
            current_time = datetime.now().isoformat()
            
            # Initialize requests tracking if not exists
            if "requests" not in self.data:
                self.data["requests"] = {
                    "total": 0,
                    "by_type": {},
                    "response_times": [],
                    "recent_requests": []
                }
            
            # Update request stats
            self.data["requests"]["total"] += 1
            
            if request_type not in self.data["requests"]["by_type"]:
                self.data["requests"]["by_type"][request_type] = {
                    "count": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_response_time": 0
                }
            
            self.data["requests"]["by_type"][request_type]["count"] += 1
            if success:
                self.data["requests"]["by_type"][request_type]["successful"] += 1
            else:
                self.data["requests"]["by_type"][request_type]["failed"] += 1
            
            # Track response time
            if response_time is not None:
                self.data["requests"]["response_times"].append(response_time)
                # Keep only last 1000 response times
                if len(self.data["requests"]["response_times"]) > 1000:
                    self.data["requests"]["response_times"] = self.data["requests"]["response_times"][-1000:]
                
                # Update average response time
                avg_time = sum(self.data["requests"]["response_times"]) / len(self.data["requests"]["response_times"])
                self.data["requests"]["by_type"][request_type]["avg_response_time"] = round(avg_time, 3)
            
            # Track recent requests (last 100)
            recent_request = {
                "timestamp": current_time,
                "user_id": user_id,
                "type": request_type,
                "data": request_data[:100] + "..." if len(request_data) > 100 else request_data,
                "response_time": response_time,
                "success": success
            }
            
            self.data["requests"]["recent_requests"].append(recent_request)
            # Keep only last 100 requests
            if len(self.data["requests"]["recent_requests"]) > 100:
                self.data["requests"]["recent_requests"] = self.data["requests"]["recent_requests"][-100:]
            
            # Track user interaction with request info
            action = f"request_{request_type}"
            additional_data = {
                "request_data": request_data,
                "response_time": response_time,
                "success": success
            }
            
            self.track_user_interaction(user_id, action, success, additional_data, user_info)
            
        except Exception as e:
            logger.error(f"Error tracking request: {e}")
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get statistics for a specific user"""
        try:
            user_id_str = str(user_id)
            if user_id_str in self.data["users"]:
                return self.data["users"][user_id_str]
            return None
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics"""
        try:
            total_users = len(self.data["users"])
            total_interactions = sum(
                user["total_interactions"] for user in self.data["users"].values()
            )
            
            # Calculate success rate
            total_successful = sum(
                user["successful_interactions"] for user in self.data["users"].values()
            )
            success_rate = (total_successful / total_interactions * 100) if total_interactions > 0 else 0
            
            # Get recent activity (last 7 days)
            recent_days = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                if date in self.data["daily_stats"]:
                    recent_days.append({
                        "date": date,
                        "stats": self.data["daily_stats"][date]
                    })
            
            # Get request statistics
            request_stats = {}
            if "requests" in self.data:
                request_stats = {
                    "total_requests": self.data["requests"]["total"],
                    "by_type": self.data["requests"]["by_type"],
                    "avg_response_time": round(
                        sum(self.data["requests"]["response_times"]) / len(self.data["requests"]["response_times"]), 3
                    ) if self.data["requests"]["response_times"] else 0,
                    "recent_requests": self.data["requests"]["recent_requests"][-20:]  # Last 20 requests
                }
            
            return {
                "total_users": total_users,
                "total_interactions": total_interactions,
                "success_rate": round(success_rate, 2),
                "link_processing": self.data["link_processing"],
                "top_commands": dict(sorted(
                    self.data["commands"].items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]),
                "language_distribution": self.data["languages"],
                "recent_activity": recent_days,
                "request_stats": request_stats,
                "uptime": self._calculate_uptime()
            }
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            return {}
    
    def _calculate_uptime(self) -> str:
        """Calculate bot uptime"""
        try:
            start_time = datetime.fromisoformat(self.data["start_time"])
            uptime = datetime.now() - start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m"
        except Exception:
            return "Unknown"
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old analytics data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up daily stats
            dates_to_remove = []
            for date_str in self.data["daily_stats"]:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj < cutoff_date:
                    dates_to_remove.append(date_str)
            
            for date_str in dates_to_remove:
                del self.data["daily_stats"][date_str]
            
            # Clean up user additional data (keep only last 50 entries per user)
            for user_data in self.data["users"].values():
                if "additional_data" in user_data and len(user_data["additional_data"]) > 50:
                    user_data["additional_data"] = user_data["additional_data"][-50:]
            
            self._save_data()
            logger.info(f"Cleaned up analytics data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up analytics data: {e}")

# Global analytics instance
analytics = BotAnalytics() 