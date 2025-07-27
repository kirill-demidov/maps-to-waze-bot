# 🔐 Analytics Security & Access Control

## 👥 Who Can See Statistics

### 🔐 **Admin Access (Full Data)**
- **Bot Owner** - You have complete access
- **Authorized Developers** - Set via environment variables
- **Server Administrators** - Direct server access

### 🌍 **Public Access (Anonymized Data)**
- **General Public** - Basic statistics only
- **Potential Users** - Success rates and usage patterns
- **Researchers** - Anonymized data for analysis

### 🚫 **No Access**
- **Regular Users** - Cannot see any statistics
- **Unauthorized Persons** - Blocked by security system

## 🛡️ Security Levels

### Level 1: Public Statistics
```bash
# Anyone can view
python secure_stats_viewer.py --public
```

**What's Visible:**
- ✅ Total requests count
- ✅ Success rate percentage
- ✅ Format distribution (types of links used)
- ✅ API usage statistics
- ❌ No user names or IDs
- ❌ No personal data
- ❌ No individual user statistics

### Level 2: Admin Statistics
```bash
# Only authorized users
python secure_stats_viewer.py --admin YOUR_USER_ID
```

**What's Visible:**
- ✅ All public data
- ✅ Individual user statistics
- ✅ User names and activity
- ✅ Error details
- ✅ Daily breakdowns
- ✅ Top users list

### Level 3: Raw Data Access
```bash
# Direct file access (server only)
cat bot_analytics.json
```

**What's Visible:**
- ✅ Complete raw data
- ✅ All user information
- ✅ Timestamps and details
- ⚠️ Requires server access

## 🔧 Setting Up Access Control

### 1. Configure Admin Users
```bash
# Set admin user IDs
export ANALYTICS_ADMIN_USERS="123456789,987654321"

# Or add to your .env file
echo "ANALYTICS_ADMIN_USERS=123456789,987654321" >> .env
```

### 2. Get Your User ID
```bash
# Your Telegram user ID (get from bot logs)
# Look for messages from your account
```

### 3. Test Access
```bash
# Test public access
python secure_stats_viewer.py --public

# Test admin access
python secure_stats_viewer.py --admin YOUR_USER_ID
```

## 📊 Data Privacy

### ✅ Data Collected
- User ID (from Telegram)
- Username (from Telegram)
- Request timestamps
- Success/failure status
- Input format type
- Error types

### ❌ Data NOT Collected
- Personal messages
- Location coordinates
- Contact information
- Message content
- Private conversations

### 🔒 Data Protection
- **Local Storage** - Data stays on your server
- **No Third Parties** - Not shared with external services
- **Anonymization** - Public data has no personal info
- **Retention Policy** - Old data automatically deleted

## 🧹 Data Management

### Automatic Cleanup
```bash
# Clean up old data (90 days retention)
python secure_stats_viewer.py --cleanup
```

### Manual Export
```bash
# Export anonymized data for sharing
python secure_stats_viewer.py --export-anonymized
```

### Backup Data
```bash
# Backup analytics data
cp bot_analytics.json backup_$(date +%Y%m%d).json

# Upload to Google Cloud Storage
gsutil cp bot_analytics.json gs://your-bucket/analytics/
```

## 🚨 Security Best Practices

### 1. **Environment Variables**
```bash
# Never hardcode user IDs
export ANALYTICS_ADMIN_USERS="your_user_id"

# Use .env file (not in git)
echo "ANALYTICS_ADMIN_USERS=your_user_id" >> .env
```

### 2. **File Permissions**
```bash
# Restrict file access
chmod 600 bot_analytics.json
chmod 600 .env
```

### 3. **Regular Cleanup**
```bash
# Set up automated cleanup
crontab -e
# Add: 0 2 * * 0 python /path/to/secure_stats_viewer.py --cleanup
```

### 4. **Monitor Access**
```bash
# Check who accessed the file
ls -la bot_analytics.json
tail -f /var/log/auth.log | grep bot_analytics
```

## 📈 Public Statistics Page

### Option 1: Static Page
```html
<!-- public_stats.html -->
<!DOCTYPE html>
<html>
<head><title>Bot Statistics</title></head>
<body>
    <h1>📊 Bot Usage Statistics</h1>
    <p>Total Requests: <span id="total">Loading...</span></p>
    <p>Success Rate: <span id="rate">Loading...</span></p>
</body>
</html>
```

### Option 2: API Endpoint
```python
# Flask endpoint for public stats
@app.route('/api/stats/public')
def public_stats():
    return jsonify(analytics_security.get_public_stats())
```

## 🔍 Monitoring & Alerts

### Check for Unauthorized Access
```bash
# Monitor file access
inotifywait -m bot_analytics.json -e access,modify

# Check for suspicious activity
grep "bot_analytics" /var/log/auth.log
```

### Set Up Alerts
```bash
# Alert if success rate drops
python -c "
from analytics import analytics
stats = analytics.get_stats()
if stats['success_rate'] < 90:
    print('⚠️ Low success rate!')
"
```

## 📋 Access Control Checklist

- [ ] Set up admin user IDs
- [ ] Test public access
- [ ] Test admin access
- [ ] Configure file permissions
- [ ] Set up automated cleanup
- [ ] Create backup strategy
- [ ] Monitor access logs
- [ ] Document access procedures

## 🆘 Emergency Procedures

### If Data is Compromised
```bash
# 1. Stop the bot
pkill -f maps_to_waze_bot.py

# 2. Backup current data
cp bot_analytics.json compromised_backup.json

# 3. Anonymize data
python secure_stats_viewer.py --export-anonymized

# 4. Reset analytics
rm bot_analytics.json

# 5. Restart bot
python maps_to_waze_bot.py
```

### If Admin Access is Lost
```bash
# Reset admin users
export ANALYTICS_ADMIN_USERS="your_new_user_id"

# Or edit the file directly (emergency only)
echo '{"admin_users": ["your_new_user_id"]}' > admin_config.json
```

---

*Security is crucial for protecting user privacy and maintaining trust!* 🔒 