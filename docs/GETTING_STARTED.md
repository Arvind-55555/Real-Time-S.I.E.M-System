# 🛡️ Real-Time SIEM System - Getting Started

## 🎯 What You Have Now

✅ **Complete SIEM System** moved to root directory  
✅ **All dependencies** cleaned and optimized  
✅ **Web Dashboard** for visualization  
✅ **CLI Tools** for monitoring  
✅ **Sample Data** for testing  
✅ **Comprehensive Documentation**

---

## 🚀 Start in 30 Seconds

```bash
cd /home/arvind/Downloads/projects/Working/S.I.E.M

# Quick start (automatic setup + demo)
bash quickstart.sh

# OR manually:
pip3 install -r requirements.txt
python3 scripts/demo.py
```

---

## 📊 Visualization Options

### 1️⃣ Web Dashboard (Best for Beginners)

```bash
python3 scripts/run_dashboard.py
```

Then open: **http://localhost:8080**

**You'll see:**
- Real-time alerts with color coding
- System statistics
- Auto-refreshing display
- REST API endpoints

---

### 2️⃣ Interactive Demo

```bash
python3 scripts/demo.py
```

**What happens:**
- Processes 10 sample security events
- Shows threat detection in action
- Displays summary statistics
- Perfect for understanding the workflow

---

### 3️⃣ CLI Monitor (For Terminal Lovers)

```bash
# Simulate random events
python3 scripts/monitor.py --simulate

# Monitor a log file
python3 scripts/monitor.py --file data/sample_logs.txt --verbose
```

---

## 🔄 Complete Workflow Example

### Terminal 1: Start Dashboard
```bash
python3 scripts/run_dashboard.py
```

### Terminal 2: Generate Events
```bash
python3 scripts/monitor.py --simulate --count 100 --interval 1
```

### Browser: Watch Results
Open: **http://localhost:8080**

---

## 📁 What's Where

```
S.I.E.M/
├── 📘 README.md                  # Complete documentation
├── 📗 DEVELOPMENT_GUIDE.md       # Development workflow
├── 📙 SETUP_COMPLETE.md          # Setup verification
├── 🚀 quickstart.sh              # One-command setup
│
├── 📂 scripts/                   # 👈 START HERE
│   ├── demo.py                   # Interactive demo
│   ├── run_dashboard.py          # Web dashboard
│   └── monitor.py                # Real-time monitor
│
├── 📂 config/                    # Configuration files
│   ├── siem_config.yaml          # Main config
│   └── detection_rules.yaml      # Detection rules
│
├── 📂 data/                      # Sample data
│   └── sample_logs.txt           # Test logs
│
├── 📂 src/realtime_siem/         # Main package
│   ├── core/                     # SIEM engine
│   ├── detection/                # Threat detection
│   ├── parsers/                  # Log parsers
│   └── alerts/                   # Alert management
│
└── 📂 logs/                      # Runtime logs
```

---

## 🎓 Learning Path

### Day 1: Understanding
1. Run demo: `python3 scripts/demo.py`
2. Read output carefully
3. Check `DEVELOPMENT_GUIDE.md`

### Day 2: Visualization
1. Start dashboard: `python3 scripts/run_dashboard.py`
2. Open http://localhost:8080
3. Run monitor in another terminal
4. Watch alerts appear in real-time

### Day 3: Customization
1. Edit `config/detection_rules.yaml`
2. Add your own rules
3. Test with sample data
4. See alerts in dashboard

### Day 4: Integration
1. Point to your log files
2. Configure parsers
3. Set up Elasticsearch (optional)
4. Create custom dashboards

---

## 🎨 Dashboard Preview

When you open http://localhost:8080, you'll see:

```
╔════════════════════════════════════════════╗
║  🛡️ SIEM Dashboard                         ║
║  Real-time Security Monitoring             ║
╠════════════════════════════════════════════╣
║                                            ║
║  📊 STATISTICS                             ║
║  ┌─────────────┬─────────────┬──────────┐  ║
║  │ Total: 45   │ Open: 12    │ Events:  │  ║
║  │ Alerts      │ Alerts      │ 1,234    │  ║
║  └─────────────┴─────────────┴──────────┘  ║
║                                            ║
║  🚨 RECENT ALERTS                          ║
║  ┌──────────────────────────────────────┐  ║
║  │ [CRITICAL] Data Exfiltration         │  ║
║  │ User: charlie | IP: 10.0.1.52        │  ║
║  │ 150MB uploaded to external server    │  ║
║  └──────────────────────────────────────┘  ║
║  ┌──────────────────────────────────────┐  ║
║  │ [HIGH] Multiple Failed Logins        │  ║
║  │ User: admin | IP: 203.0.113.1        │  ║
║  │ 8 failed attempts in 2 minutes       │  ║
║  └──────────────────────────────────────┘  ║
║                                            ║
╚════════════════════════════════════════════╝
```

---

## 🧪 Quick Test

Verify everything works:

```bash
# Run system test
python3 test_complete_system.py

# Expected output:
# ============================================================
# ALL TESTS PASSED! ✓
# ============================================================
```

---

## 💡 Common Use Cases

### Monitor SSH Login Attempts
```bash
tail -f /var/log/auth.log | python3 scripts/monitor.py --file - --follow
```

### Process Application Logs
```bash
python3 scripts/monitor.py --file /var/log/myapp.log --follow --tail
```

### Test Custom Rules
```python
# Edit config/detection_rules.yaml, then:
python3 -c "
from realtime_siem.core.siem_engine import SIEMCore
siem = SIEMCore()
siem.start()
result = siem.process_log('{\"test\": \"event\"}', 'json')
print('Threats detected:', len(result.get('threats', [])))
"
```

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **README.md** | Complete system documentation |
| **DEVELOPMENT_GUIDE.md** | Development workflow & API |
| **SETUP_COMPLETE.md** | Setup verification & commands |
| **GETTING_STARTED.md** | This quick start guide |

---

## 🆘 Troubleshooting

**Problem: ModuleNotFoundError**
```bash
pip3 install -r requirements.txt
```

**Problem: Dashboard won't start**
```bash
# Check if port 8080 is free
lsof -i :8080
# Or use different port
python3 scripts/run_dashboard.py --port 8888
```

**Problem: No alerts appearing**
```bash
# Test with known bad data
python3 -c "
from realtime_siem.core.siem_engine import SIEMCore
siem = SIEMCore()
siem.start()
result = siem.process_log('{\"failed_logins\": 100}', 'json')
print('Threats:', result.get('threats', []))
"
```

---

## ✅ Next Steps

1. **NOW**: `python3 scripts/run_dashboard.py`
2. **Browser**: Open http://localhost:8080
3. **New Terminal**: `python3 scripts/monitor.py --simulate`
4. **Watch**: See alerts appear in dashboard
5. **Learn**: Read DEVELOPMENT_GUIDE.md
6. **Customize**: Edit config/detection_rules.yaml
7. **Deploy**: Follow README.md for production

---

## 🎉 You're Ready!

**The system is fully functional and ready for:**
- ✅ Local development
- ✅ Testing and learning
- ✅ Visualization and monitoring
- ✅ Customization and extension
- ✅ Production deployment

**Start with:** `python3 scripts/run_dashboard.py`

Then explore the scripts, customize the rules, and build your security monitoring solution!

---

*For detailed documentation, see README.md and DEVELOPMENT_GUIDE.md*
