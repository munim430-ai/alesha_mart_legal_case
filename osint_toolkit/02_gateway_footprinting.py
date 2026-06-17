#!/usr/bin/env python3
"""
Script 2: Merchant ID & Gateway Infrastructure Footprinting
Purpose:  Map SSLCommerz/Nagad transaction infrastructure and locate
          public evidentiary references to your specific Merchant Bank IDs
          in public code repositories, technical documentation, and
          publicly indexed data — for legal asset tracing.

Merchant Bank IDs (evidentiary targets — 6 confirmed paid orders):
    NG61552021060966458   (Order #210609160513SWRWB2AQFCJEW, BDT 250,310 — June 9)
    NG79612021060967264   (Order #210609161243OE7SEGDEEF1EW, BDT 250,310 — June 9)
    NG21462021061355311   (Order #210613133727KPI7LG6LPJ7EW, BDT 279,560 — June 13)
    NG64552021061356312   (Order #210613134502GZRKFCTPPMDEW, BDT 279,560 — June 13)
    NG54122021061358770   (Order #210613140347UIQBLQMEWJUEW, BDT 279,560 — June 13)
    NG93752021061361888   (Order #210613142805UNAJXEFPNSEW,  BDT 279,560 — June 13)

NOTE: All searches target PUBLICLY INDEXED data only.
      Any credentials found in public repos are treated as
      EVIDENTIARY ARTIFACTS for legal proceedings — not for system access.

Usage:
    pip install PyGithub requests
    export GITHUB_TOKEN="your_github_personal_access_token"
    python3 02_gateway_footprinting.py
"""

import os, sys, re, json, time, requests
from datetime import datetime, timezone
from github import Github          # pip install PyGithub

# ── Case-specific constants ───────────────────────────────────────────────────
MERCHANT_IDS  = [
    "NG61552021060966458", "NG79612021060967264",
    "NG21462021061355311", "NG64552021061356312",
    "NG54122021061358770", "NG93752021061361888",
]
ORDER_IDS     = [
    "210609160513SWRWB2AQFCJEW", "210609161243OE7SEGDEEF1EW",
    "210613133727KPI7LG6LPJ7EW", "210613134502GZRKFCTPPMDEW",
    "210613140347UIQBLQMEWJUEW", "210613142805UNAJXEFPNSEW",
]
COMPANY_TERMS = ["aleshamart", "alesha mart", "alesha-mart", "aleshashop",
                 "manjurul alam sikder", "manjur alam sikder"]
GATEWAY_TERMS = ["sslcommerz", "ssl_commerz", "ssl-commerz"]
NAGAD_TERMS   = ["nagad_merchant", "nagad_api", "nagad.com.bd"]

GITHUB_TOKEN  = os.getenv("GITHUB_TOKEN", "")    # https://github.com/settings/tokens
HEADERS       = {"User-Agent": "LegalAssetTracingOSINT/1.0"}


# ────────────────────────────────────────────────────────────────────────────
# SECTION A — GOOGLE DORK REFERENCE LIST
# Copy-paste each dork directly into Google Search.
# These are targeted queries against publicly indexed data.
# ────────────────────────────────────────────────────────────────────────────

