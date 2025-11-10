# 🛡️ Real-Time SIEM Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.x-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

A comprehensive Security Information and Event Management (SIEM) system for analyzing Apache access logs, detecting anomalies, and identifying potential security threats in real-time.

## 🚀 Live Demo

[![View Artifact](https://img.shields.io/badge/View%20Artifact-%230077B5.svg?style=for-the-badge&logo=claude&logoColor=white)](https://claude.ai/public/artifacts/61aa2497-7d5b-4782-8796-f5a2d0c7571a)


## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Detection Rules](#detection-rules)
- [Project Structure](#project-structure)
- [Sample Data](#sample-data)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🔍 **Advanced Analysis Capabilities**

- **Log Ingestion & Normalization**: Parse Apache Combined Log Format with automatic validation
- **Real-Time Processing**: Instant analysis of uploaded log files
- **Anomaly Detection**: Multi-factor threat scoring (0-100 scale)
- **Attack Pattern Recognition**:
  - Brute force/credential stuffing detection
  - Path scanning and reconnaissance
  - Webshell probe identification
  - Suspicious user agent detection
- **Time-Series Analysis**: Traffic burst detection with statistical thresholds
- **Interactive Dashboards**: Four specialized views (Overview, Anomalies, Attacks, Timeline)
- **Export Functionality**: Download reports in Markdown and CSV formats

### 📊 **Visualization Components**

- Request volume timeline charts
- Status code distribution (pie charts)
- Top source IPs (bar charts)
- Real-time console logging with color-coded severity
- Threat severity indicators (CRITICAL/HIGH/MEDIUM)

### 🎯 **Detection Rules**

| Rule | Threshold | Severity |
|------|-----------|----------|
| High Request Rate | >100 requests from single IP | Medium-High |
| Path Scanning | >50 distinct paths | Medium |
| Brute Force | >10 failed auth attempts | High |
| Known Exploits | `/wp-admin`, `/shell`, `/phpmyadmin` | High |
| Suspicious User Agents | `sqlmap`, `nikto`, `nmap`, `curl` | Low-Medium |
| High Failure Rate | >50% failed requests | Medium |

## 🏗️ Architecture

```
┌─────────────────┐
│   Log Upload    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parser Engine  │
│  (Apache CLF)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Quality   │
│     Checks      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Analysis Pipeline              │
│  ┌─────────────────────────────┐    │
│  │ 1. Statistical Analysis     │    │
│  │ 2. Anomaly Detection        │    │
│  │ 3. Pattern Recognition      │    │
│  │ 4. Time-Series Analysis     │    │
│  │ 5. Threat Scoring           │    │
│  └─────────────────────────────┘    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Visualization               │
│  ┌──────────┬──────────┬─────────┐  │
│  │ Overview │ Anomalies│ Attacks │  │
│  └──────────┴──────────┴─────────┘  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Export Reports │
│  (MD/CSV/JSON)  │
└─────────────────┘
```

## 🔧 Installation

### Prerequisites

- Node.js 16.x or higher
- Python 3.8+ (for standalone script)
- npm or yarn

### Web Interface Setup

1. **Clone the repository**
```bash
git clone https://github.com/Arvind-55555/Real-Time-S.I.E.M-System/siem-analysis-platform.git
cd siem-analysis-platform
```

2. **Install dependencies**
```bash
npm install
```

3. **Start the development server**
```bash
npm start
```

4. **Open your browser**
```
http://localhost:3000
```

### Python Standalone Script

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Run the analyzer**
```bash
python siem_analyzer.py --input access.log --output report.md
```

## 📖 Usage

### Web Interface

1. **Upload Log File**: Click the upload area and select your Apache access log file
2. **Analyze**: Click the "Analyze" button to start processing
3. **Review Results**: Navigate through tabs to explore findings
4. **Export Reports**: Download Markdown reports or CSV files for further analysis

### Command Line Interface

```bash
# Basic analysis
python siem_analyzer.py --input access.log

# With custom output
python siem_analyzer.py --input access.log --output custom_report.md

# JSON output
python siem_analyzer.py --input access.log --format json --output results.json

# Adjust anomaly threshold
python siem_analyzer.py --input access.log --threshold 50
```

## 📁 Project Structure

```
siem-analysis-platform/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── SIEMAnalyzer.jsx       # Main React component
│   │   ├── LogUploader.jsx
│   │   ├── AnalysisConsole.jsx
│   │   └── DashboardTabs.jsx
│   ├── utils/
│   │   ├── logParser.js           # Apache log parser
│   │   ├── anomalyDetector.js     # Anomaly detection engine
│   │   ├── attackDetector.js      # Attack pattern recognition
│   │   └── reportGenerator.js     # Report export utilities
│   ├── App.js
│   └── index.js
├── scripts/
│   ├── siem_analyzer.py           # Standalone Python script
│   ├── generate_sample_logs.py    # Sample log generator
│   └── test_analyzer.py           # Unit tests
├── sample-data/
│   ├── normal_traffic.log
│   ├── attack_scenario_1.log      # Brute force example
│   └── attack_scenario_2.log      # Path scanning example
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DETECTION_RULES.md
│   └── API_REFERENCE.md
├── tests/
│   ├── test_parser.js
│   ├── test_anomaly_detection.js
│   └── test_attack_patterns.js
├── .gitignore
├── package.json
├── requirements.txt
├── LICENSE
└── README.md
```

## 📊 Sample Data

The repository includes sample log files for testing:

### Normal Traffic
```
192.168.1.100 - - [10/Nov/2025:14:32:10 +0000] "GET /index.php HTTP/1.1" 200 2326 "-" "Mozilla/5.0"
192.168.1.101 - - [10/Nov/2025:14:32:11 +0000] "GET /about.html HTTP/1.1" 200 1542 "-" "Chrome/90.0"
```

### Attack Scenario (Brute Force)
```
203.0.113.45 - - [10/Nov/2025:14:35:01 +0000] "POST /wp-login.php HTTP/1.1" 401 - "-" "sqlmap/1.0"
203.0.113.45 - - [10/Nov/2025:14:35:02 +0000] "POST /wp-login.php HTTP/1.1" 401 - "-" "sqlmap/1.0"
203.0.113.45 - - [10/Nov/2025:14:35:03 +0000] "POST /wp-login.php HTTP/1.1" 401 - "-" "sqlmap/1.0"
```

### Generate Custom Logs
```bash
python scripts/generate_sample_logs.py --count 10000 --output custom.log --attack-ratio 0.1
```

## 🔬 Detection Rules

### Anomaly Scoring Algorithm

```python
score = 0
reasons = []

# High request rate (>100 requests)
if requests > 100:
    score += 30
    reasons.append("High request volume")

# Path scanning (>50 distinct paths)
if distinct_paths > 50:
    score += 40
    reasons.append("Path scanning detected")

# High failure rate (>50%)
if fail_rate > 0.5:
    score += 20
    reasons.append("High failure rate")

# Brute force (>20 failures)
if failures > 20:
    score += 10
    reasons.append("Possible brute-force")

threat_score = min(score, 100)
```

### Attack Patterns

#### Brute Force Detection
```javascript
const authPaths = ['/login', '/wp-login.php', '/admin', '/auth'];
const threshold = 10; // failures per IP

if (failureCount > threshold) {
  flagAsBruteForce(ip);
}
```

#### Path Scanning Detection
```javascript
const distinctPathThreshold = 50;

if (distinctPaths.size > distinctPathThreshold) {
  flagAsScanning(ip);
}
```

## 🧪 Testing

### Run Unit Tests
```bash
npm test
```

### Run Python Tests
```bash
pytest tests/
```

### Coverage Report
```bash
npm run test:coverage
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t siem-analyzer .

# Run container
docker run -p 3000:3000 siem-analyzer
```

### Docker Compose

```bash
docker-compose up -d
```

## 🔮 Future Enhancements

- [ ] GeoIP integration for location-based analysis
- [ ] Machine learning models (IsolationForest, LSTM)
- [ ] Real-time log streaming (WebSocket support)
- [ ] Multi-source log aggregation
- [ ] Email/Slack alerting system
- [ ] Custom rule builder interface
- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] User authentication and multi-tenancy
- [ ] REST API for programmatic access
- [ ] Elasticsearch integration
- [ ] Threat intelligence feeds integration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Arvind** - *Initial work* - [YourGitHub](https://github.com/Arvind-55555)

## 🙏 Acknowledgments

- Inspired by industry-standard SIEM tools (Splunk, ELK Stack)
- Built with React and Recharts for visualization
- Apache Combined Log Format specification
- OWASP Top 10 security risks


## 🔗 Related Projects

- [Splunk](https://www.splunk.com/) - Enterprise SIEM solution
- [ELK Stack](https://www.elastic.co/elastic-stack) - Open-source log analysis
- [Graylog](https://www.graylog.org/) - Log management platform
- [OSSEC](https://www.ossec.net/) - Host-based intrusion detection

---

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the cybersecurity community
