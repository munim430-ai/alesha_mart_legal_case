#!/usr/bin/env bash
set -e

echo "=== OSINT Tools Installer ==="
echo "Initializing and updating git submodules..."
git submodule update --init --recursive

# Sherlock
echo ""
echo "[1/5] Installing Sherlock..."
cd tools/sherlock
pip install -r requirements.txt
cd ../..

# Maigret
echo ""
echo "[2/5] Installing Maigret..."
cd tools/maigret
pip install -r requirements.txt
cd ../..

# SpiderFoot
echo ""
echo "[3/5] Installing SpiderFoot..."
cd tools/spiderfoot
pip install -r requirements.txt
cd ../..

# Social Analyzer
echo ""
echo "[4/5] Installing Social Analyzer..."
cd tools/social-analyzer
pip install -r requirements.txt
cd ../..

# theHarvester
echo ""
echo "[5/5] Installing theHarvester..."
cd tools/theHarvester
pip install -r requirements.txt
cd ../..

echo ""
echo "=== All OSINT tools installed successfully ==="
echo ""
echo "Usage:"
echo "  Sherlock:        python tools/sherlock/sherlock <username>"
echo "  Maigret:         python tools/maigret/maigret <username>"
echo "  SpiderFoot:      python tools/spiderfoot/sf.py -l 127.0.0.1:5001"
echo "  Social Analyzer: python tools/social-analyzer/app.py"
echo "  theHarvester:    python tools/theHarvester/theHarvester.py -d <domain> -b all"
