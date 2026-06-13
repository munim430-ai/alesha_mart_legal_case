#!/usr/bin/env python3
"""
Script 1: Passive DNS & Historical WHOIS Recon Pipeline
Target:   aleshamart.com and associated payment infrastructure
Purpose:  Legal asset tracing — isolate payment staging endpoints
          active around June 2021 for BDT 500,620 fund recovery

Usage:
    python3 01_passive_dns_recon.py
    python3 01_passive_dns_recon.py aleshamart.com

APIs used (all have free tiers):
    - crt.sh             : no key required
    - HackerTarget       : no key required
    - URLScan.io         : no key required
    - RDAP/IANA          : no key required
    - SecurityTrails     : free key at https://securitytrails.com/corp/api
    - VirusTotal         : free key at https://www.virustotal.com/gui/join-us
"""

import requests, json, time, sys, os
from datetime import datetime, timezone
from collections import defaultdict

# ── Config ──────────────────────────────────────────────────────────────────
TARGET_DOMAIN         = "aleshamart.com"
SECURITYTRAILS_APIKEY = os.getenv("ST_API_KEY", "YOUR_SECURITYTRAILS_KEY")
VIRUSTOTAL_APIKEY     = os.getenv("VT_API_KEY", "YOUR_VIRUSTOTAL_KEY")
REQUEST_TIMEOUT       = 30
RATE_LIMIT_SLEEP      = 1.2      # seconds between API calls

# Related infrastructure to check in parallel pass
RELATED_TARGETS = [
    "aleshamart.com.bd",
    "aleshatech.com",
    "aleshashop.com",
    "aleshagroupbd.com",
    "alesha-mart.com",
    "aleshamartpayment.com",
    "ssl.aleshamart.com",          # historical payment subdomain hint
    "pay.aleshamart.com",
    "api.aleshamart.com",
    "merchant.aleshamart.com",
    "gateway.aleshamart.com",
    "checkout.aleshamart.com",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (LegalAssetTracing/Investigation; +legal-osint)"
}

# ── Sources ──────────────────────────────────────────────────────────────────

def crtsh_subdomains(domain: str) -> list[dict]:
    """
    Certificate Transparency via crt.sh.
    Returns every cert ever issued for the domain — critical for finding
    staging subdomains that existed in mid-2021 but are now offline.
    """
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        seen = set()
        results = []
        for cert in r.json():
            # Each cert may have multiple names (SANs) newline-separated
            for name in cert.get("name_value", "").split("\n"):
                name = name.strip().lower()
                if domain in name and "*" not in name and name not in seen:
                    seen.add(name)
                    results.append({
                        "name":        name,
                        "issuer":      cert.get("issuer_name", ""),
                        "not_before":  cert.get("not_before", ""),
                        "not_after":   cert.get("not_after", ""),
                        "cert_id":     cert.get("id"),
                    })
        # Sort by issue date ascending so we can see the 2021 certs
        results.sort(key=lambda x: x.get("not_before", ""))
        return results
    except Exception as e:
        print(f"  [crt.sh ERR] {e}")
        return []


def hackertarget_passive_dns(domain: str) -> list[dict]:
    """HackerTarget passive DNS — free, no auth."""
    url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        results = []
        for line in r.text.strip().splitlines():
            if "," in line and "error" not in line.lower():
                host, ip = line.split(",", 1)
                results.append({"hostname": host.strip(), "ip": ip.strip()})
        return results
    except Exception as e:
        print(f"  [HackerTarget ERR] {e}")
        return []


def urlscan_history(domain: str) -> list[dict]:
    """
    URLScan.io historical page scans.
    Surfaces actual rendered page data, server tech stack, and IP
    for each point in time the domain was scanned — invaluable for
    confirming which payment servers were running in June 2021.
    """
    url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=200"
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        results = []
        for hit in r.json().get("results", []):
            pg = hit.get("page", {})
            task = hit.get("task", {})
            results.append({
                "url":        pg.get("url"),
                "ip":         pg.get("ip"),
                "server":     pg.get("server"),
                "country":    pg.get("country"),
                "asn":        pg.get("asn"),
                "asnname":    pg.get("asnname"),
                "scan_time":  task.get("time"),
                "scan_id":    task.get("uuid"),
            })
        return results
    except Exception as e:
        print(f"  [URLScan ERR] {e}")
        return []


def rdap_whois(domain: str) -> dict:
    """RDAP WHOIS — IANA standard, no auth required."""
    url = f"https://rdap.org/domain/{domain}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code == 404:
            return {"status": "NOT_FOUND"}
        data = r.json()
        events = {e["eventAction"]: e["eventDate"]
                  for e in data.get("events", [])}
        return {
            "domain":      data.get("ldhName"),
            "status":      data.get("status", []),
            "registered":  events.get("registration"),
            "last_changed": events.get("last changed"),
            "expiration":  events.get("expiration"),
            "nameservers": [ns.get("ldhName") for ns in data.get("nameservers", [])],
        }
    except Exception as e:
        print(f"  [RDAP ERR] {e}")
        return {}


