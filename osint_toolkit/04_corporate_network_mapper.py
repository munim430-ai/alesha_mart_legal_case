#!/usr/bin/env python3
"""
Script 4: Corporate Alias & Network Mapping
Purpose:  Map Alesha Mart's executive network, shell entities, affiliated
          companies, and active corporate footprints using SpiderFoot,
          Maigret, and direct OSINT queries against public registries.

Targets:
    - Primary: @aleshamart.com executive email domain
    - Executive: Manjurul Alam Sikder, wife (Rokshana Akter / similar)
    - Payment affiliates: SSLCommerz merchant accounts
    - Corporate: RJSC-registered entities

Output:
    - SpiderFoot scan config (JSON)
    - Maigret CLI command profile
    - Direct OSINT correlation map

Usage:
    python3 04_corporate_network_mapper.py
    python3 04_corporate_network_mapper.py --spiderfoot
    python3 04_corporate_network_mapper.py --maigret
    python3 04_corporate_network_mapper.py --direct-osint
"""

import os, sys, json, time, subprocess, argparse, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Known identifiers ─────────────────────────────────────────────────────────
CASE = {
    "company":        "Alesha Mart Limited",
    "company_domain": "aleshamart.com",
    "executive_1":    "Manjurul Alam Sikder",
    "executive_2":    "Rokshana Akter",           # chairman's wife (verify name spelling)
    "company_email_domain": "@aleshamart.com",

    # Probable executive email patterns (enumerate for OSINT)
    "probable_emails": [
        "ceo@aleshamart.com",
        "md@aleshamart.com",
        "chairman@aleshamart.com",
        "manjurul@aleshamart.com",
        "m.sikder@aleshamart.com",
        "msikder@aleshamart.com",
        "admin@aleshamart.com",
        "accounts@aleshamart.com",
        "payment@aleshamart.com",
        "finance@aleshamart.com",
        "sikder.manjurul@gmail.com",    # common Bangladeshi personal Gmail pattern
        "manjurul.sikder@gmail.com",
        "alesha.mart@gmail.com",
        "aleshamart@gmail.com",
    ],

    # Known related corporate entities (expand via RJSC research)
    "affiliated_entities": [
        "Alesha Group",
        "Alesha Technology Limited",
        "Alesha Shopping",
        "AleshaShop Limited",
        "Alesha Telecom",
    ],

    # Transaction targets for cross-reference
    "merchant_ids": ["NG79612021060967264", "NG61552021060966458"],
    "order_ids":    ["2106091612430E7SEGDEEF1EW", "210609160513SWRWB2AQFCJEW"],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (LegalOSINT-AssetTracing/1.0)"}

# ────────────────────────────────────────────────────────────────────────────
# SECTION A — SPIDERFOOT CONFIGURATION
# SpiderFoot can be run as a web UI or CLI. This generates both.
# CLI: python3 tools/spiderfoot/sf.py -s TARGET -t TYPENAME -o json
# ────────────────────────────────────────────────────────────────────────────

SPIDERFOOT_MODULES_CORPORATE = [
    # Public records and registries
    "sfp_whois",           # WHOIS/RDAP data
    "sfp_dns",             # DNS A/MX/NS/TXT records
    "sfp_dnsdumpster",     # Passive DNS via DNSDumpster
    "sfp_sublist3r",       # Subdomain enumeration

    # Breach and leak databases (public indexes only)
    "sfp_haveibeenpwned",  # HaveIBeenPwned — checks email exposure
    "sfp_dehashed",        # Dehashed public breach index

    # Corporate and financial intelligence
    "sfp_opendns",
    "sfp_shodan",          # Shodan integration
    "sfp_censys",          # Censys.io certificate/IP data
    "sfp_sslcert",         # SSL certificate parsing
    "sfp_crt",             # crt.sh Certificate Transparency

    # Social and email intelligence
    "sfp_emailformat",     # Generate email permutations for domain
    "sfp_hunter",          # Hunter.io email verification (free tier)
    "sfp_linkedin",        # LinkedIn company profile
    "sfp_twitter",         # Twitter/X handles
    "sfp_facebook",        # Facebook presence

    # URL and web intelligence
    "sfp_webanalytics",    # Web tech fingerprinting
    "sfp_webserver",       # Server banner analysis
    "sfp_googlesearch",    # Google indexed pages
    "sfp_bing",            # Bing indexed pages

    # Passive threat intelligence
    "sfp_urlscan",         # URLScan.io
    "sfp_virustotal",      # VirusTotal domain/IP data
    "sfp_threatcrowd",     # ThreatCrowd
]

SPIDERFOOT_SCAN_CONFIGS = [
    {
        "scan_name":    "Aleshamart_Domain_Full",
        "target":       "aleshamart.com",
        "target_type":  "INTERNET_NAME",
        "scan_type":    "passive",
        "description":  "Full passive scan of aleshamart.com domain infrastructure",
        "modules":      SPIDERFOOT_MODULES_CORPORATE,
    },
    {
        "scan_name":    "Manjurul_Alam_Sikder",
        "target":       "Manjurul Alam Sikder",
        "target_type":  "HUMAN_NAME",
        "scan_type":    "passive",
        "description":  "Person OSINT — Alesha Mart chairman",
        "modules": [
            "sfp_whois", "sfp_googlesearch", "sfp_bing",
            "sfp_linkedin", "sfp_twitter", "sfp_facebook",
            "sfp_emailformat", "sfp_haveibeenpwned",
        ],
    },
    {
        "scan_name":    "Alesha_Payment_IPs",
        "target":       "aleshamart.com",
        "target_type":  "INTERNET_NAME",
        "scan_type":    "passive",
        "description":  "Map payment-related IP infrastructure",
        "modules": [
            "sfp_dns", "sfp_dnsdumpster", "sfp_shodan",
            "sfp_censys", "sfp_sslcert", "sfp_crt", "sfp_urlscan",
        ],
    },
]

# SpiderFoot CLI command generator
def generate_spiderfoot_commands(spiderfoot_path: str = "tools/spiderfoot/sf.py") -> list[str]:
    commands = []
    for cfg in SPIDERFOOT_SCAN_CONFIGS:
        mods = ",".join(cfg["modules"])
        cmd = (
            f"python3 {spiderfoot_path} "
            f'-s "{cfg["target"]}" '
            f'-t {cfg["target_type"]} '
            f'-m {mods} '
            f'-o json '
            f'> spiderfoot_{cfg["scan_name"]}.json'
        )
        commands.append({"scan": cfg["scan_name"], "command": cmd})
    return commands


# SpiderFoot REST API launcher (if SF is running as web server)
def spiderfoot_api_launch(host: str = "127.0.0.1", port: int = 5001):
    """
    Launch scans via SpiderFoot's REST API.
    First start SpiderFoot: python3 tools/spiderfoot/sf.py -l 127.0.0.1:5001
    Then run this function to submit scan jobs programmatically.
    """
    base = f"http://{host}:{port}"
    results = []

    for cfg in SPIDERFOOT_SCAN_CONFIGS:
        payload = {
            "scanname":   cfg["scan_name"],
            "scantarget": cfg["target"],
            "targettype": cfg["target_type"],
            "modulelist": ",".join(cfg["modules"]),
            "typelist":   "",
        }
        try:
            r = requests.post(f"{base}/startscan", data=payload, timeout=30)
            if r.status_code == 200:
                scan_id = r.text.strip()
                results.append({"scan": cfg["scan_name"], "id": scan_id, "status": "launched"})
                print(f"  [SpiderFoot] Launched: {cfg['scan_name']} → ID={scan_id}")
            else:
                print(f"  [SpiderFoot ERR] {cfg['scan_name']}: HTTP {r.status_code}")
        except requests.ConnectionError:
            print(f"  [SpiderFoot] Not reachable at {base}")
            print(f"  Start it: python3 tools/spiderfoot/sf.py -l {host}:{port}")
            break
        time.sleep(1)
    return results


def spiderfoot_poll_results(scan_id: str, host: str = "127.0.0.1", port: int = 5001):
    """Poll SpiderFoot scan results once complete."""
    base = f"http://{host}:{port}"
    while True:
        try:
            r = requests.get(f"{base}/scanstatus/{scan_id}", timeout=10)
            status = r.json()
            state = status.get("STATUS", "UNKNOWN")
            print(f"  Scan {scan_id}: {state}")
            if state in ("FINISHED", "ABORTED", "ERROR"):
                break
        except Exception as e:
            print(f"  [Poll ERR] {e}")
            break
        time.sleep(30)

    # Fetch results
    r = requests.get(f"{base}/scaneventresults/{scan_id}", timeout=30)
    return r.json() if r.status_code == 200 else {}


# ────────────────────────────────────────────────────────────────────────────
# SECTION B — MAIGRET CLI PROFILES
# Maigret searches usernames across 2000+ sites.
# Target: email local-parts and known username patterns for executives.
# ────────────────────────────────────────────────────────────────────────────

MAIGRET_TARGETS = [
    # Email local-parts as probable usernames
    "manjurulsikder",
    "manjurul.sikder",
    "m.alam.sikder",
    "aleshamart",
    "alesha_mart",
    "aleshaceo",
    "manjurul_alam",
    "sikder_manjurul",

    # Common Bangladeshi e-commerce CEO username patterns
    "aleshamartbd",
    "aleshabd",
    "manjurul1",
    "msikderbd",
]

# LinkedIn-specific OSINT (via Maigret)
MAIGRET_SITES_FOCUS = [
    "LinkedIn",
    "Twitter",
    "Facebook",
    "Instagram",
    "TikTok",
    "GitHub",
    "GitLab",
    "Telegram",
    "Pinterest",
    "YouTube",
    "Medium",
    "Reddit",
    "Quora",
    "Behance",    # common for BD designers
    "BizSugar",
]

def generate_maigret_commands(maigret_path: str = "tools/maigret") -> list[str]:
    commands = []
    for username in MAIGRET_TARGETS:
        # Full scan with HTML report
        cmd_full = (
            f"python3 {maigret_path}/maigret {username} "
            f"--html --pdf --csv "
            f"-a "                                     # all sites
            f"-T 30 "                                  # timeout 30s per site
            f"--retries 2 "
            f"-J {username}_maigret_report.json"
        )
        # Focused scan on high-value sites
        sites_arg = " ".join(f"--site {s}" for s in MAIGRET_SITES_FOCUS)
        cmd_focused = (
            f"python3 {maigret_path}/maigret {username} "
            f"{sites_arg} "
            f"--html --csv "
            f"-J {username}_maigret_focused.json"
        )
        commands.append({
            "username": username,
            "full_command":    cmd_full,
            "focused_command": cmd_focused,
        })
    return commands


def run_maigret_programmatic(maigret_path: str = "tools/maigret") -> list[dict]:
    """Run Maigret via subprocess for each target username."""
    results = []
    for username in MAIGRET_TARGETS:
        out_file = f"maigret_{username}.json"
        cmd = [
            sys.executable,
            f"{maigret_path}/maigret",
            username,
            "-a",
            "-T", "30",
            "--retries", "2",
            "-J", out_file,
        ]
        print(f"  [Maigret] Scanning username: {username}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.getcwd(),
            )
            entry = {
                "username":   username,
                "returncode": result.returncode,
                "output":     result.stdout[-2000:] if result.stdout else "",
                "report":     out_file if os.path.exists(out_file) else None,
            }
            if os.path.exists(out_file):
                with open(out_file) as f:
                    maigret_data = json.load(f)
                # Extract found accounts
                found = {site: data for site, data in maigret_data.items()
                         if isinstance(data, dict) and data.get("status") == "Claimed"}
                entry["accounts_found"] = list(found.keys())
                if found:
                    print(f"    [!!!] Accounts found: {list(found.keys())}")
            results.append(entry)
        except subprocess.TimeoutExpired:
            print(f"    [Timeout] {username}")
            results.append({"username": username, "error": "timeout"})
        except Exception as e:
            print(f"    [ERR] {username}: {e}")
            results.append({"username": username, "error": str(e)})
        time.sleep(3)
    return results


# ────────────────────────────────────────────────────────────────────────────
# SECTION C — DIRECT OSINT: Public Registry & Email Verification
# ────────────────────────────────────────────────────────────────────────────

def verify_email_existence(email: str) -> dict:
    """
    Check if an email address has a valid MX record and exists in public
    breach indexes — no SMTP probing (avoids ToS issues).
    Uses: Hunter.io verify API (free tier: 25 req/month)
          and HaveIBeenPwned API.
    """
    result = {"email": email, "checks": {}}

    # 1. DNS MX verification (does domain accept mail?)
    domain = email.split("@")[-1]
    try:
        import socket
        mx_records = []
        # Use a basic DNS lookup
        r = requests.get(
            f"https://dns.google/resolve?name={domain}&type=MX",
            headers=HEADERS, timeout=10
        )
        data = r.json()
        mx_records = [a.get("data") for a in data.get("Answer", [])]
        result["checks"]["mx_records"] = mx_records
        result["checks"]["domain_accepts_mail"] = bool(mx_records)
    except Exception as e:
        result["checks"]["mx_error"] = str(e)

    # 2. HaveIBeenPwned (breached email — public breach index)
    try:
        hibp_url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        hibp_headers = {**HEADERS, "hibp-api-key": os.getenv("HIBP_API_KEY", "")}
        r = requests.get(hibp_url, headers=hibp_headers, timeout=10)
        if r.status_code == 200:
            breaches = r.json()
            result["checks"]["hibp_breaches"] = [b.get("Name") for b in breaches]
            result["checks"]["hibp_breached"] = True
        elif r.status_code == 404:
            result["checks"]["hibp_breached"] = False
        else:
            result["checks"]["hibp_status"] = r.status_code
    except Exception as e:
        result["checks"]["hibp_error"] = str(e)

    # 3. Hunter.io email verification (free API)
    hunter_key = os.getenv("HUNTER_API_KEY", "")
    if hunter_key:
        try:
            r = requests.get(
                "https://api.hunter.io/v2/email-verifier",
                params={"email": email, "api_key": hunter_key},
                headers=HEADERS, timeout=15,
            )
            if r.status_code == 200:
                data = r.json().get("data", {})
                result["checks"]["hunter_status"]   = data.get("status")
                result["checks"]["hunter_score"]    = data.get("score")
                result["checks"]["hunter_smtp_ok"]  = data.get("smtp_server")
                result["checks"]["hunter_gibberish"] = data.get("gibberish")
        except Exception as e:
            result["checks"]["hunter_error"] = str(e)

    return result


def map_corporate_network() -> dict:
    """
    Direct OSINT map using public APIs:
    - OpenCorporates: company registry data
    - EDGAR / international registries: cross-check for offshore entities
    - LinkedIn company scraping (unauthenticated public profile)
    """
    network = {"nodes": [], "edges": []}

    # OpenCorporates Bangladesh company search
    oc_url = "https://api.opencorporates.com/v0.4/companies/search"
    for term in ["Alesha Mart", "Alesha Technology", "Alesha Group"]:
        try:
            r = requests.get(
                oc_url,
                params={"q": term, "jurisdiction_code": "bd", "per_page": 10},
                headers=HEADERS,
                timeout=15,
            )
            if r.status_code == 200:
                for company in r.json().get("results", {}).get("companies", []):
                    c = company.get("company", {})
                    node = {
                        "type":             "company",
                        "name":             c.get("name"),
                        "number":           c.get("company_number"),
                        "status":           c.get("current_status"),
                        "incorporation_dt": c.get("incorporation_date"),
                        "jurisdiction":     c.get("jurisdiction_code"),
                        "registered_address": c.get("registered_address_in_full"),
                        "oc_url":           c.get("opencorporates_url"),
                        "source":           "OpenCorporates",
                        "search_term":      term,
                    }
                    network["nodes"].append(node)
                    print(f"  [OpenCorporates] {node['name']} | "
                          f"{node['number']} | {node['status']}")
        except Exception as e:
            print(f"  [OpenCorporates ERR | {term}] {e}")
        time.sleep(1)

    # OpenCorporates officer search (find if executive appears in other companies)
    for officer in ["Manjurul Alam Sikder", "Manjurul Alam", "Rokshana Akter"]:
        try:
            r = requests.get(
                "https://api.opencorporates.com/v0.4/officers/search",
                params={"q": officer, "jurisdiction_code": "bd"},
                headers=HEADERS,
                timeout=15,
            )
            if r.status_code == 200:
                for off in r.json().get("results", {}).get("officers", []):
                    o = off.get("officer", {})
                    node = {
                        "type":       "officer",
                        "name":       o.get("name"),
                        "company":    o.get("company", {}).get("name"),
                        "company_num": o.get("company", {}).get("company_number"),
                        "position":   o.get("position"),
                        "start_date": o.get("start_date"),
                        "end_date":   o.get("end_date"),
                        "source":     "OpenCorporates",
                    }
                    network["nodes"].append(node)
                    print(f"  [OC Officer] {node['name']} → {node['company']} "
                          f"({node['position']}, {node['start_date']}–{node['end_date']})")
                    # Add edge: executive → company
                    network["edges"].append({
                        "from": node["name"],
                        "to":   node["company"],
                        "rel":  node["position"],
                    })
        except Exception as e:
            print(f"  [OC Officers ERR | {officer}] {e}")
        time.sleep(1)

    return network


# ────────────────────────────────────────────────────────────────────────────
# SECTION D — THEHAREVSTER OSINT for aleshamart.com
# theHarvester scrapes emails, IPs, and subdomains from public sources.
# ────────────────────────────────────────────────────────────────────────────

def run_theharvester(domain: str = "aleshamart.com") -> dict:
    """
    Run theHarvester against aleshamart.com using multiple data sources.
    theHarvester is already installed in tools/theHarvester.
    """
    out_xml = f"theharvester_{domain.replace('.','_')}.xml"
    cmd = [
        sys.executable, "-m", "theHarvester.theHarvester",
        "-d", domain,
        "-b", "bing,google,duckduckgo,baidu,yahoo,crtsh,dnsdumpster,rapiddns,urlscan,virustotal",
        "-l", "500",
        "-f", out_xml.replace(".xml", ""),
    ]
    result = {"domain": domain, "command": " ".join(cmd)}
    print(f"  [theHarvester] Scanning {domain}...")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=300,
        )
        result["stdout"] = proc.stdout[-3000:] if proc.stdout else ""
        result["returncode"] = proc.returncode

        # Parse output for key findings
        emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', proc.stdout)
        ips    = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', proc.stdout)
        subs   = re.findall(rf'[\w.-]+\.{re.escape(domain)}', proc.stdout)

        result["emails_found"]     = list(set(emails))
        result["ips_found"]        = list(set(ips))
        result["subdomains_found"] = list(set(subs))

        if result["emails_found"]:
            print(f"  [!!!] Emails: {result['emails_found']}")
        if result["subdomains_found"]:
            print(f"  [!!!] Subdomains: {result['subdomains_found']}")

    except subprocess.TimeoutExpired:
        result["error"] = "timeout"
        print("  [theHarvester] Timeout")
    except Exception as e:
        result["error"] = str(e)
        print(f"  [theHarvester ERR] {e}")
    return result