GOOGLE_DORKS = {

    "1_merchant_id_direct": [
        # Direct evidence of your specific transaction IDs in public web
        '"NG79612021060967264"',
        '"NG61552021060966458"',
        '"2106091612430E7SEGDEEF1EW"',
        '"210609160513SWRWB2AQFCJEW"',
        '"NG79612021060967264" OR "NG61552021060966458"',
    ],

    "2_sslcommerz_aleshamart_technical": [
        # Technical integration docs, API configs, dev discussions
        'site:github.com "aleshamart" "sslcommerz"',
        'site:github.com "aleshamart" "nagad"',
        'site:stackoverflow.com "aleshamart" "sslcommerz"',
        '"aleshamart" "MERCHANT_ID" filetype:env',
        '"aleshamart" "store_id" sslcommerz',
        '"aleshamart.com" "nagad" payment',
        'site:pastebin.com "aleshamart" sslcommerz',
        'site:pastebin.com "aleshamart" nagad',
    ],

    "3_sslcommerz_merchant_id_pattern": [
        # SSLCommerz merchant naming convention: store_id format
        # Based on pattern: NG[4-5digit-prefix][YYYYMMDD][seq]
        '"NG7961" sslcommerz',
        '"NG6155" sslcommerz',
        '"NG7961" nagad merchant',
        '"NG6155" nagad merchant',
        'sslcommerz "nagad" "merchant_id" "aleshamart"',
        'sslcommerz "store_id" "alesha"',
    ],

    "4_leaked_env_evidentiary": [
        # Search for publicly committed config files that reference the merchant
        # EVIDENTIARY PURPOSE: Confirm the payment infrastructure existed
        'site:github.com "aleshamart" ".env" OR "config.php" OR "settings.py"',
        'site:github.com "alesha" "SSLCZ_SECRET" OR "STORE_ID"',
        'site:github.com "alesha" "nagad_merchant_id" OR "nagad_api_key"',
        '"aleshamart" inurl:raw.githubusercontent.com',
        'site:github.com path:.env "aleshamart"',
        'site:github.com path:config "aleshamart" "sslcommerz"',
    ],

    "5_court_records_government": [
        # Government portals, court records, official documents
        'site:ecc.gov.bd "aleshamart" OR "alesha mart"',
        'site:dncrp.gov.bd "aleshamart" OR "alesha mart"',
        'site:rjsc.gov.bd "aleshamart"',
        'site:judiciary.gov.bd "manjurul alam sikder" OR "aleshamart"',
        '"aleshamart" "refund" site:gov.bd',
        '"alesha mart" "court order" filetype:pdf',
        '"manjurul alam sikder" court sentence site:bd',
        '"NG79612021060967264" OR "NG61552021060966458" site:gov.bd',
    ],

    "6_financial_forensics": [
        # Bangladesh Bank and financial sector filings
        '"aleshamart" "sslcommerz" settlement 2021',
        '"alesha mart" "nagad" transaction freeze',
        '"aleshamart" "merchant account" Bangladesh Bank',
        '"alesha mart" "escrow" "Bangladesh Bank" 2021',
        '"aleshamart" "CID" "financial crime" Bangladesh',
        '"alesha mart" "CDCC" refund list filetype:pdf',
        '"aleshamart" victim list filetype:pdf',
    ],

    "7_corporate_shell_tracing": [
        # Executive and affiliated entity tracing
        '"manjurul alam sikder" director company Bangladesh',
        '"manjurul alam" "aleshamart" offshore OR "shell company"',
        '"alesha group" "alesha technology" Bangladesh company',
        '"alesha mart" "sister concern" OR "affiliate" company',
        'site:rjsc.gov.bd "alesha" company registration',
        '"manjurul alam sikder" "company" RJSC Bangladesh',
        '"aleshamart" "director" "beneficial owner"',
    ],

    "8_media_investigative": [
        # Investigative journalism with financial detail
        '"alesha mart" "fund" "gateway" filetype:pdf',
        '"aleshamart" "sslcommerz" "funds" "crore"',
        '"alesha mart" "payment trapped" OR "frozen funds"',
        '"alesha mart" "nagad" BDT crore fraud',
        '"aleshamart" CID "merchant account" seized',
    ],
}


# ────────────────────────────────────────────────────────────────────────────
# SECTION B — GITHUB API SEARCH
# Uses the GitHub Search API to find publicly indexed code, issues,
# commits, and repositories referencing the target identifiers.
# Requires a GitHub Personal Access Token (PAT) — free to create.
# ────────────────────────────────────────────────────────────────────────────

