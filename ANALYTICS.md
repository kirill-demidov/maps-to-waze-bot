# 📊 Analytics & Statistics

## Overview

The Maps to Waze Bot includes a comprehensive analytics system to track usage, performance, and user behavior.

## 📈 Available Statistics

### Core Metrics
- **Total Requests** - Number of messages processed
- **Successful Conversions** - Successful Google Maps to Waze conversions
- **Failed Conversions** - Failed conversion attempts
- **Success Rate** - Percentage of successful conversions
- **Active Users** - Number of unique users

### Detailed Analytics
- **Daily Activity** - Requests per day with success/failure breakdown
- **Format Distribution** - Types of input formats used
- **User Statistics** - Individual user activity and success rates
- **Error Distribution** - Common error types and frequencies
- **API Usage** - Google Maps API calls and URL expansions

## 🔧 How to View Statistics

### 1. Command Line Interface

```bash
# View last 7 days (default)
python stats_viewer.py

# View last 30 days
python stats_viewer.py --days 30

# Get raw JSON data
python stats_viewer.py --json

# Generate HTML report
python stats_viewer.py --web
```

### 2. Google Cloud Logging

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=maps-to-waze-bot" --limit=50

# View logs for specific date
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=maps-to-waze-bot AND timestamp>=\"2024-07-27\"" --limit=100
```

### 3. Analytics Dashboard

The bot generates an HTML dashboard with:
- 📊 Real-time statistics
- 📅 Daily activity charts
- 👥 Top user analysis
- ❌ Error tracking
- 🎯 Format distribution

## 📁 Data Storage

### Analytics File
- **Location:** `bot_analytics.json`
- **Format:** JSON
- **Backup:** Stored in Google Cloud Storage (recommended)

### Data Structure
```json
{
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
  }
}
```

## 🚀 Integration with Bot

The analytics system is automatically integrated into the bot:

```python
from analytics import analytics

# Log a successful request
analytics.log_request(
    user_id=123456789,
    user_name="John Doe",
    input_text="https://maps.google.com/...",
    success=True,
    format_type="google_maps_links"
)

# Log API usage
analytics.log_api_usage("google_maps_api_calls")
```

## 📊 Sample Reports

### Text Report
```
📊 Bot Analytics Report
==================================================

📈 Overall Statistics:
• Total Requests: 1,234
• Successful Conversions: 1,180
• Failed Conversions: 54
• Success Rate: 95.6%

📅 Recent Activity (7 days):
• 2024-07-27: 45 requests (43 successful)
• 2024-07-26: 38 requests (36 successful)
• 2024-07-25: 52 requests (50 successful)

🎯 Format Distribution:
• Google Maps Links: 890
• Coordinates: 234
• DMS Coordinates: 110
• Unknown Format: 0

🔧 API Usage:
• Google Maps API Calls: 156
• URL Expansions: 234

👥 Top Users:
• John Doe: 45 requests (95.6% success)
• Jane Smith: 32 requests (96.9% success)
• Bob Wilson: 28 requests (92.9% success)
```

### HTML Dashboard
The web dashboard provides:
- Interactive charts and graphs
- Real-time data visualization
- Export capabilities
- Mobile-responsive design

## 🔒 Privacy & Data Protection

### Data Collected
- User ID and username (from Telegram)
- Request timestamps
- Success/failure status
- Input format type
- Error types (no personal data)

### Data NOT Collected
- Personal messages
- Location data
- Contact information
- Message content

### Data Retention
- Analytics data is stored locally
- No data is sent to third parties
- Data can be deleted at any time

## 🛠️ Advanced Analytics

### Custom Queries
```python
from analytics import analytics

# Get specific user stats
stats = analytics.get_stats()
for user in stats['top_users']:
    if user['user_name'] == 'John Doe':
        print(f"User activity: {user}")

# Export data for external analysis
import json
with open('export.json', 'w') as f:
    json.dump(analytics.analytics_data, f, indent=2)
```

### Monitoring Alerts
```bash
# Check for high error rates
python -c "
from analytics import analytics
stats = analytics.get_stats()
if stats['success_rate'] < 90:
    print('⚠️ Low success rate detected!')
"
```

## 📈 Performance Metrics

### Key Performance Indicators (KPIs)
- **Conversion Rate** - Target: >95%
- **Response Time** - Target: <2 seconds
- **Uptime** - Target: >99.9%
- **User Retention** - Track returning users

### Business Metrics
- **Daily Active Users** - Growth tracking
- **Peak Usage Times** - Capacity planning
- **Popular Formats** - Feature development
- **Error Patterns** - Quality improvement

## 🔄 Data Export & Backup

### Export Options
```bash
# Export to JSON
python stats_viewer.py --json > analytics_export.json

# Export to CSV (custom script)
python export_to_csv.py

# Backup to Google Cloud Storage
gsutil cp bot_analytics.json gs://your-bucket/analytics/
```

### Automated Backups
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y-%m-%d)
gsutil cp bot_analytics.json gs://your-bucket/analytics/backup_$DATE.json
```

## 🎯 Future Enhancements

### Planned Features
- **Real-time Dashboard** - Live statistics
- **Email Reports** - Automated summaries
- **API Endpoints** - External access
- **Advanced Filtering** - Custom date ranges
- **Export Formats** - PDF, Excel, CSV
- **Alert System** - Performance notifications

### Integration Options
- **Google Analytics** - Web traffic correlation
- **Slack Notifications** - Real-time alerts
- **Grafana Dashboards** - Advanced visualization
- **Data Warehouse** - Long-term storage

---

*Analytics help you understand your users and improve your bot's performance!* 📊 