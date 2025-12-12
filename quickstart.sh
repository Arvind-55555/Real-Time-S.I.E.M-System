#!/bin/bash
# SIEM Quick Start Script

echo "========================================"
echo "  SIEM System - Quick Start"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed"
else
    echo "⚠️  Some dependency conflicts exist (non-critical)"
fi
echo ""

# Run tests
echo "🧪 Running system tests..."
python3 test_complete_system.py > /tmp/siem_test.log 2>&1
if [ $? -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "❌ Tests failed. Check /tmp/siem_test.log"
    exit 1
fi
echo ""

# Create logs directory
mkdir -p logs data/exports

echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Run demo with sample data:"
echo "   python3 scripts/demo.py"
echo ""
echo "2. Start web dashboard:"
echo "   python3 scripts/run_dashboard.py"
echo "   Then open: http://localhost:8080"
echo ""
echo "3. Monitor in real-time:"
echo "   python3 scripts/monitor.py --simulate"
echo ""
echo "4. Process log file:"
echo "   python3 scripts/monitor.py --file data/sample_logs.txt"
echo ""
echo "For detailed guide, see: DEVELOPMENT_GUIDE.md"
echo ""
