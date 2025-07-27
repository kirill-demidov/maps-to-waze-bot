# 📊 Bot Analytics System

Analytics system for tracking Telegram bot usage.

## 🎯 Features

### User Tracking
- **User Count** - total number of unique users
- **User Activity** - first and last interaction times
- **User Statistics** - successful/failed interaction counts

### Interaction Tracking
- **Commands** - `/start`, `/help`, `/menu`, `/language`
- **Buttons** - inline button clicks
- **Messages** - text message processing
- **Link Processing** - successful and failed attempts

### Daily Statistics
- **Daily Activity** - interaction count by day
- **Unique Users** - number of active users per day
- **Link Processing** - successful and failed attempts by day

### Language Preferences
- **Language Distribution** - language usage statistics
- **Language Changes** - tracking language setting changes

## 🚀 Running the Analytics System

### Local Setup
```bash
# Start analytics web interface
python stats_viewer.py
```

### Access to Analytics
- **Web Interface**: http://localhost:8082
- **Stats API**: http://localhost:8082/api/stats
- **User Stats**: http://localhost:8082/api/user?user_id=123456

## 📈 Metrics

### Key Indicators
- **Total Users** - total number of users
- **Total Interactions** - total number of interactions
- **Success Rate** - percentage of successful operations
- **Uptime** - bot running time

### Link Processing
- **Total** - total processing attempts
- **Successful** - successful processing
- **Failed** - failed processing

### Popular Commands
- List of most used commands and buttons
- Usage count for each command

## 🔧 Integration

### Automatic Tracking
The system automatically tracks:
- ✅ Commands `/start`, `/help`, `/menu`, `/language`
- ✅ Button clicks
- ✅ Message processing
- ✅ Language changes
- ✅ Successful/failed link processing

### Manual Tracking
```python
from analytics import analytics

# Track user interaction
analytics.track_user_interaction(user_id, "custom_action", True)

# Track link processing
analytics.track_link_processing(user_id, url, success, coordinates, error)

# Track language change
analytics.track_language_change(user_id, language)
```

## 📊 Web Interface

### Main Page
- **Dashboard** with key metrics
- **Activity charts** by day
- **Top commands** and languages
- **Link processing statistics**

### User Search
- **Search by User ID** - enter user ID to view their statistics
- **Detailed information** - first/last interaction times
- **User actions** - list of all user actions

## 🔒 Security

### Data Protection
- **Anonymization** - user data is stored securely
- **Limited Access** - local access only to analytics
- **Auto-cleanup** - old data is automatically deleted

### Data Cleanup
```python
# Clean up data older than 30 days
analytics.cleanup_old_data(days_to_keep=30)
```

## 📁 Files

### Main Files
- `analytics.py` - main analytics system
- `stats_viewer.py` - web interface for viewing
- `analytics_data.json` - data file (created automatically)

### Configuration
- **Web Interface Port**: 8082 (default)
- **Data File**: `analytics_data.json`
- **Auto-save**: after each interaction

## 🛠️ Development

### Adding New Metrics
```python
# In processing function
if ANALYTICS_AVAILABLE and analytics:
    analytics.track_user_interaction(user_id, "new_action", True)
```

### Extending Web Interface
- Add new endpoints to `StatsViewerHandler`
- Update HTML/JavaScript to display new data

## 📈 Usage Examples

### View General Statistics
```bash
curl http://localhost:8082/api/stats
```

### Search for User
```bash
curl "http://localhost:8082/api/user?user_id=123456"
```

### Web Interface
Open http://localhost:8082 in your browser to view the beautiful analytics dashboard.

## 🎯 Benefits

1. **Automatic Tracking** - no additional actions required
2. **Beautiful Web Interface** - convenient statistics viewing
3. **Detailed Analytics** - information about users and actions
4. **Security** - protected data storage
5. **Easy to Use** - simple to start and use 