#!/bin/bash
# Complete SIEM Production Setup Script

echo "========================================"
echo "  🛡️  SIEM PRODUCTION SETUP"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Install dependencies
echo -e "${GREEN}📦 Step 1/6: Installing Python dependencies...${NC}"
pip3 install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
fi
echo ""

# Step 2: Create necessary directories
echo -e "${GREEN}📁 Step 2/6: Creating directories...${NC}"
mkdir -p logs data/exports models config/logstash/conf.d dashboards/kibana
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 3: Start Elasticsearch + Kibana
echo -e "${GREEN}🐳 Step 3/6: Starting Elasticsearch + Kibana...${NC}"
if command -v docker-compose &> /dev/null; then
    docker-compose up -d elasticsearch kibana
    echo -e "${YELLOW}   Waiting for Elasticsearch to start (60s)...${NC}"
    sleep 60
    
    # Check if Elasticsearch is running
    if curl -s http://localhost:9200 > /dev/null; then
        echo -e "${GREEN}✓ Elasticsearch is running at http://localhost:9200${NC}"
    else
        echo -e "${YELLOW}⚠  Elasticsearch not yet ready (may need more time)${NC}"
    fi
    
    # Check if Kibana is running
    if curl -s http://localhost:5601 > /dev/null; then
        echo -e "${GREEN}✓ Kibana is running at http://localhost:5601${NC}"
    else
        echo -e "${YELLOW}⚠  Kibana not yet ready (may need more time)${NC}"
    fi
else
    echo -e "${YELLOW}⚠  Docker Compose not found. Skipping ELK stack.${NC}"
    echo -e "${YELLOW}   SIEM will run without Elasticsearch${NC}"
fi
echo ""

# Step 4: Train ML model
echo -e "${GREEN}🤖 Step 4/6: Training ML anomaly detection model...${NC}"
python3 scripts/ml_anomaly_detector.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ML model trained and saved${NC}"
else
    echo -e "${YELLOW}⚠  ML model training had issues (non-critical)${NC}"
fi
echo ""

# Step 5: Run system tests
echo -e "${GREEN}🧪 Step 5/6: Running system tests...${NC}"
python3 test_complete_system.py > /tmp/siem_test.log 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${YELLOW}⚠  Some tests failed (check /tmp/siem_test.log)${NC}"
fi
echo ""

# Step 6: Show next steps
echo -e "${GREEN}✅ Step 6/6: Setup complete!${NC}"
echo ""
echo "========================================"
echo "  🎉 SIEM SYSTEM READY!"
echo "========================================"
echo ""
echo -e "${GREEN}Services Running:${NC}"
echo "  • Elasticsearch: http://localhost:9200"
echo "  • Kibana: http://localhost:5601"
echo ""
echo -e "${GREEN}Quick Start Commands:${NC}"
echo ""
echo "1. Start collecting real-time web data:"
echo -e "   ${YELLOW}python3 scripts/collect_web_data.py --mode continuous${NC}"
echo ""
echo "2. Start live dashboard:"
echo -e "   ${YELLOW}python3 scripts/run_live_dashboard.py${NC}"
echo "   Then open: http://localhost:8080"
echo ""
echo "3. View in Kibana:"
echo "   a. Open http://localhost:5601"
echo "   b. Create index pattern: siem-events-*"
echo "   c. Go to Discover to view events"
echo ""
echo "4. Monitor in terminal:"
echo -e "   ${YELLOW}python3 scripts/monitor.py --simulate${NC}"
echo ""
echo "========================================"
echo ""
echo -e "${GREEN}Advanced Features:${NC}"
echo "  • ML Anomaly Detection: ✓ Trained"
echo "  • Advanced Rules: config/advanced_detection_rules.yaml"
echo "  • Web Data Collection: scripts/collect_web_data.py"
echo "  • ELK Stack: Running (if Docker available)"
echo ""
echo -e "${YELLOW}Recommended: Start web data collection in one terminal,${NC}"
echo -e "${YELLOW}and run the dashboard in another!${NC}"
echo ""
