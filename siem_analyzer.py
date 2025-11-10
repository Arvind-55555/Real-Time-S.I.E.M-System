#!/usr/bin/env python3
"""
SIEM Log Analyzer - Standalone Python Script
Analyzes Apache access logs for security threats and anomalies
"""

import re
import json
import argparse
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
import sys


class LogEntry:
    """Represents a single Apache log entry"""
    
    def __init__(self, ip, timestamp, method, path, status, size, referer, user_agent):
        self.ip = ip
        self.timestamp = timestamp
        self.method = method
        self.path = path
        self.status = status
        self.size = size
        self.referer = referer
        self.user_agent = user_agent


class SIEMAnalyzer:
    """Main SIEM analysis engine"""
    
    # Detection patterns
    AUTH_PATHS = ['/login', '/wp-login.php', '/admin', '/auth', '/signin']
    SHELL_PATTERNS = ['/shell', '/wp-admin', '/phpmyadmin', '/xmlrpc.php', 
                     '/etc/passwd', '/.env', '/config.php', '/.git']
    SUSPICIOUS_UAS = ['sqlmap', 'nikto', 'nmap', 'masscan', 'acunetix', 
                     'nessus', 'openvas', 'metasploit']
    
    def __init__(self, threshold=30):
        self.threshold = threshold
        self.logs = []
        self.ip_stats = defaultdict(lambda: {
            'requests': 0,
            'distinct_paths': set(),
            'failures': 0,
            'total_size': 0,
            'methods': set(),
            'timestamps': []
        })
        
    def parse_log_line(self, line):
        """Parse Apache Combined Log Format"""
        pattern = r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\S+) "([^"]*)" "([^"]*)"'
        match = re.match(pattern, line)
        
        if match:
            ip, timestamp, method, path, status, size, referer, ua = match.groups()
            return LogEntry(
                ip=ip,
                timestamp=timestamp,
                method=method,
                path=path,
                status=int(status),
                size=0 if size == '-' else int(size),
                referer=referer,
                user_agent=ua
            )
        return None
    
    def ingest_logs(self, filepath):
        """Read and parse log file"""
        print(f"[INFO] Reading log file: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        print(f"[INFO] Parsing {len(lines)} log entries...")
        
        parsed = 0
        for line in lines:
            entry = self.parse_log_line(line.strip())
            if entry:
                self.logs.append(entry)
                parsed += 1
                
                # Update statistics
                stats = self.ip_stats[entry.ip]
                stats['requests'] += 1
                stats['distinct_paths'].add(entry.path)
                if entry.status >= 400:
                    stats['failures'] += 1
                stats['total_size'] += entry.size
                stats['methods'].add(entry.method)
                stats['timestamps'].append(entry.timestamp)
        
        print(f"[SUCCESS] Successfully parsed {parsed}/{len(lines)} entries")
        print(f"[INFO] Unique IPs: {len(self.ip_stats)}")
        return parsed
    
    def detect_anomalies(self):
        """Detect anomalous IP behavior"""
        print("\n[INFO] Running anomaly detection...")
        
        anomalies = []
        
        for ip, stats in self.ip_stats.items():
            score = 0
            reasons = []
            
            requests = stats['requests']
            distinct_paths = len(stats['distinct_paths'])
            fail_rate = stats['failures'] / requests if requests > 0 else 0
            
            # High request rate
            if requests > 100:
                score += 30
                reasons.append(f"High request volume ({requests})")
            
            # Path scanning
            if distinct_paths > 50:
                score += 40
                reasons.append(f"Path scanning ({distinct_paths} paths)")
            
            # High failure rate
            if fail_rate > 0.5:
                score += 20
                reasons.append(f"High failure rate ({fail_rate*100:.1f}%)")
            
            # Brute force indicator
            if stats['failures'] > 20:
                score += 10
                reasons.append(f"Multiple failures ({stats['failures']})")
            
            if score >= self.threshold:
                anomalies.append({
                    'ip': ip,
                    'score': min(score, 100),
                    'requests': requests,
                    'distinct_paths': distinct_paths,
                    'fail_rate': f"{fail_rate*100:.1f}%",
                    'reasons': ', '.join(reasons)
                })
        
        anomalies.sort(key=lambda x: x['score'], reverse=True)
        print(f"[WARNING] Detected {len(anomalies)} anomalous IPs")
        
        return anomalies
    
    def detect_attack_patterns(self):
        """Detect specific attack patterns"""
        print("\n[INFO] Detecting attack patterns...")
        
        patterns = {
            'brute_force': [],
            'webshell': [],
            'suspicious_ua': []
        }
        
        ip_auth_failures = defaultdict(int)
        
        for log in self.logs:
            # Brute force detection
            if any(path in log.path for path in self.AUTH_PATHS) and log.status >= 400:
                ip_auth_failures[log.ip] += 1
            
            # Webshell detection
            if any(pattern in log.path.lower() for pattern in self.SHELL_PATTERNS):
                patterns['webshell'].append({
                    'ip': log.ip,
                    'path': log.path,
                    'timestamp': log.timestamp
                })
            
            # Suspicious UA detection
            if any(ua in log.user_agent.lower() for ua in self.SUSPICIOUS_UAS):
                patterns['suspicious_ua'].append({
                    'ip': log.ip,
                    'ua': log.user_agent,
                    'path': log.path
                })
        
        # Filter brute force attempts
        for ip, count in ip_auth_failures.items():
            if count > 10:
                patterns['brute_force'].append({
                    'ip': ip,
                    'attempts': count
                })
        
        print(f"[WARNING] Brute force attempts: {len(patterns['brute_force'])}")
        print(f"[WARNING] Webshell probes: {len(patterns['webshell'])}")
        print(f"[WARNING] Suspicious UAs: {len(patterns['suspicious_ua'])}")
        
        return patterns
    
    def analyze_time_series(self):
        """Analyze traffic patterns over time"""
        print("\n[INFO] Analyzing time series data...")
        
        time_slots = defaultdict(int)
        
        for log in self.logs:
            # Extract minute-level timestamp
            try:
                dt = datetime.strptime(log.timestamp, '%d/%b/%Y:%H:%M:%S %z')
                minute = dt.strftime('%Y-%m-%d %H:%M')
                time_slots[minute] += 1
            except:
                continue
        
        # Calculate average and detect bursts
        if time_slots:
            avg_requests = sum(time_slots.values()) / len(time_slots)
            bursts = [(time, count) for time, count in time_slots.items() 
                     if count > avg_requests * 3]
            
            print(f"[INFO] Average requests per minute: {avg_requests:.1f}")
            print(f"[WARNING] Detected {len(bursts)} traffic bursts")
            
            return sorted(time_slots.items()), bursts
        
        return [], []
    
    def generate_report(self, output_file, format='markdown'):
        """Generate analysis report"""
        print(f"\n[INFO] Generating {format} report...")
        
        anomalies = self.detect_anomalies()
        patterns = self.detect_attack_patterns()
        time_series, bursts = self.analyze_time_series()
        
        if format == 'markdown':
            self._generate_markdown_report(output_file, anomalies, patterns, bursts)
        elif format == 'json':
            self._generate_json_report(output_file, anomalies, patterns, bursts)
        
        print(f"[SUCCESS] Report saved to {output_file}")
    
    def _generate_markdown_report(self, output_file, anomalies, patterns, bursts):
        """Generate Markdown report"""
        
        with open(output_file, 'w') as f:
            f.write("# SIEM Analysis Report\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write(f"- **Total Requests:** {len(self.logs):,}\n")
            f.write(f"- **Unique Source IPs:** {len(self.ip_stats)}\n")
            f.write(f"- **Anomalous IPs Detected:** {len(anomalies)}\n")
            f.write(f"- **Brute Force Attempts:** {len(patterns['brute_force'])}\n")
            f.write(f"- **Webshell Probes:** {len(patterns['webshell'])}\n")
            f.write(f"- **Traffic Bursts:** {len(bursts)}\n\n")
            
            # Top IPs
            f.write("## Top 10 Source IPs\n\n")
            top_ips = sorted(self.ip_stats.items(), 
                           key=lambda x: x[1]['requests'], 
                           reverse=True)[:10]
            for i, (ip, stats) in enumerate(top_ips, 1):
                f.write(f"{i}. **{ip}** - {stats['requests']:,} requests\n")
            f.write("\n")
            
            # Anomalies
            if anomalies:
                f.write("## Anomalous IPs (Threat Score ≥ 30)\n\n")
                for anom in anomalies[:20]:
                    severity = "🔴 CRITICAL" if anom['score'] >= 70 else \
                              "🟠 HIGH" if anom['score'] >= 50 else "🟡 MEDIUM"
                    f.write(f"### {anom['ip']} - {severity}\n\n")
                    f.write(f"- **Threat Score:** {anom['score']}/100\n")
                    f.write(f"- **Requests:** {anom['requests']:,}\n")
                    f.write(f"- **Distinct Paths:** {anom['distinct_paths']}\n")
                    f.write(f"- **Failure Rate:** {anom['fail_rate']}\n")
                    f.write(f"- **Reasons:** {anom['reasons']}\n\n")
            
            # Attack Patterns
            f.write("## Attack Patterns Detected\n\n")
            
            f.write("### Brute Force Attempts\n\n")
            if patterns['brute_force']:
                for bf in patterns['brute_force'][:10]:
                    f.write(f"- **{bf['ip']}:** {bf['attempts']} failed authentication attempts\n")
            else:
                f.write("*None detected*\n")
            f.write("\n")
            
            f.write("### Webshell Probes\n\n")
            if patterns['webshell']:
                for ws in patterns['webshell'][:10]:
                    f.write(f"- **{ws['ip']}** attempted access to `{ws['path']}`\n")
            else:
                f.write("*None detected*\n")
            f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("### Immediate Actions\n\n")
            if anomalies:
                f.write(f"1. **Block top {min(5, len(anomalies))} anomalous IPs**\n")
                for anom in anomalies[:5]:
                    f.write(f"   - `{anom['ip']}` (Score: {anom['score']})\n")
            f.write("2. **Implement rate limiting** (500 requests per 10 minutes)\n")
            f.write("3. **Review authentication logs** for potential compromise\n\n")
            
            f.write("### Detection Rules to Deploy\n\n")
            f.write("- Alert on >20 auth failures in 5 minutes\n")
            f.write("- Alert on >50 distinct paths from single IP in 10 minutes\n")
            f.write("- Block known scanner user agents\n")
            f.write("- Monitor for webshell access patterns\n\n")
            
            f.write("### Further Investigation\n\n")
            f.write("- Correlate with firewall and IDS/IPS logs\n")
            f.write("- Check for data exfiltration patterns\n")
            f.write("- Review affected endpoints for vulnerabilities\n")
            f.write("- Implement GeoIP filtering if applicable\n")
    
    def _generate_json_report(self, output_file, anomalies, patterns, bursts):
        """Generate JSON report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_requests': len(self.logs),
                'unique_ips': len(self.ip_stats),
                'anomalous_ips': len(anomalies),
                'brute_force_attempts': len(patterns['brute_force']),
                'webshell_probes': len(patterns['webshell']),
                'traffic_bursts': len(bursts)
            },
            'anomalies': anomalies,
            'attack_patterns': patterns,
            'bursts': [{'time': t, 'count': c} for t, c in bursts]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(
        description='SIEM Log Analyzer - Detect security threats in Apache logs'
    )
    parser.add_argument('--input', '-i', required=True, 
                       help='Path to Apache access log file')
    parser.add_argument('--output', '-o', default='siem_report.md',
                       help='Output report file (default: siem_report.md)')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'], 
                       default='markdown',
                       help='Output format (default: markdown)')
    parser.add_argument('--threshold', '-t', type=int, default=30,
                       help='Anomaly detection threshold (default: 30)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input).exists():
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)
    
    print("=" * 60)
    print("        SIEM LOG ANALYZER")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SIEMAnalyzer(threshold=args.threshold)
    
    # Ingest logs
    parsed = analyzer.ingest_logs(args.input)
    
    if parsed == 0:
        print("[ERROR] No valid log entries found")
        sys.exit(1)
    
    # Generate report
    analyzer.generate_report(args.output, format=args.format)
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()