#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  ALESHA MART OSINT TOOLKIT — Master Runner
#  Run all four pipeline scripts in logical sequence.
#  Each script outputs JSON to the current directory.
#
#  Setup:
#    pip install -r requirements.txt
#    playwright install chromium
#
#  Environment variables (optional but recommended):
#    export ST_API_KEY="..."         # SecurityTrails free key
#    export VT_API_KEY="..."         # VirusTotal free key
#    export GITHUB_TOKEN="ghp_..."   # GitHub personal access token
#    export HUNTER_API_KEY="..."     # Hunter.io free key
#    export HIBP_API_KEY="..."       # HaveIBeenPwned API key (paid)
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TS=$(date +%Y%m%d_%H%M%S)
LOG="run_all_${TS}.log"

echo "=================================================="
echo " ALESHA MART OSINT PIPELINE"
echo " Started: $(date -u)"
echo "=================================================="
echo ""

# ── 1. Passive DNS Recon ─────────────────────────────────────
echo "[1/4] Passive DNS & WHOIS Recon..."
python3 01_passive_dns_recon.py 2>&1 | tee -a "$LOG"
echo ""

# ── 2. Gateway Footprinting ──────────────────────────────────
echo "[2/4] Gateway Infrastructure Footprinting..."
python3 02_gateway_footprinting.py 2>&1 | tee -a "$LOG"
echo ""

# ── 3. Government Portal Scraping ────────────────────────────
echo "[3/4] Government Portal Scraping (Phase 1 + 3)..."
python3 03_government_portal_scraper.py --phase 1 2>&1 | tee -a "$LOG"
echo ""
echo "       Running PDF extraction..."
python3 03_government_portal_scraper.py --phase 3 2>&1 | tee -a "$LOG"
echo ""

# ── 4. Corporate Network Mapping ─────────────────────────────
echo "[4/4] Corporate Network Mapping..."
python3 04_corporate_network_mapper.py --direct-osint 2>&1 | tee -a "$LOG"
echo ""

# ── Playwright phase (requires chromium) ─────────────────────
echo "[+] Playwright dynamic scraping (requires chromium)..."
python3 03_government_portal_scraper.py --phase 2 2>&1 | tee -a "$LOG"
echo ""

echo "=================================================="
echo " ALL SCANS COMPLETE"
echo " Log: $LOG"
echo " Results: $(ls *.json 2>/dev/null | wc -l) JSON files generated"
echo "=================================================="

# Combine all JSON results
python3 - <<'EOF'
import json, glob, os
from datetime import datetime, timezone

combined = {
    "case": "Alesha Mart BDT 1618860 Recovery (6 orders)",
    "generated": datetime.now(timezone.utc).isoformat(),
    "merchant_ids": ["NG61552021060966458", "NG79612021060967264", "NG21462021061355311", "NG64552021061356312", "NG54122021061358770", "NG93752021061361888"],
    "results": {}
}
for f in sorted(glob.glob("*.json")):
    if f.startswith("combined"):
        continue
    try:
        with open(f) as fh:
            combined["results"][f] = json.load(fh)
    except Exception as e:
        combined["results"][f] = {"error": str(e)}

out = f"combined_osint_results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
with open(out, "w") as fh:
    json.dump(combined, fh, indent=2, default=str)
print(f"[✓] Combined results → {out}")
EOF