def securitytrails_dns_history(domain: str) -> dict:
    """
    SecurityTrails — full A-record history.
    Free tier: 50 queries/month.  Best used on the apex domain only.
    """
    if SECURITYTRAILS_APIKEY == "YOUR_SECURITYTRAILS_KEY":
        return {}
    url  = f"https://api.securitytrails.com/v1/history/{domain}/dns/a"
    hdrs = {"APIKEY": SECURITYTRAILS_APIKEY, **HEADERS}
    try:
        r = requests.get(url, headers=hdrs, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [SecurityTrails history ERR] {e}")
        return {}


def securitytrails_subdomains(domain: str) -> list[str]:
    if SECURITYTRAILS_APIKEY == "YOUR_SECURITYTRAILS_KEY":
        return []
    url  = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    hdrs = {"APIKEY": SECURITYTRAILS_APIKEY, **HEADERS}
    try:
        r = requests.get(url, headers=hdrs, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return [f"{s}.{domain}" for s in data.get("subdomains", [])]
    except Exception as e:
        print(f"  [SecurityTrails subdomains ERR] {e}")
        return []


def securitytrails_whois_history(domain: str) -> list[dict]:
    """Historical WHOIS changes — catches registrant changes and privacy shields."""
    if SECURITYTRAILS_APIKEY == "YOUR_SECURITYTRAILS_KEY":
        return []
    url  = f"https://api.securitytrails.com/v1/history/{domain}/whois"
    hdrs = {"APIKEY": SECURITYTRAILS_APIKEY, **HEADERS}
    try:
        r = requests.get(url, headers=hdrs, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json().get("result", {}).get("items", [])
    except Exception as e:
        print(f"  [SecurityTrails WHOIS history ERR] {e}")
        return []


def virustotal_domain_info(domain: str) -> dict:
    if VIRUSTOTAL_APIKEY == "YOUR_VIRUSTOTAL_KEY":
        return {}
    url  = f"https://www.virustotal.com/api/v3/domains/{domain}"
    hdrs = {"x-apikey": VIRUSTOTAL_APIKEY, **HEADERS}
    try:
        r = requests.get(url, headers=hdrs, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        attrs = r.json().get("data", {}).get("attributes", {})
        return {
            "registrar":          attrs.get("registrar"),
            "creation_date":      attrs.get("creation_date"),
            "last_update_date":   attrs.get("last_update_date"),
            "last_dns_records":   attrs.get("last_dns_records", []),
            "last_https_cert":    attrs.get("last_https_certificate", {})
                                       .get("subject", {})
                                       .get("CN"),
            "categories":         attrs.get("categories", {}),
            "tags":               attrs.get("tags", []),
        }
    except Exception as e:
        print(f"  [VirusTotal ERR] {e}")
        return {}


def shodan_host_lookup(ip: str) -> dict:
    """
    Shodan free API (no key needed for basic /shodan/host/{ip}).
    Use this on IPs discovered above to pull port/service banners.
    """
    url = f"https://api.shodan.io/shodan/host/{ip}?key=YOUR_SHODAN_KEY"
    # Without a key, use the no-auth summary endpoint:
    alt_url = f"https://internetdb.shodan.io/{ip}"
    try:
        r = requests.get(alt_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [Shodan InternetDB ERR {ip}] {e}")
        return {}


# ── Analysis helpers ─────────────────────────────────────────────────────────

def filter_june2021(records: list[dict], date_key: str = "scan_time") -> list[dict]:
    return [r for r in records if "2021-06" in str(r.get(date_key, ""))]


def extract_unique_ips(urlscans: list[dict]) -> set[str]:
    return {r["ip"] for r in urlscans if r.get("ip")}


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(domain: str = TARGET_DOMAIN):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    print(f"\n{'='*65}")
    print(f"  PASSIVE DNS RECON PIPELINE")
    print(f"  Target  : {domain}")
    print(f"  Started : {ts}Z")
    print(f"{'='*65}")

    output = {"target": domain, "timestamp": ts}

    # ── 1. Certificate Transparency ──────────────────────────────────────────
    print("\n[1/7] Certificate Transparency → crt.sh")
    certs = crtsh_subdomains(domain)
    output["certs"] = certs
    print(f"  Certificates found : {len(certs)}")
    june_certs = [c for c in certs if "2021-06" in str(c.get("not_before", ""))]
    if june_certs:
        print(f"  [!!!] JUNE 2021 CERTS ({len(june_certs)}):")
        for c in june_certs:
            print(f"    {c['not_before'][:10]}  {c['name']:<50}  {c['issuer'][:40]}")
    else:
        print("  June 2021 certs: none found in this batch")
    # Print all unique subdomains from certs
    subs = sorted({c["name"] for c in certs})
    print(f"\n  All subdomains from CT ({len(subs)}):")
    for s in subs:
        print(f"    {s}")
    time.sleep(RATE_LIMIT_SLEEP)

    # ── 2. Passive DNS ───────────────────────────────────────────────────────
    print("\n[2/7] Passive DNS → HackerTarget")
    pdns = hackertarget_passive_dns(domain)
    output["passive_dns"] = pdns
    for r in pdns:
        print(f"  {r['hostname']:<50}  {r['ip']}")
    time.sleep(RATE_LIMIT_SLEEP)

    # ── 3. RDAP WHOIS ────────────────────────────────────────────────────────
    print("\n[3/7] RDAP WHOIS")
    whois = rdap_whois(domain)
    output["whois"] = whois
    for k, v in whois.items():
        print(f"  {k:<20} {v}")
    time.sleep(RATE_LIMIT_SLEEP)

    # ── 4. URLScan History ───────────────────────────────────────────────────
    print("\n[4/7] Historical Scans → URLScan.io")
    scans = urlscan_history(domain)
    output["urlscans"] = scans
    june_scans = filter_june2021(scans)
    all_ips = extract_unique_ips(scans)
    print(f"  Total historical scans  : {len(scans)}")
    print(f"  June 2021 scans         : {len(june_scans)}")
    print(f"  Unique IPs observed     : {len(all_ips)}")
    if june_scans:
        print(f"\n  [!!!] JUNE 2021 SNAPSHOTS:")
        for s in june_scans:
            print(f"    {s['scan_time'][:16]}  IP={s['ip']:<16}  Server={s['server']}")
            print(f"      URL: {s['url']}")
            print(f"      ASN: {s['asnname']}  Country: {s['country']}")
    time.sleep(RATE_LIMIT_SLEEP)

    # ── 5. Shodan on discovered IPs ──────────────────────────────────────────
    print(f"\n[5/7] Shodan InternetDB → discovered IPs ({len(all_ips)})")
    shodan_results = {}
    for ip in list(all_ips)[:10]:  # cap at 10 to avoid rate limits
        result = shodan_host_lookup(ip)
        shodan_results[ip] = result
        ports = result.get("ports", [])
        vulns = result.get("vulns", [])
        tags  = result.get("tags", [])
        print(f"  {ip:<18}  ports={ports}  vulns={vulns}  tags={tags}")
        time.sleep(0.5)
    output["shodan"] = shodan_results

    # ── 6. SecurityTrails ────────────────────────────────────────────────────
    if SECURITYTRAILS_APIKEY != "YOUR_SECURITYTRAILS_KEY":
        print("\n[6/7] SecurityTrails — DNS History + Subdomains + WHOIS History")
        st_history = securitytrails_dns_history(domain)
        st_subs    = securitytrails_subdomains(domain)
        st_whois   = securitytrails_whois_history(domain)
        output["st_dns_history"] = st_history
        output["st_subdomains"]  = st_subs
        output["st_whois_history"] = st_whois
        records = st_history.get("records", [])
        print(f"  A-record history entries : {len(records)}")
        for rec in records:
            ips = [v.get("ip") for v in rec.get("values", [])]
            print(f"    {rec.get('first_seen','?')} → {rec.get('last_seen','?')}  IPs: {ips}")
        print(f"  Subdomains enumerated : {len(st_subs)}")
        for s in st_subs:
            print(f"    {s}")
        time.sleep(RATE_LIMIT_SLEEP)
    else:
        print("\n[6/7] SecurityTrails — SKIPPED (set ST_API_KEY env var)")

    # ── 7. VirusTotal ────────────────────────────────────────────────────────
    if VIRUSTOTAL_APIKEY != "YOUR_VIRUSTOTAL_KEY":
        print("\n[7/7] VirusTotal Domain Intelligence")
        vt = virustotal_domain_info(domain)
        output["virustotal"] = vt
        for k, v in vt.items():
            if v:
                print(f"  {k:<25} {str(v)[:120]}")
    else:
        print("\n[7/7] VirusTotal — SKIPPED (set VT_API_KEY env var)")

    # ── Related domain sweep ─────────────────────────────────────────────────
    print("\n[+] Related/typosquat domain check:")
    related_results = []
    for rel in RELATED_TARGETS:
        w = rdap_whois(rel)
        status = w.get("status", [])
        reg    = w.get("registered", "")
        ns     = w.get("nameservers", [])
        if w.get("domain"):
            flag = "[ACTIVE]" if "active" in str(status).lower() else "[REGISTERED]"
            print(f"  {flag:<12} {rel:<40} reg={reg}  ns={ns}")
            related_results.append({"domain": rel, **w})
        else:
            print(f"  [NOT FOUND]  {rel}")
        time.sleep(0.4)
    output["related_domains"] = related_results

    # ── Export ───────────────────────────────────────────────────────────────
    out_path = f"dns_recon_results_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n[✓] Full results exported → {out_path}")
    print(f"    Subdomains found : {len(subs)}")
    print(f"    Unique IPs       : {len(all_ips)}")
    print(f"    June 2021 hits   : {len(june_scans)} URL scans, {len(june_certs)} certs")
    return output


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else TARGET_DOMAIN
    run_pipeline(target)