# ────────────────────────────────────────────────────────────────────────────
# SECTION E — SHERLOCK Username Hunt
# ────────────────────────────────────────────────────────────────────────────

def run_sherlock(usernames: list[str]) -> list[dict]:
    """
    Run Sherlock against all probable executive usernames.
    Sherlock is already installed: sherlock <username>
    """
    results = []
    for username in usernames[:5]:  # cap at 5 to avoid excessive noise
        out_file = f"sherlock_{username}.txt"
        cmd = ["sherlock", username, "--output", out_file, "--print-found"]
        print(f"  [Sherlock] Searching: {username}")
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120,
            )
            found_urls = re.findall(r'https?://\S+', proc.stdout)
            results.append({
                "username":   username,
                "found_urls": found_urls,
                "report":     out_file,
            })
            if found_urls:
                print(f"    [!!!] Found on {len(found_urls)} platforms:")
                for u in found_urls[:10]:
                    print(f"      {u}")
        except subprocess.TimeoutExpired:
            results.append({"username": username, "error": "timeout"})
        except FileNotFoundError:
            print("  [!] sherlock not in PATH — run: pip install sherlock-project")
            break
        time.sleep(2)
    return results


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────

def main(args):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    all_output = {"timestamp": ts}

    # A. SpiderFoot config export
    print(f"\n{'='*65}")
    print("  SPIDERFOOT SCAN CONFIGURATION")
    print(f"{'='*65}")

    sf_commands = generate_spiderfoot_commands()
    print("\n  CLI Commands:")
    for c in sf_commands:
        print(f"\n  [{c['scan']}]")
        print(f"  {c['command']}")
    all_output["spiderfoot_commands"] = sf_commands

    if args.spiderfoot:
        print("\n  Attempting SpiderFoot API launch...")
        sf_launched = spiderfoot_api_launch()
        all_output["spiderfoot_launched"] = sf_launched

    # B. Maigret commands and run
    print(f"\n{'='*65}")
    print("  MAIGRET USERNAME HUNT")
    print(f"{'='*65}")

    maigret_cmds = generate_maigret_commands()
    print("\n  CLI Commands (copy-paste to run):")
    for c in maigret_cmds:
        print(f"\n  # Username: {c['username']}")
        print(f"  {c['focused_command']}")
    all_output["maigret_commands"] = maigret_cmds

    if args.maigret:
        print("\n  Running Maigret scans...")
        maigret_results = run_maigret_programmatic()
        all_output["maigret_results"] = maigret_results

    # C. Direct OSINT
    if args.direct_osint:
        print(f"\n{'='*65}")
        print("  DIRECT OSINT — Email Verification & Corporate Network")
        print(f"{'='*65}")

        print("\n  Email verification:")
        email_results = []
        for email in CASE["probable_emails"][:5]:  # first 5 to conserve API
            print(f"  Checking: {email}")
            result = verify_email_existence(email)
            email_results.append(result)
            breached = result["checks"].get("hibp_breached")
            mx_ok    = result["checks"].get("domain_accepts_mail")
            print(f"    MX valid: {mx_ok}  |  Breached: {breached}  "
                  f"|  Breaches: {result['checks'].get('hibp_breaches', [])}")
            time.sleep(1.5)
        all_output["email_checks"] = email_results

        print("\n  Corporate network mapping (OpenCorporates):")
        network = map_corporate_network()
        all_output["corporate_network"] = network
        print(f"  Nodes found: {len(network['nodes'])}")
        print(f"  Edges found: {len(network['edges'])}")

        print("\n  theHarvester domain scan:")
        harvester_result = run_theharvester("aleshamart.com")
        all_output["theharvester"] = harvester_result

        print("\n  Sherlock username hunt:")
        sherlock_targets = [
            "manjurulsikder",
            "aleshamart",
            "alesha_mart",
            "manjurul.alam",
        ]
        sherlock_results = run_sherlock(sherlock_targets)
        all_output["sherlock"] = sherlock_results

    # D. Export complete config
    config_out = f"osint_config_and_commands_{ts}.json"
    with open(config_out, "w") as f:
        json.dump(all_output, f, indent=2, default=str)
    print(f"\n[✓] Full config + results exported → {config_out}")

    # Print a final correlation summary
    print(f"\n{'='*65}")
    print("  INVESTIGATION CORRELATION MATRIX")
    print(f"{'='*65}")
    print(f"""
  Case:         Alesha Mart — BDT 500,620.00
  Merchant IDs: {CASE['merchant_ids']}
  Domain:       {CASE['company_domain']}
  Executive:    {CASE['executive_1']}

  Tools deployed:
    1. SpiderFoot  → infrastructure map of aleshamart.com
    2. Maigret     → username presence across 2000+ platforms
    3. Sherlock    → executive social media accounts
    4. theHarvester → email + IP + subdomain harvest
    5. OpenCorporates → shell company / officer network

  Key evidentiary outputs:
    - DNS history + June 2021 payment server snapshots
    - SSL cert chain proving payment subdomains existed
    - Email addresses tied to @aleshamart.com domain
    - Corporate officer cross-links to affiliated entities
    - Social media accounts for freeze/monitoring

  Next step: Forward all findings to legal counsel
    for inclusion in writ petition exhibits.
    """)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corporate Network Mapper")
    parser.add_argument("--spiderfoot",   action="store_true", help="Launch SpiderFoot API scans")
    parser.add_argument("--maigret",      action="store_true", help="Run Maigret username scans")
    parser.add_argument("--direct-osint", action="store_true", help="Run email/corp OSINT")
    parser.add_argument("--all",          action="store_true", help="Run everything")
    args = parser.parse_args()
    if args.all:
        args.spiderfoot = args.maigret = args.direct_osint = True
    main(args)