def github_search_code(g: Github, query: str, label: str, max_results: int = 30) -> list[dict]:
    """Search GitHub code index for the given query."""
    results = []
    try:
        code_results = g.search_code(query)
        count = 0
        for item in code_results:
            if count >= max_results:
                break
            results.append({
                "label":      label,
                "query":      query,
                "repo":       item.repository.full_name,
                "file":       item.path,
                "url":        item.html_url,
                "raw_url":    item.download_url,
                "repo_stars": item.repository.stargazers_count,
                "repo_lang":  item.repository.language,
                "last_push":  str(item.repository.pushed_at),
            })
            count += 1
        time.sleep(2)   # GitHub code search: 10 req/min on free tier
    except Exception as e:
        print(f"  [GitHub ERR | {label}] {e}")
    return results


def github_search_repositories(g: Github, query: str) -> list[dict]:
    """Search repository names and descriptions."""
    results = []
    try:
        repos = g.search_repositories(query)
        for repo in repos[:20]:
            results.append({
                "name":        repo.full_name,
                "description": repo.description,
                "url":         repo.html_url,
                "stars":       repo.stargazers_count,
                "language":    repo.language,
                "created":     str(repo.created_at),
                "pushed":      str(repo.pushed_at),
                "topics":      repo.get_topics(),
            })
        time.sleep(1)
    except Exception as e:
        print(f"  [GitHub Repo ERR] {e}")
    return results


def github_search_commits(g: Github, query: str) -> list[dict]:
    """Search commit messages — catches mentions in commit logs."""
    results = []
    try:
        commits = g.search_commits(query)
        for commit in commits[:20]:
            results.append({
                "sha":     commit.sha[:12],
                "message": commit.commit.message[:200],
                "author":  commit.commit.author.name,
                "date":    str(commit.commit.author.date),
                "repo":    commit.repository.full_name,
                "url":     commit.html_url,
            })
        time.sleep(1)
    except Exception as e:
        print(f"  [GitHub Commits ERR] {e}")
    return results


def github_pipeline(token: str) -> dict:
    if not token:
        print("  [!] No GITHUB_TOKEN — skipping GitHub API search")
        print("      Set env var: export GITHUB_TOKEN='ghp_...'")
        print("      Create free token at: https://github.com/settings/tokens")
        return {}

    g = Github(token)
    all_results = {"code": [], "repos": [], "commits": []}
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # ── Code searches ─────────────────────────────────────────────────────
    code_queries = [
        # Direct merchant ID references (highest evidentiary value)
        ("merchant_id_1",   '"NG79612021060967264"'),
        ("merchant_id_2",   '"NG61552021060966458"'),
        ("order_id_1",      '"2106091612430E7SEGDEEF1EW"'),
        ("order_id_2",      '"210609160513SWRWB2AQFCJEW"'),

        # SSLCommerz + Alesha integration code
        ("ssl_alesha",       'aleshamart sslcommerz'),
        ("ssl_alesha_env",   'aleshamart STORE_ID'),
        ("nagad_alesha",     'aleshamart nagad'),
        ("alesha_config",    'aleshamart merchant_id'),
        ("alesha_api_key",   'aleshamart api_key'),

        # Generic SSLCommerz+Nagad patterns (may reveal merchant ID format)
        ("ssl_nagad_mid",    'sslcommerz nagad "NG7" merchant'),
        ("ssl_nagad_secret", 'sslcommerz nagad store_password'),
    ]

    print("\n[GitHub] Code Search:")
    for label, query in code_queries:
        print(f"  Searching: {query}")
        hits = github_search_code(g, query, label)
        if hits:
            print(f"    [!!!] {len(hits)} results found:")
            for h in hits:
                print(f"      {h['repo']:<45} {h['file']}")
                print(f"        URL: {h['url']}")
        all_results["code"].extend(hits)

    # ── Repository searches ───────────────────────────────────────────────
    print("\n[GitHub] Repository Search:")
    repo_queries = [
        "aleshamart payment",
        "alesha mart sslcommerz",
        "aleshamart bangladesh ecommerce",
    ]
    for q in repo_queries:
        print(f"  Searching repos: {q}")
        hits = github_search_repositories(g, q)
        for h in hits:
            print(f"    {h['name']:<45} {h['description'] or '—'}")
        all_results["repos"].extend(hits)

    # ── Commit message searches ───────────────────────────────────────────
    print("\n[GitHub] Commit Message Search:")
    commit_queries = [
        "aleshamart sslcommerz",
        "aleshamart nagad payment",
        "NG79612021060967264",
    ]
    for q in commit_queries:
        print(f"  Searching commits: {q}")
        hits = github_search_commits(g, q)
        for h in hits:
            print(f"    [{h['date'][:10]}] {h['repo']} — {h['message'][:100]}")
        all_results["commits"].extend(hits)

    # Export
    out_path = f"github_results_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  [✓] GitHub results exported → {out_path}")
    return all_results


