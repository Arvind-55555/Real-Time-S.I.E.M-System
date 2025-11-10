# 🚀 Quick Setup Guide

This guide will help you set up the SIEM Analysis Platform on your local machine or server.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 16.x or higher ([Download](https://nodejs.org/))
- **npm** or **yarn** package manager
- **Python** 3.8+ (for standalone analyzer)
- **Git** for version control
- **Docker** (optional, for containerized deployment)

## 🔧 Installation Methods

### Method 1: Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/Arvind-55555/Real-Time-S.I.E.M-System/siem-analysis-platform.git
cd siem-analysis-platform
```

#### 2. Install Node.js Dependencies

```bash
npm install
```

#### 3. Install Python Dependencies (Optional)

```bash
pip install -r requirements.txt
```

#### 4. Start Development Server

```bash
npm start
```

The application will open at `http://localhost:3000`

### Method 2: Docker Setup

#### 1. Build and Run with Docker

```bash
# Build the image
docker build -t siem-analyzer .

# Run the container
docker run -p 3000:80 siem-analyzer
```

#### 2. Using Docker Compose

```bash
docker-compose up -d
```

Access the application at `http://localhost:3000`

## 📂 Project Structure Setup

Create the following directory structure:

```bash
mkdir -p sample-data reports scripts src/components src/utils
```

## 🎯 Testing the Application

### 1. Generate Sample Logs

```bash
python scripts/generate_sample_logs.py --count 5000 --output sample-data/test.log
```

This creates a log file with:
- 4,500 normal requests
- 250 attack patterns (brute force, scanning, webshell probes)
- 250 DDoS burst traffic

### 2. Upload and Analyze

1. Open the web interface at `http://localhost:3000`
2. Click "Upload Apache Access Log"
3. Select `sample-data/test.log`
4. Click "Analyze"
5. Review the results in different tabs

### 3. Using Python CLI

```bash
python scripts/siem_analyzer.py --input sample-data/test.log --output reports/analysis.md
```

## 📊 Understanding the Output

### Web Interface Tabs

1. **Overview Tab**
   - Summary statistics
   - Request volume chart
   - Status code distribution
   - Top IPs and paths

2. **Anomalies Tab**
   - Threat-scored IPs
   - Severity levels (Critical/High/Medium)
   - Detection reasons
   - Export to CSV

3. **Attacks Tab**
   - Brute force attempts
   - Webshell probes
   - Suspicious user agents

4. **Timeline Tab**
   - Traffic bursts
   - Time-based patterns

### Generated Reports

Reports are saved in the `reports/` directory:
- `analysis.md` - Full Markdown report
- `anomalies.csv` - Anomalous IPs
- `attacks.json` - Attack patterns (if using JSON format)

## 🔐 Security Configuration

### Environment Variables

Create a `.env` file (not tracked in git):

```env
# API Configuration (if integrating with external services)
GEOIP_LICENSE_KEY=your_maxmind_key
ALERT_EMAIL=security@yourcompany.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Thresholds
ANOMALY_THRESHOLD=30
RATE_LIMIT_REQUESTS=500
RATE_LIMIT_WINDOW=600

# Database (optional)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=siem_db
DB_USER=siem_user
DB_PASSWORD=secure_password
```

## 🧪 Running Tests

### JavaScript Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- LogParser.test.js
```

### Python Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=scripts tests/

# Run specific test
pytest tests/test_anomaly_detection.py
```

## 📈 Performance Tuning

### For Large Log Files (>1GB)

1. **Increase Node.js memory**:
```bash
NODE_OPTIONS="--max-old-space-size=4096" npm start
```

2. **Use Python CLI for batch processing**:
```bash
python scripts/siem_analyzer.py --input large.log --threshold 50
```

3. **Split large files**:
```bash
split -l 100000 large.log sample-data/chunk_
```

## 🔄 Updating the Project

```bash
# Pull latest changes
git pull origin main

# Update dependencies
npm install
pip install -r requirements.txt

# Rebuild Docker image
docker-compose build
```

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Change port in package.json or use:
PORT=3001 npm start
```

#### Module Not Found

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Python Dependencies Failed

```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### Docker Build Fails

```bash
# Clear Docker cache
docker system prune -a
docker-compose build --no-cache
```

## 📚 Next Steps

1. **Customize Detection Rules**: Edit thresholds in `src/utils/anomalyDetector.js`
2. **Add GeoIP**: Integrate MaxMind GeoIP database
3. **Set Up Alerts**: Configure email/Slack notifications
4. **Database Integration**: Store results in PostgreSQL/MongoDB
5. **Real-time Streaming**: Implement WebSocket for live analysis

## 💡 Tips

- Start with smaller log files (10k-50k lines) for testing
- Adjust anomaly thresholds based on your traffic patterns
- Export anomalies to CSV for deeper analysis in Excel/Pandas
- Use the Python CLI for automated scheduled analysis
- Integrate with your existing SIEM/log aggregation tools

## 📞 Getting Help

- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/Arvind-55555/siem-analysis-platform/issues)
- 💬 [Discussions](https://github.com/Arvind-55555/siem-analysis-platform/discussions)

## ✅ Verification Checklist

- [ ] Node.js and npm installed
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Sample logs generated
- [ ] Web interface accessible
- [ ] Python CLI working
- [ ] Tests passing
- [ ] Docker container running (if using Docker)

---

**You're all set! 🎉**

Start analyzing your logs and detecting security threats!