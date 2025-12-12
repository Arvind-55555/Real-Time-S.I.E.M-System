#!/usr/bin/env python3
"""
Real-time SIEM Monitor - Display events and alerts as they happen
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from realtime_siem.core.siem_engine import SIEMCore
from realtime_siem.config.config_manager import ConfigManager
from realtime_siem.utils.helpers import setup_logging

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    
    class Fore:
        RED = YELLOW = GREEN = CYAN = MAGENTA = BLUE = WHITE = ""
    
    class Style:
        BRIGHT = RESET_ALL = ""

def get_severity_color(severity):
    if not COLORS_AVAILABLE:
        return ""
    
    colors = {
        'critical': Fore.RED + Style.BRIGHT,
        'high': Fore.RED,
        'medium': Fore.YELLOW,
        'low': Fore.CYAN,
    }
    return colors.get(severity.lower(), Fore.WHITE)

def print_banner():
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║         REAL-TIME SIEM MONITORING DASHBOARD                  ║
║                                                              ║
║  Press Ctrl+C to stop monitoring                             ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def display_event(event, show_full=False):
    timestamp = event.get('timestamp', datetime.utcnow().isoformat())
    event_type = event.get('type', 'unknown')
    event_id = event.get('event_id', 'N/A')
    
    # Event header
    print(f"\n{Fore.CYAN}[{timestamp}] {Fore.WHITE}Event: {event_id} | Type: {event_type}")
    
    # Message
    message = event.get('message', 'No message')
    if len(message) > 100 and not show_full:
        message = message[:100] + "..."
    print(f"  Message: {message}")
    
    # Source information
    if 'source_ip' in event:
        print(f"  Source IP: {Fore.MAGENTA}{event['source_ip']}{Style.RESET_ALL}")
    if 'user' in event:
        print(f"  User: {Fore.MAGENTA}{event['user']}{Style.RESET_ALL}")
    
    # Threats
    if 'threats' in event and event['threats']:
        print(f"\n  {Fore.RED}⚠️  THREATS DETECTED: {len(event['threats'])}{Style.RESET_ALL}")
        for threat in event['threats']:
            severity = threat.get('severity', 'unknown')
            threat_type = threat.get('type', threat.get('rule_name', 'unknown'))
            color = get_severity_color(severity)
            print(f"    {color}[{severity.upper()}]{Style.RESET_ALL} {threat_type}")
            
            if 'description' in threat:
                print(f"      → {threat['description']}")

def display_stats(siem):
    stats = siem.get_stats()
    alerts = siem.alert_manager.get_alerts(status='open')
    
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"{'SYSTEM STATISTICS':^60}")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    print(f"  Status: {'🟢 Running' if stats['is_running'] else '🔴 Stopped'}")
    print(f"  Elasticsearch: {'🟢 Connected' if stats['elasticsearch_connected'] else '🔴 Disconnected'}")
    print(f"  Active Alerts: {Fore.RED}{len(alerts)}{Style.RESET_ALL}")
    print(f"  Total Alerts: {stats['alerts_count']}")
    print(f"  Events Processed: {siem.event_processor.processed_count}")

def monitor_file(filepath, siem, args):
    """Monitor a log file for new entries"""
    print(f"{Fore.CYAN}Monitoring file: {filepath}{Style.RESET_ALL}\n")
    
    with open(filepath, 'r') as f:
        # Go to end of file if --tail is specified
        if args.tail:
            f.seek(0, 2)
        
        try:
            while True:
                line = f.readline()
                
                if not line:
                    if args.follow:
                        time.sleep(0.1)
                        continue
                    else:
                        break
                
                # Process the log line
                log_type = 'json' if line.strip().startswith('{') else 'syslog' if line.strip().startswith('<') else 'default'
                result = siem.process_log(line.strip(), log_type)
                
                if result:
                    display_event(result, args.verbose)
                
                if args.interval > 0:
                    time.sleep(args.interval)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Monitoring stopped{Style.RESET_ALL}")

def simulate_events(siem, args):
    """Simulate random security events"""
    import random
    
    sample_events = [
        '{"user": "alice", "action": "login", "status": "success", "source_ip": "10.0.1.50"}',
        '{"user": "admin", "action": "login", "status": "failed", "failed_logins": 8, "source_ip": "203.0.113.1"}',
        '{"user": "bob", "action": "file_access", "source_ip": "192.0.2.1", "file": "/etc/passwd"}',
        '<134>Dec 12 10:05:15 server1 sshd[12345]: Failed password for admin',
        'ERROR: Unauthorized access attempt from 198.51.100.1',
    ]
    
    print(f"{Fore.CYAN}Simulating security events...{Style.RESET_ALL}\n")
    
    try:
        count = 0
        while count < args.count if args.count > 0 else True:
            log = random.choice(sample_events)
            log_type = 'json' if log.startswith('{') else 'syslog' if log.startswith('<') else 'default'
            
            result = siem.process_log(log, log_type)
            
            if result:
                display_event(result, args.verbose)
            
            count += 1
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Simulation stopped{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='Real-time SIEM Monitor')
    parser.add_argument('--file', type=str, help='Log file to monitor')
    parser.add_argument('--follow', '-f', action='store_true', help='Follow log file (like tail -f)')
    parser.add_argument('--tail', action='store_true', help='Start from end of file')
    parser.add_argument('--simulate', action='store_true', help='Simulate random events')
    parser.add_argument('--count', type=int, default=10, help='Number of events to simulate (0 = infinite)')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval between events (seconds)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show full event details')
    parser.add_argument('--stats', action='store_true', help='Show statistics periodically')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Initialize SIEM
    print(f"{Fore.GREEN}Initializing SIEM...{Style.RESET_ALL}")
    setup_logging()
    config = ConfigManager()
    siem = SIEMCore(config)
    siem.start()
    print(f"{Fore.GREEN}✓ SIEM started{Style.RESET_ALL}\n")
    
    try:
        if args.file:
            monitor_file(args.file, siem, args)
        elif args.simulate:
            simulate_events(siem, args)
        else:
            # Interactive mode
            print(f"{Fore.YELLOW}No file specified. Use --file or --simulate{Style.RESET_ALL}")
            print(f"\nExample usage:")
            print(f"  python3 scripts/monitor.py --simulate")
            print(f"  python3 scripts/monitor.py --file logs/siem.log --follow")
        
        # Show final stats
        if args.stats or args.simulate or args.file:
            print()
            display_stats(siem)
    
    finally:
        siem.stop()
        print(f"\n{Fore.GREEN}✓ SIEM stopped{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
