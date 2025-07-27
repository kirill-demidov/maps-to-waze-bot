#!/usr/bin/env python3
"""
Bot Statistics Viewer
Usage: python stats_viewer.py [--days N] [--json] [--web]
"""

import argparse
import json
import webbrowser
from datetime import datetime
from analytics import analytics

def view_stats(days=7, json_output=False, web_output=False):
    """View bot statistics"""
    
    if json_output:
        # Output raw JSON data
        stats = analytics.get_stats(days)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return
    
    if web_output:
        # Generate HTML report
        generate_html_report(days)
        return
    
    # Generate text report
    report = analytics.generate_report(days)
    print(report)

def generate_html_report(days=7):
    """Generate HTML analytics report"""
    stats = analytics.get_stats(days)
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maps to Waze Bot Analytics</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
        }}
        .stat-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            padding: 20px;
            border-bottom: 1px solid #eee;
        }}
        .section h2 {{
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .user-list {{
            list-style: none;
            padding: 0;
        }}
        .user-item {{
            background: #f8f9fa;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .error-list {{
            list-style: none;
            padding: 0;
        }}
        .error-item {{
            background: #fff3cd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Bot Analytics Dashboard</h1>
            <p>Last {days} days of activity</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_requests']:,}</div>
                <div class="stat-label">Total Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['successful_conversions']:,}</div>
                <div class="stat-label">Successful Conversions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['success_rate']}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(stats['top_users'])}</div>
                <div class="stat-label">Active Users</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📅 Daily Activity</h2>
            <div class="stats-grid">
"""
    
    for day in stats['daily_stats']:
        html += f"""
                <div class="stat-card">
                    <div class="stat-number">{day['requests']}</div>
                    <div class="stat-label">{day['date']}</div>
                    <div style="color: #28a745; font-size: 0.9em;">{day['successful']} successful</div>
                </div>
"""
    
    html += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Format Distribution</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['format_distribution']['google_maps_links']:,}</div>
                    <div class="stat-label">Google Maps Links</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['format_distribution']['coordinates']:,}</div>
                    <div class="stat-label">Coordinates</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['format_distribution']['dms_coordinates']:,}</div>
                    <div class="stat-label">DMS Coordinates</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>👥 Top Users</h2>
            <ul class="user-list">
"""
    
    for user in stats['top_users'][:10]:
        success_rate = round((user['successful_requests'] / user['total_requests']) * 100, 2) if user['total_requests'] > 0 else 0
        html += f"""
                <li class="user-item">
                    <strong>{user['user_name']}</strong><br>
                    {user['total_requests']} requests ({success_rate}% success)<br>
                    <small>Last seen: {user['last_seen'][:10]}</small>
                </li>
"""
    
    html += """
            </ul>
        </div>
"""
    
    if stats['error_distribution']:
        html += """
        <div class="section">
            <h2>❌ Error Distribution</h2>
            <ul class="error-list">
"""
        
        for error, count in stats['error_distribution'].items():
            html += f"""
                <li class="error-item">
                    <strong>{error}</strong>: {count} occurrences
                </li>
"""
        
        html += """
            </ul>
        </div>
"""
    
    html += f"""
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Maps to Waze Bot Analytics Dashboard</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    with open('analytics_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Open in browser
    webbrowser.open('analytics_report.html')
    print("📊 HTML report generated and opened in browser!")

def main():
    parser = argparse.ArgumentParser(description='View bot analytics')
    parser.add_argument('--days', type=int, default=7, help='Number of days to analyze (default: 7)')
    parser.add_argument('--json', action='store_true', help='Output raw JSON data')
    parser.add_argument('--web', action='store_true', help='Generate HTML report and open in browser')
    
    args = parser.parse_args()
    
    view_stats(args.days, args.json, args.web)

if __name__ == "__main__":
    main() 