# ────────────────────────────────────────────────────────────────────────────
# SECTION C — GITLAB PUBLIC SEARCH (unauthenticated API)
# GitLab's public API allows searching without auth at lower rate limits.
# ────────────────────────────────────────────────────────────────────────────

def gitlab_search(query: str) -> list[dict]:
    """
    GitLab global code search — free, no auth needed (rate-limited).
    https://docs.gitlab.com/ee/api/search.html
    """
    url = "https://gitlab.com/api/v4/search"
    params = {"scope": "blobs", "search": query}
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        print(f"  [GitLab ERR] {e}")
        return []


# ────────────────────────────────────────────────────────────────────────────
# SECTION D — SSLCommerz Merchant ID Structural Analysis
# Decode the naming convention embedded in the Merchant Bank IDs
# ────────────────────────────────────────────────────────────────────────────

def analyze_merchant_ids(ids: list[str]) -> dict:
    """
    Reverse-engineer the SSLCommerz/Nagad Merchant Bank ID structure.

    Format observed:  NG [5-digit-prefix] [YYYYMMDD] [9-digit-seq]
    NG79612021060967264  →  NG | 7961 | 20210609 | 67264
    NG61552021060966458  →  NG | 6155 | 20210609 | 66458

    The 4-digit prefix (7961 / 6155) likely corresponds to the
    Alesha Mart merchant account number registered with Nagad.
    These are the same merchant — different prefix may indicate
    different Nagad sub-merchant / wallet split, or order sequence bracket.
    """
    results = {}
    pattern = re.compile(
        r'^(NG|BK|RK|UC|CB|MB)'  # MFS provider prefix
        r'(\d{4,6})'              # Merchant sub-ID / wallet ID
        r'(\d{4})(\d{2})(\d{2})' # YYYY MM DD
        r'(\d+)$'                 # Sequential transaction counter
    )
    for mid in ids:
        m = pattern.match(mid)
        if m:
            provider, merchant_sub, yr, mo, dy, seq = m.groups()
            results[mid] = {
                "raw":           mid,
                "mfs_prefix":    provider,
                "merchant_sub_id": merchant_sub,
                "transaction_date": f"{yr}-{mo}-{dy}",
                "sequence_number": seq,
                "mfs_provider":  {"NG": "Nagad", "BK": "bKash",
                                   "RK": "Rocket", "UC": "UCash",
                                   "CB": "CityBank Mobile"}.get(provider, "Unknown"),
                "interpretation": (
                    f"Merchant sub-wallet '{merchant_sub}' at Nagad, "
                    f"transaction on {yr}-{mo}-{dy}, sequence #{seq}"
                )
            }
        else:
            results[mid] = {"raw": mid, "parse_error": "Pattern did not match"}

    print("\n[Merchant ID Analysis]")
    for mid, info in results.items():
        print(f"\n  ID: {mid}")
        for k, v in info.items():
            print(f"    {k:<22}: {v}")

    # Hypothesis: Are the two merchant sub-IDs (7961, 6155) the same account?
    sub_ids = [v.get("merchant_sub_id") for v in results.values() if "merchant_sub_id" in v]
    if len(set(sub_ids)) > 1:
        print(f"\n  [NOTE] Two distinct merchant sub-IDs: {set(sub_ids)}")
        print("         Hypothesis: Alesha Mart held multiple Nagad merchant wallets")
        print("         Action: Request Nagad to map BOTH sub-IDs to the same merchant entity")
    return results


