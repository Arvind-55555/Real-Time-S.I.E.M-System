#!/usr/bin/env python3
"""
Simple Web Dashboard for SIEM - View alerts and statistics in browser
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from realtime_siem.core.siem_engine import SIEMCore
from realtime_siem.config.config_manager import ConfigManager

# Global SIEM instance
siem = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIEM Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{
            color: #667eea;
            font-size: 2em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .alerts-section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .alert-item {{
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .alert-critical {{ border-left-color: #dc3545; }}
        .alert-high {{ border-left-color: #fd7e14; }}
        .alert-medium {{ border-left-color: #ffc107; }}
        .alert-low {{ border-left-color: #28a745; }}
        .severity-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }}
        .severity-critical {{ background: #dc3545; }}
        .severity-high {{ background: #fd7e14; }}
        .severity-medium {{ background: #ffc107; }}
        .severity-low {{ background: #28a745; }}
        .status-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        .status-open {{ background: #dc3545; color: white; }}
        .status-closed {{ background: #28a745; color: white; }}
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 0;
        }}
        .refresh-btn:hover {{ background: #5568d3; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .auto-refresh {{
            float: right;
            color: #28a745;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ SIEM Dashboard</h1>
            <p>Real-time Security Monitoring</p>
            <span class="auto-refresh">● Auto-refreshing every 5 seconds</span>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Alerts</h3>
                <div class="stat-value">{total_alerts}</div>
            </div>
            <div class="stat-card">
                <h3>Open Alerts</h3>
                <div class="stat-value" style="color: #dc3545;">{open_alerts}</div>
            </div>
            <div class="stat-card">
                <h3>Events Processed</h3>
                <div class="stat-value" style="color: #28a745;">{events_processed}</div>
            </div>
            <div class="stat-card">
                <h3>System Status</h3>
                <div class="stat-value" style="font-size: 1.5em; color: {status_color};">{status}</div>
            </div>
        </div>
        
        <div class="alerts-section">
            <h2>Recent Alerts</h2>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
            
            {alerts_html}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds
        setTimeout(function(){{ location.reload(); }}, 5000);
    </script>
</body>
</html>
"""

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global siem
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get stats
            stats = siem.get_stats()
            alerts = siem.alert_manager.get_alerts()
            open_alerts = siem.alert_manager.get_alerts(status='open')
            
            # Generate alerts HTML
            alerts_html = ""
            for alert in reversed(alerts[-20:]):  # Show last 20
                severity = alert.get('severity', 'low')
                status = alert.get('status', 'open')
                threat = alert.get('threat', {})
                
                alerts_html += f"""
                <div class="alert-item alert-{severity}">
                    <div>
                        <span class="severity-badge severity-{severity}">{severity.upper()}</span>
                        <span class="status-badge status-{status}">{status.upper()}</span>
                        <span class="timestamp">{alert.get('timestamp', 'N/A')}</span>
                    </div>
                    <h4>{alert.get('alert_id', 'N/A')}</h4>
                    <p>Type: {threat.get('type', threat.get('rule_name', 'Unknown'))}</p>
                    {f"<p>{threat.get('description', '')}</p>" if threat.get('description') else ''}
                </div>
                """
            
            if not alerts_html:
                alerts_html = "<p>No alerts yet. System is monitoring...</p>"
            
            # Fill template
            html = HTML_TEMPLATE.format(
                total_alerts=stats['alerts_count'],
                open_alerts=len(open_alerts),
                events_processed=siem.event_processor.processed_count,
                status='🟢 Running' if stats['is_running'] else '🔴 Stopped',
                status_color='#28a745' if stats['is_running'] else '#dc3545',
                alerts_html=alerts_html
            )
            
            self.wfile.write(html.encode())
        
        elif parsed_path.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            stats = siem.get_stats()
            stats['events_processed'] = siem.event_processor.processed_count
            
            self.wfile.write(json.dumps(stats).encode())
        
        elif parsed_path.path == '/api/alerts':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            alerts = siem.alert_manager.get_alerts()
            self.wfile.write(json.dumps(alerts, default=str).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress access logs
        pass

def run_dashboard(port=8080):
    global siem
    
    print(f"🚀 Starting SIEM Dashboard...")
    
    # Initialize SIEM
    config = ConfigManager()
    siem = SIEMCore(config)
    siem.start()
    
    print(f"✓ SIEM initialized")
    
    # Start web server
    server = HTTPServer(('', port), DashboardHandler)
    
    print(f"\n{'='*60}")
    print(f"  SIEM Dashboard running at: http://localhost:{port}")
    print(f"  API endpoints:")
    print(f"    - http://localhost:{port}/api/stats")
    print(f"    - http://localhost:{port}/api/alerts")
    print(f"\n  Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down dashboard...")
        siem.stop()
        server.shutdown()
        print("✓ Dashboard stopped\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='SIEM Web Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on (default: 8080)')
    args = parser.parse_args()
    
    run_dashboard(args.port)
