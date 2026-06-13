#!/usr/bin/env bash
set -e

echo "=== OSINT Tools Installer ==="
echo "Initializing and updating git submodules..."
git submodule update --init --recursive

# Upgrade setuptools first (required to build stem for Sherlock)
echo ""
echo "Upgrading setuptools..."
pip install --upgrade setuptools

# Sherlock (uses pyproject.toml)
echo ""
echo "[1/5] Installing Sherlock..."
pip install -e tools/sherlock --ignore-installed

# Maigret (uses pyproject.toml)
echo ""
echo "[2/5] Installing Maigret..."
pip install -e tools/maigret --ignore-installed
# Pin aiodns to a version compatible with pycares 5.x
pip install "aiodns==3.2.0"

# SpiderFoot (uses requirements.txt)
echo ""
echo "[3/5] Installing SpiderFoot..."
pip install -r tools/spiderfoot/requirements.txt --ignore-installed

# Social Analyzer (uses requirements.txt)
echo ""
echo "[4/5] Installing Social Analyzer..."
pip install -r tools/social-analyzer/requirements.txt --ignore-installed

# theHarvester (latest commit requires Python 3.12; use last 3.11-compatible version)
echo ""
echo "[5/5] Installing theHarvester..."
pip install -e tools/theHarvester --ignore-installed

echo ""
echo "=== All OSINT tools installed successfully ==="
echo ""
echo "Usage:"
echo "  Sherlock:        sherlock <username>"
echo "  Maigret:         maigret <username>"
echo "  SpiderFoot:      python tools/spiderfoot/sf.py -l 127.0.0.1:5001"
echo "  Social Analyzer: python tools/social-analyzer/app.py --username <username> --mode fast"
echo "  theHarvester:    theHarvester -d <domain> -b all"
