#!/usr/bin/env python3
"""
Integrated SIEM Dashboard with Event Generator
Combines dashboard and event generation in one process
"""

import sys
from pathlib import Path
import json
import random
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from realtime_siem.core.siem_engine import SIEMCore
from realtime_siem.config.config_manager import ConfigManager

# Global SIEM instance
siem = None
auto_generate = True

# Sample events for automatic generation
SAMPLE_EVENTS = [
    '{"user": "alice", "action": "login", "status": "success", "source_ip": "10.0.1.50"}',
    '{"user": "admin", "action": "login", "status": "failed", "failed_logins": 8, "source_ip": "203.0.113.1"}',
    '{"user": "bob", "action": "file_access", "source_ip": "192.0.2.1", "file": "/etc/passwd"}',
    '{"user": "charlie", "action": "upload", "bytes_sent": 150000000, "destination": "external.com"}',
    '{"user": "dave", "action": "sudo", "command": "su root"}',
    '<134>Dec 12 10:05:15 server1 sshd[12345]: Failed password for admin',
    'ERROR: Unauthorized access attempt from 198.51.100.1',
    'WARNING: Multiple failed authentication attempts',
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIEM Dashboard - Live</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{ color: #667eea; font-size: 2em; }}
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
            animation: slideIn 0.3s ease-out;
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
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
        .severity-medium {{ background: #ffc107; color: #333; }}
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
        .controls {{
            margin: 20px 0;
            display: flex;
            gap: 10px;
        }}
        button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
        }}
        button:hover {{ background: #5568d3; }}
        button.secondary {{ background: #6c757d; }}
        button.secondary:hover {{ background: #5a6268; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .auto-refresh {{
            float: right;
            color: #28a745;
            font-size: 0.9em;
        }}
        .live-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #28a745;
            border-radius: 50%;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ SIEM Dashboard</h1>
            <p>Real-time Security Monitoring <span class="live-indicator"></span><span style="color: #28a745;">LIVE</span></p>
            <span class="auto-refresh">Auto-refreshing every 3 seconds</span>
        </header>
        
        <div class="controls">
            <button onclick="location.reload()">🔄 Refresh Now</button>
            <button class="secondary" onclick="generateEvent()">⚡ Generate Test Event</button>
            <button class="secondary" onclick="clearAlerts()">🗑️ Clear Alerts</button>
        </div>
        
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
            <h2>Recent Alerts (Last 20)</h2>
            {alerts_html}
        </div>
    </div>
    
    <script>
        setTimeout(function(){{ location.reload(); }}, 3000);
        
        function generateEvent() {{
            fetch('/api/generate').then(() => {{
                alert('Test event generated! Dashboard will refresh automatically.');
            }});
        }}
        
        function clearAlerts() {{
            if (confirm('Clear all alerts?')) {{
                fetch('/api/clear').then(() => location.reload());
            }}
        }}
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
            
            stats = siem.get_stats()
            alerts = siem.alert_manager.get_alerts()
            open_alerts = siem.alert_manager.get_alerts(status='open')
            
            alerts_html = ""
            for alert in reversed(alerts[-20:]):
                severity = alert.get('severity', 'low')
                status = alert.get('status', 'open')
                threat = alert.get('threat', {})
                event = alert.get('event', {})
                
                event_info = ""
                if 'user' in event:
                    event_info += f"User: {event['user']} | "
                if 'source_ip' in event:
                    event_info += f"IP: {event['source_ip']} | "
                
                alerts_html += f"""
                <div class="alert-item alert-{severity}">
                    <div>
                        <span class="severity-badge severity-{severity}">{severity.upper()}</span>
                        <span class="status-badge status-{status}">{status.upper()}</span>
                        <span class="timestamp">{alert.get('timestamp', 'N/A')[:19]}</span>
                    </div>
                    <h4>{alert.get('alert_id', 'N/A')}</h4>
                    <p><strong>Threat:</strong> {threat.get('type', threat.get('rule_name', 'Unknown'))}</p>
                    {f"<p><strong>Description:</strong> {threat.get('description', '')}</p>" if threat.get('description') else ''}
                    {f"<p><strong>Event Details:</strong> {event_info.rstrip(' | ')}</p>" if event_info else ''}
                </div>
                """
            
            if not alerts_html:
                alerts_html = "<p>No alerts yet. System is monitoring... Events are being generated automatically.</p>"
            
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
        
        elif parsed_path.path == '/api/generate':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Generate one event immediately
            generate_single_event()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())
        
        elif parsed_path.path == '/api/clear':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            siem.alert_manager.alerts.clear()
            self.wfile.write(json.dumps({'status': 'cleared'}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def generate_single_event():
    """Generate a single random event"""
    global siem
    log = random.choice(SAMPLE_EVENTS)
    log_type = 'json' if log.startswith('{') else 'syslog' if log.startswith('<') else 'default'
    siem.process_log(log, log_type)

def event_generator():
    """Background thread to generate events automatically"""
    global auto_generate, siem
    
    print("🤖 Auto-generating events every 5 seconds...")
    
    while auto_generate:
        time.sleep(5)
        generate_single_event()
        
        # Print stats occasionally
        stats = siem.get_stats()
        if siem.event_processor.processed_count % 10 == 0:
            print(f"  📊 Events: {siem.event_processor.processed_count} | Alerts: {stats['alerts_count']}")

def run_dashboard(port=8080):
    global siem, auto_generate
    
    print(f"🚀 Starting Integrated SIEM Dashboard...")
    
    config = ConfigManager()
    siem = SIEMCore(config)
    siem.start()
    
    print(f"✓ SIEM initialized")
    
    # Start event generator thread
    generator_thread = threading.Thread(target=event_generator, daemon=True)
    generator_thread.start()
    
    server = HTTPServer(('', port), DashboardHandler)
    
    print(f"\n{'='*60}")
    print(f"  🛡️  LIVE SIEM Dashboard: http://localhost:{port}")
    print(f"  📊 Events auto-generating every 5 seconds")
    print(f"  🔄 Dashboard auto-refreshes every 3 seconds")
    print(f"\n  API Endpoints:")
    print(f"    - http://localhost:{port}/api/stats")
    print(f"    - http://localhost:{port}/api/alerts")
    print(f"    - http://localhost:{port}/api/generate (trigger event)")
    print(f"\n  Press Ctrl+C to stop")
    print(f"{'='*60}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down...")
        auto_generate = False
        siem.stop()
        server.shutdown()
        print("✓ Dashboard stopped\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='SIEM Live Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Port to run on')
    args = parser.parse_args()
    
    run_dashboard(args.port)
