# SIEM System - Local Development & Visualization Guide

## Quick Start (5 Minutes)

### 1. Installation
```bash
# Navigate to project directory
cd /home/arvind/Downloads/projects/Working/S.I.E.M

# Install dependencies
pip install -r requirements.txt

# Test installation
python3 test_complete_system.py
```

### 2. Run Demo
```bash
# Run interactive demo with sample data
python3 scripts/demo.py
```

### 3. Launch Web Dashboard
```bash
# Start web dashboard on http://localhost:8080
python3 scripts/run_dashboard.py
```

Open browser to: **http://localhost:8080**

---

## Development Workflow

### Step 1: System Architecture Understanding

```
┌─────────────────────────────────────────────────────────────┐
│                    SIEM WORKFLOW                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Log Source                                                  │
│      │                                                       │
│      ├──▶ Parser (Syslog/JSON/Generic)                     │
│      │         │                                             │
│      │         ├──▶ Event Processor (Enrich/Normalize)     │
│      │         │         │                                   │
│      │         │         ├──▶ Threat Detector               │
│      │         │         │    ├── Rules Engine              │
│      │         │         │    └── Anomaly Detector          │
│      │         │         │              │                    │
│      │         │         │              ├──▶ Alert Manager  │
│      │         │         │              │                    │
│      │         │         └──▶ Correlation Engine            │
│      │         │                        │                    │
│      │         └──▶ Elasticsearch (Storage)                 │
│      │                                                       │
│      └──▶ Visualization (Dashboard/Kibana)                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Development Environment Setup

```bash
# Create Python virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Verify installation
python3 -c "from realtime_siem import SIEMCore; print('✓ Import successful')"
```

### Step 3: Configuration

Edit `config/siem_config.yaml`:

```yaml
elasticsearch:
  host: localhost
  port: 9200
  enabled: false  # Set to true when Elasticsearch is running

logging:
  level: DEBUG    # Use DEBUG for development
  file: logs/siem.log

detection:
  anomaly_threshold: 2.0  # Lower for more sensitive detection
```

### Step 4: Run Development Server

```bash
# Terminal 1: Run dashboard
python3 scripts/run_dashboard.py --port 8080

# Terminal 2: Run real-time monitor
python3 scripts/monitor.py --simulate --count 0 --interval 2

# Terminal 3: Process sample logs
python3 scripts/monitor.py --file data/sample_logs.txt --follow
```

---

## Visualization Options

### Option 1: Built-in Web Dashboard (Easiest)

**Start Dashboard:**
```bash
python3 scripts/run_dashboard.py
```

**Access:** http://localhost:8080

**Features:**
- Real-time alert display
- System statistics
- Auto-refresh every 5 seconds
- Color-coded severity levels
- REST API endpoints

**API Endpoints:**
- `GET /` - Dashboard UI
- `GET /api/stats` - System statistics (JSON)
- `GET /api/alerts` - All alerts (JSON)

### Option 2: CLI Real-time Monitor

**Basic usage:**
```bash
# Simulate random events
python3 scripts/monitor.py --simulate

# Monitor a log file
python3 scripts/monitor.py --file logs/siem.log --follow --tail

# Process sample data
python3 scripts/monitor.py --file data/sample_logs.txt --verbose
```

**Advanced options:**
```bash
# Simulate 100 events with 0.5s interval
python3 scripts/monitor.py --simulate --count 100 --interval 0.5

# Show full event details and statistics
python3 scripts/monitor.py --simulate --verbose --stats
```

### Option 3: Elasticsearch + Kibana (Production)

**Start services:**
```bash
# Start Elasticsearch and Kibana
docker-compose up -d

# Wait for services to start (30-60 seconds)
docker-compose ps

# Verify Elasticsearch
curl http://localhost:9200

# Access Kibana
# Open http://localhost:5601
```

**Configure SIEM:**
```yaml
# config/siem_config.yaml
elasticsearch:
  host: localhost
  port: 9200
  index: siem-events
  enabled: true
```

**Run SIEM:**
```bash
python3 scripts/demo.py
```

**View in Kibana:**
1. Open http://localhost:5601
2. Go to Stack Management → Index Patterns
3. Create pattern: `siem-events*`
4. Go to Discover to view events
5. Create dashboards in Dashboard section

### Option 4: Custom Integration

**Python API:**
```python
from realtime_siem.core.siem_engine import SIEMCore

siem = SIEMCore()
siem.start()

# Process logs
result = siem.process_log('{"user": "admin", "action": "login"}', 'json')

# Get alerts
alerts = siem.alert_manager.get_alerts(severity='high', status='open')

# Export to your visualization tool
for alert in alerts:
    # Send to your dashboard
    send_to_dashboard(alert)
```

---

## Testing & Validation

### Run All Tests
```bash
# Comprehensive system test
python3 test_complete_system.py

# Unit tests (if available)
python3 -m pytest tests/ -v

# Test specific component
python3 -c "
from realtime_siem.detection.rules_engine import RulesEngine
engine = RulesEngine()
print(f'Rules loaded: {len(engine.rules)}')
"
```

### Test Detection Rules
```bash
# Validate rules syntax
siem validate-rules --rule-file config/detection_rules.yaml

# Test with sample data
python3 -c "
from realtime_siem.core.siem_engine import SIEMCore
siem = SIEMCore()
siem.start()

