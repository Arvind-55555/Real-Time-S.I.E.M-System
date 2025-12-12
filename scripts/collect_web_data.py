#!/usr/bin/env python3
"""
Real-time Web Data Collector
Fetches security events from public APIs and feeds
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, List
import feedparser
import logging

from realtime_siem.core.siem_engine import SIEMCore
from realtime_siem.config.config_manager import ConfigManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDataCollector:
    """Collect security events from web sources"""
    
    def __init__(self, siem: SIEMCore):
        self.siem = siem
        self.running = False
        
    def collect_threat_feeds(self):
        """Collect from threat intelligence feeds"""
        feeds = [
            'https://feeds.feedburner.com/TheHackersNews',
            'https://www.bleepingcomputer.com/feed/',
            'https://threatpost.com/feed/',
        ]
        
        logger.info("🌐 Collecting from threat intelligence feeds...")
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Get latest 5
                    event = {
                        'source': 'threat_feed',
                        'type': 'threat_intelligence',
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', '')[:200],
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'timestamp': datetime.utcnow().isoformat(),
                        'threat_level': self._assess_threat_level(entry.get('title', ''))
                    }
                    
                    # Convert to JSON and process
                    self.siem.process_log(json.dumps(event), 'json')
                    logger.info(f"  📰 {entry.get('title', 'Unknown')[:60]}...")
                    
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {e}")
    
    def collect_abuse_ipdb(self, sample_ips: List[str]):
        """Check IPs against AbuseIPDB (requires API key)"""
        # This is a demo - you'd need a real API key
        logger.info("🔍 Checking IPs against threat databases...")
        
        for ip in sample_ips:
            event = {
                'source': 'abuse_check',
                'type': 'ip_reputation',
                'source_ip': ip,
                'timestamp': datetime.utcnow().isoformat(),
                'reputation_score': self._mock_reputation_score(ip),
                'threat_category': 'suspicious' if '192.0.2' in ip else 'clean'
            }
            
            self.siem.process_log(json.dumps(event), 'json')
            logger.info(f"  🔎 Checked IP: {ip}")
    
    def collect_github_security_advisories(self):
        """Fetch from GitHub security advisories"""
        try:
            url = "https://api.github.com/advisories"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                advisories = response.json()
                logger.info("🔐 Collecting GitHub security advisories...")
                
                for advisory in advisories[:10]:  # Get latest 10
                    event = {
                        'source': 'github_advisory',
                        'type': 'vulnerability',
                        'ghsa_id': advisory.get('ghsa_id', ''),
                        'severity': advisory.get('severity', 'unknown'),
                        'summary': advisory.get('summary', ''),
                        'cve_id': advisory.get('cve_id', ''),
                        'published_at': advisory.get('published_at', ''),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    self.siem.process_log(json.dumps(event), 'json')
                    logger.info(f"  🛡️  {advisory.get('summary', 'Unknown')[:60]}...")
                    
        except Exception as e:
            logger.error(f"Error fetching GitHub advisories: {e}")
    
    def simulate_live_traffic(self):
        """Simulate live web traffic with potential threats"""
        import random
        
        logger.info("🚦 Simulating live web traffic...")
        
        traffic_patterns = [
            # Normal traffic
            {
                'source_ip': f'10.0.{random.randint(1,255)}.{random.randint(1,255)}',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'method': 'GET',
                'path': '/',
                'status_code': 200,
                'bytes_sent': random.randint(1000, 10000)
            },
            # Suspicious traffic
            {
                'source_ip': f'192.0.2.{random.randint(1,255)}',
                'user_agent': 'sqlmap/1.0',
                'method': 'POST',
                'path': '/admin/login',
                'query': "username=admin' OR 1=1--",
                'status_code': 403,
                'failed_logins': random.randint(5, 15)
            },
            # Port scan
            {
                'source_ip': f'203.0.113.{random.randint(1,100)}',
                'user_agent': 'nmap',
                'unique_ports_accessed': random.randint(20, 50),
                'scan_type': 'syn_scan'
            },
            # Large data transfer
            {
                'source_ip': f'10.0.{random.randint(1,255)}.{random.randint(1,255)}',
                'user': 'employee_' + str(random.randint(1,100)),
                'action': 'upload',
                'bytes_sent': random.randint(100000000, 500000000),
                'destination': 'external-server.com'
            },
        ]
        
        for _ in range(10):
            pattern = random.choice(traffic_patterns)
            pattern['timestamp'] = datetime.utcnow().isoformat()
            pattern['type'] = 'web_traffic'
            
            self.siem.process_log(json.dumps(pattern), 'json')
            time.sleep(0.5)
    
    def collect_honeypot_data(self):
        """Simulate honeypot data collection"""
        logger.info("🍯 Collecting honeypot data...")
        
        honeypot_events = [
            {
                'source': 'honeypot',
                'type': 'ssh_attempt',
                'source_ip': f'185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                'username': random.choice(['root', 'admin', 'user', 'test']),
                'password': random.choice(['123456', 'password', 'admin', 'root']),
                'timestamp': datetime.utcnow().isoformat(),
                'failed_logins': random.randint(5, 20)
            }
            for _ in range(5)
        ]
        
        for event in honeypot_events:
            self.siem.process_log(json.dumps(event), 'json')
            logger.info(f"  🎣 Honeypot catch: {event['source_ip']} tried {event['username']}")
    
    def _assess_threat_level(self, title: str) -> str:
        """Assess threat level from title"""
        title_lower = title.lower()
        if any(word in title_lower for word in ['critical', 'zero-day', 'ransomware', 'breach']):
            return 'critical'
        elif any(word in title_lower for word in ['vulnerability', 'exploit', 'malware']):
            return 'high'
        elif any(word in title_lower for word in ['phishing', 'scam', 'warning']):
            return 'medium'
        return 'low'
    
    def _mock_reputation_score(self, ip: str) -> int:
        """Mock reputation score for demo"""
        if '192.0.2' in ip or '203.0.113' in ip:
            return random.randint(80, 100)  # High risk
        return random.randint(0, 30)  # Low risk
    
    def start_continuous_collection(self, interval: int = 60):
        """Start continuous data collection"""
        self.running = True
        
        def collection_loop():
            while self.running:
                try:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"🔄 Data Collection Cycle - {datetime.now().strftime('%H:%M:%S')}")
                    logger.info(f"{'='*60}")
                    
                    # Collect from various sources
                    self.simulate_live_traffic()
                    self.collect_honeypot_data()
                    
                    # Every 5 minutes, fetch external data
                    if int(time.time()) % 300 < interval:
                        self.collect_threat_feeds()
                        self.collect_github_security_advisories()
                        
                        # Sample IPs to check
                        sample_ips = [
                            '192.0.2.1', '10.0.1.50', '203.0.113.100',
                            f'185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'
                        ]
                        self.collect_abuse_ipdb(sample_ips)
                    
                    # Show stats
                    stats = self.siem.get_stats()
                    logger.info(f"\n📊 Current Stats:")
                    logger.info(f"   Events Processed: {self.siem.event_processor.processed_count}")
                    logger.info(f"   Active Alerts: {stats['alerts_count']}")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error in collection loop: {e}")
                    time.sleep(interval)
        
        collection_thread = threading.Thread(target=collection_loop, daemon=True)
        collection_thread.start()
        
        logger.info(f"✅ Continuous collection started (interval: {interval}s)")
    
    def stop(self):
        """Stop continuous collection"""
        self.running = False
        logger.info("⏹️  Data collection stopped")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Web Data Collector for SIEM')
    parser.add_argument('--mode', choices=['once', 'continuous'], default='continuous',
                       help='Collection mode')
    parser.add_argument('--interval', type=int, default=30,
                       help='Collection interval in seconds (for continuous mode)')
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("  🌐 REAL-TIME WEB DATA COLLECTOR")
    logger.info("="*60)
    
    # Initialize SIEM
    config = ConfigManager()
    siem = SIEMCore(config)
    siem.start()
    
    # Initialize collector
    collector = WebDataCollector(siem)
    
    if args.mode == 'once':
        # Run once
        logger.info("\n🔄 Running one-time collection...")
        collector.simulate_live_traffic()
        collector.collect_honeypot_data()
        collector.collect_threat_feeds()
        collector.collect_github_security_advisories()
        
        sample_ips = ['192.0.2.1', '10.0.1.50', '203.0.113.100']
        collector.collect_abuse_ipdb(sample_ips)
        
        logger.info("\n✅ Collection complete!")
        
    else:
        # Continuous mode
        logger.info(f"\n🔄 Starting continuous collection (interval: {args.interval}s)")
        logger.info("Press Ctrl+C to stop\n")
        
        collector.start_continuous_collection(args.interval)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Stopping collection...")
            collector.stop()
    
    # Show final stats
    stats = siem.get_stats()
    logger.info("\n" + "="*60)
    logger.info("  📊 FINAL STATISTICS")
    logger.info("="*60)
    logger.info(f"Events Processed: {siem.event_processor.processed_count}")
    logger.info(f"Total Alerts: {stats['alerts_count']}")
    logger.info(f"Rules Active: {siem.threat_detector.rules_engine.get_stats()['total_rules']}")
    logger.info("="*60 + "\n")
    
    siem.stop()


if __name__ == "__main__":
    import random
    main()