# ────────────────────────────────────────────────────────────────────────────
# SECTION E — Shodan/Censys Infrastructure Search
# Map servers that hosted SSLCommerz payment endpoints for aleshamart.com
# ────────────────────────────────────────────────────────────────────────────

def shodan_internet_db_check(ips: list[str]) -> dict:
    results = {}
    for ip in ips:
        url = f"https://internetdb.shodan.io/{ip}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            data = r.json()
            results[ip] = data
            print(f"  {ip:<18}  ports={data.get('ports',[])}  vulns={data.get('vulns',[])}  hostnames={data.get('hostnames',[])}")
        except Exception as e:
            results[ip] = {"error": str(e)}
        time.sleep(0.5)
    return results


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*65}")
    print("  GATEWAY INFRASTRUCTURE FOOTPRINTING")
    print(f"  Target Merchant IDs: {MERCHANT_IDS}")
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}Z")
    print(f"{'='*65}")

    # A. Print dork list
    print("\n" + "─"*65)
    print("  GOOGLE DORK REFERENCE LIST")
    print("  Copy each query into Google Search — no automation needed")
    print("─"*65)
    for category, dorks in GOOGLE_DORKS.items():
        print(f"\n  [{category}]")
        for d in dorks:
            print(f"    {d}")

    # B. Merchant ID structural analysis
    print("\n" + "─"*65)
    print("  MERCHANT ID STRUCTURAL ANALYSIS")
    print("─"*65)
    mid_analysis = analyze_merchant_ids(MERCHANT_IDS)

    # C. GitHub pipeline
    print("\n" + "─"*65)
    print("  GITHUB PUBLIC CODE SEARCH")
    print("─"*65)
    gh_results = github_pipeline(GITHUB_TOKEN)

    # D. GitLab search
    print("\n" + "─"*65)
    print("  GITLAB PUBLIC CODE SEARCH")
    print("─"*65)
    for query in [MERCHANT_IDS[0], MERCHANT_IDS[1], "aleshamart sslcommerz"]:
        print(f"  Searching GitLab: {query}")
        gl_hits = gitlab_search(query)
        if gl_hits:
            print(f"  [!!!] {len(gl_hits)} results:")
            for hit in gl_hits[:5]:
                print(f"    {hit.get('project_id')} | {hit.get('path')}")
        else:
            print("    No results")
        time.sleep(2)

    # E. Export dorks to text file for investigator reference
    dork_out = "google_dorks_complete.txt"
    with open(dork_out, "w") as f:
        f.write("# ALESHA MART FRAUD — GOOGLE DORK MASTER LIST\n")
        f.write(f"# Generated: {datetime.now(timezone.utc).isoformat()}Z\n\n")
        for cat, dorks in GOOGLE_DORKS.items():
            f.write(f"\n## {cat}\n")
            for d in dorks:
                f.write(f"{d}\n")
    print(f"\n[✓] Dork list exported → {dork_out}")

    summary_out = "gateway_analysis_summary.json"
    with open(summary_out, "w") as f:
        json.dump({
            "merchant_id_analysis": mid_analysis,
            "github_hit_count":     len(gh_results.get("code", [])),
        }, f, indent=2, default=str)
    print(f"[✓] Analysis summary exported → {summary_out}")


if __name__ == "__main__":
    main()