# Test failed login detection
log = '{\"failed_logins\": 10, \"user\": \"admin\"}'
result = siem.process_log(log, 'json')
print(f'Threats detected: {len(result.get(\"threats\", []))}')
"
```

### Performance Testing
```bash
# Generate and process 1000 events
python3 -c "
import time
from realtime_siem.core.siem_engine import SIEMCore

siem = SIEMCore()
siem.start()

start = time.time()
for i in range(1000):
    siem.process_log('{\"event\": \"test\"}', 'json')
elapsed = time.time() - start

print(f'Processed 1000 events in {elapsed:.2f}s')
print(f'Rate: {1000/elapsed:.0f} events/second')
"
```

---

## Common Development Tasks

### Add Custom Parser

**Create parser:**
```python
# src/realtime_siem/parsers/custom_parser.py
from .log_parser import LogParser
from datetime import datetime

class CustomParser(LogParser):
    def parse(self, log_line: str):
        # Your parsing logic
        return {
            'message': log_line,
            'type': 'custom',
            'timestamp': datetime.utcnow().isoformat(),
            # Add your custom fields
        }
```

**Register parser:**
```python
from realtime_siem.core.siem_engine import SIEMCore
from realtime_siem.parsers.custom_parser import CustomParser

siem = SIEMCore()
siem.parsers['custom'] = CustomParser()
```

### Add Custom Detection Rule

**Via YAML:**
```yaml
# config/detection_rules.yaml
rules:
  - name: "my_custom_rule"
    description: "Detect specific threat"
    condition: "event.custom_field > 100"
    severity: "high"
```

**Via Python:**
```python
from realtime_siem.detection.rules_engine import RulesEngine

engine = RulesEngine()
engine.add_rule({
    'name': 'custom_threshold',
    'field': 'request_size',
    'operator': '>',
    'threshold': 1000000,
    'severity': 'critical'
})
```

### Export Alerts

```python
import json
from realtime_siem.core.siem_engine import SIEMCore

siem = SIEMCore()
siem.start()

# Process some logs...

# Export alerts to JSON
alerts = siem.alert_manager.get_alerts()
with open('alerts_export.json', 'w') as f:
    json.dump(alerts, f, indent=2, default=str)
```

### Generate Reports

```python
from realtime_siem.core.siem_engine import SIEMCore
from datetime import datetime

siem = SIEMCore()
siem.start()

# Generate daily report
stats = siem.get_stats()
alert_stats = siem.alert_manager.get_stats()

report = f"""
SIEM Daily Report - {datetime.now().date()}
{'='*50}

System Status: {'Running' if stats['is_running'] else 'Stopped'}
Total Alerts: {alert_stats['total_alerts']}
Open Alerts: {alert_stats['open_alerts']}
Closed Alerts: {alert_stats['closed_alerts']}

Severity Distribution:
{json.dumps(alert_stats['severity_distribution'], indent=2)}

Events Processed: {siem.event_processor.processed_count}
Rules Active: {siem.threat_detector.rules_engine.get_stats()['total_rules']}
"""

print(report)

# Save to file
with open(f'reports/daily_{datetime.now().date()}.txt', 'w') as f:
    f.write(report)
```

---

## Troubleshooting

### Issue: No alerts appearing

**Solution:**
```bash
# Check if threats are being detected
python3 -c "
from realtime_siem.core.siem_engine import SIEMCore

siem = SIEMCore()
siem.start()

# Test with data that should trigger alert
log = '{\"failed_logins\": 10, \"source_ip\": \"192.0.2.1\"}'
result = siem.process_log(log, 'json')

print('Event:', result.get('event_id'))
print('Threats:', result.get('threats', []))
print('Alert count:', len(siem.alert_manager.alerts))
"
```

### Issue: Dashboard not updating

**Solution:**
```bash
# Check if SIEM is processing events
curl http://localhost:8080/api/stats

# Manually trigger events
python3 scripts/monitor.py --simulate --count 10
```

### Issue: Elasticsearch connection failed

**Solution:**
```bash
# Check Elasticsearch status
docker-compose ps elasticsearch
curl http://localhost:9200/_cluster/health

# Restart Elasticsearch
docker-compose restart elasticsearch

# Disable Elasticsearch in config if not needed
# config/siem_config.yaml
# elasticsearch:
#   enabled: false
```

---

## Next Steps for Production

### 1. Deploy with Docker
```bash
docker-compose up -d
```

### 2. Set up Log Collection
```bash
# Configure rsyslog to send logs to SIEM
# /etc/rsyslog.d/siem.conf
*.* @localhost:514

# Configure filebeat to send logs to SIEM
```

### 3. Configure Alerts
```bash
# Enable email notifications
# config/siem_config.yaml
notifications:
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    from: siem@yourcompany.com
    to: security@yourcompany.com
```

### 4. Set up Monitoring
```bash
# Monitor SIEM itself
python3 scripts/health_check.py --interval 60

# Set up alerts for SIEM downtime
```

### 5. Create Custom Dashboards
- Use Kibana for advanced visualization
- Create custom dashboards in `scripts/run_dashboard.py`
- Integrate with existing monitoring tools (Grafana, etc.)

---

## Resources

- **Documentation**: See `docs/` folder
- **Examples**: See `scripts/` folder
- **Sample Data**: See `data/` folder
- **Configuration**: See `config/` folder

**Happy SIEM Development! 🛡️**
