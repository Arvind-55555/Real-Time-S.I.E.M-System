# 🎯 SIEM Quick Command Reference

## 🚀 Setup & Installation

```bash
# Complete production setup (automated)
bash setup_production.sh

# Manual setup
pip3 install -r requirements.txt
docker-compose up -d
python3 scripts/ml_anomaly_detector.py
```

## 📊 Start Services

```bash
# Start ELK stack
docker-compose up -d

# Stop ELK stack
docker-compose down

# View logs
docker-compose logs -f elasticsearch
docker-compose logs -f kibana
```

## 🌐 Data Collection

```bash
# Continuous real-time collection (recommended)
python3 scripts/collect_web_data.py --mode continuous --interval 30

# One-time collection
python3 scripts/collect_web_data.py --mode once

# Custom interval
python3 scripts/collect_web_data.py --mode continuous --interval 60
```

## 🎨 Dashboards

```bash
# Live SIEM dashboard
python3 scripts/run_live_dashboard.py
# Open: http://localhost:8080

# Original dashboard (no auto-events)
python3 scripts/run_dashboard.py

# Different port
python3 scripts/run_live_dashboard.py --port 9090
```

## 🖥️ Monitoring

```bash
# Interactive demo
python3 scripts/demo.py

# Simulate events
python3 scripts/monitor.py --simulate --count 50 --interval 2

# Monitor log file
python3 scripts/monitor.py --file data/sample_logs.txt --verbose

# Follow log file (like tail -f)
python3 scripts/monitor.py --file /var/log/syslog --follow --tail
```

## 🤖 Machine Learning

```bash
# Train and test ML model
python3 scripts/ml_anomaly_detector.py

# Use ML in code
python3 << EOF
from scripts.ml_anomaly_detector import MLAnomalyDetector

detector = MLAnomalyDetector()
detector.load_model('models/ml_anomaly_detector.pkl')

event = {'failed_logins': 100, 'bytes_sent': 900000000}
result = detector.detect_anomaly(event)
print(f"Anomaly: {result['is_anomaly']}")
