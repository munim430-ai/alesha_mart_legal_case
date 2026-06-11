#!/usr/bin/env python3
"""
Script 3: Bangladesh Government & RJSC Portal Scraper
Purpose:  Automate scraping of public government endpoints to detect if
          SM Nabil's specific transaction references appear in published
          victim/refund lists, corporate filings, or court records.

Targets:
    - Ministry of Commerce / Digital Commerce Cell (ecc.gov.bd)
    - DNCRP public complaint/refund notices (dncrp.gov.bd)
    - RJSC company registry (rjsc.gov.bd)
    - Bangladesh Judiciary case search (judiciary.gov.bd)
    - Bangladesh Bank press releases / circulars (bb.org.bd)
    - Court of Settlement — CDCC refund lists

Approach:
    - Phase 1: requests + BeautifulSoup  (static pages)
    - Phase 2: Playwright                (JS-rendered pages, form submissions)
    - Phase 3: PDF extraction            (for official gazette / PDFs)

Install:
    pip install requests beautifulsoup4 playwright pdfplumber lxml
    playwright install chromium

Usage:
    python3 03_government_portal_scraper.py
    python3 03_government_portal_scraper.py --phase 2   # Playwright only
"""

import os, sys, re, json, time, argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

try:
    import pdfplumber
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False
    print("[!] pdfplumber not installed — PDF extraction disabled")
    print("    Run: pip install pdfplumber")

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_ENABLED = True
except ImportError:
    PLAYWRIGHT_ENABLED = False
    print("[!] Playwright not installed — dynamic scraping disabled")
    print("    Run: pip install playwright && playwright install chromium")

# ── Search terms ──────────────────────────────────────────────────────────────
SEARCH_TERMS = [
    # Exact transaction identifiers
    "NG79612021060967264",
    "NG61552021060966458",
    "2106091612430E7SEGDEEF1EW",
    "210609160513SWRWB2AQFCJEW",

    # Company & executives
    "Alesha Mart",
    "AleShaMart",
    "aleshamart",
    "Manjurul Alam Sikder",
    "Manjur Alam Sikder",
    "Manjurul Alam",

    # Account holder
    "SM Nabil",
    "S.M. Nabil",

    # Payment processors
    "SSLCommerz",
    "sslcommerz",
    "Nagad merchant",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ── Target endpoints ──────────────────────────────────────────────────────────

STATIC_TARGETS = [
    {
        "name": "Ministry of Commerce – Digital Commerce",
        "url":  "https://mincom.gov.bd/site/page/notice-board",
        "type": "notice_board",
    },
    {
        "name": "Ministry of Commerce – Press Releases",
        "url":  "https://mincom.gov.bd/site/press_release",
        "type": "press_release",
    },
    {
        "name": "Bangladesh Bank – Payment System Dept Circulars",
        "url":  "https://www.bb.org.bd/pub/regulationguideline/psd/index.php",
        "type": "circular_list",
    },
    {
        "name": "Bangladesh Bank – Press Releases",
        "url":  "https://www.bb.org.bd/pub/press/index.php",
        "type": "press_list",
    },
    {
        "name": "DNCRP – Public Notices",
        "url":  "https://dncrp.gov.bd/site/notices",
        "type": "notice_board",
    },
    {
        "name": "DNCRP – Complaint Status",
        "url":  "https://dncrp.gov.bd/site/complaint",
        "type": "form_page",
    },
    {
        "name": "ECC – E-commerce Circular List",
        "url":  "https://ecc.gov.bd/circulars",
        "type": "circular_list",
    },
    {
        "name": "ECC – Notice Board",
        "url":  "https://ecc.gov.bd/notices",
        "type": "notice_board",
    },
    {
        "name": "Bangladesh Judiciary – Case Search",
        "url":  "https://www.judiciary.gov.bd/case-info",
        "type": "case_search",
    },
]

# Known PDF URLs for official publications related to Alesha Mart
# These are real gazette/circular PDF patterns — adjust as new ones surface
KNOWN_PDF_URLS = [
    "https://www.bb.org.bd/pub/regulationguideline/psd/2021/06/psdcircular01_2021.pdf",
    "https://www.bb.org.bd/pub/regulationguideline/psd/2021/07/psdcircular_ecommerce.pdf",
    "https://mincom.gov.bd/sites/default/files/files/mincom.portal.gov.bd/page/alesha_mart_refund.pdf",
    "https://ecc.gov.bd/sites/default/files/victim_refund_list.pdf",
]


# ────────────────────────────────────────────────────────────────────────────
# PHASE 1: Static BeautifulSoup scraping
# ────────────────────────────────────────────────────────────────────────────

def scrape_static(target: dict, session: requests.Session) -> dict:
    result = {"name": target["name"], "url": target["url"], "hits": [], "links": []}
    try:
        r = session.get(target["url"], headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(separator=" ", strip=True)

        # Search for all terms
        for term in SEARCH_TERMS:
            if term.lower() in text.lower():
                result["hits"].append(term)
                # Extract surrounding context (100 chars each side)
                idx = text.lower().find(term.lower())
                ctx = text[max(0, idx-100):idx+len(term)+100]
                result.setdefault("contexts", {}).setdefault(term, []).append(ctx.strip())

        # Extract all links (for PDF and document discovery)
        for a in soup.find_all("a", href=True):
            href = urljoin(target["url"], a["href"])
            link_text = a.get_text(strip=True)
            # Flag interesting links
            if any(kw in link_text.lower() or kw in href.lower()
                   for kw in ["alesha", "refund", "digital commerce", "victim", "ecommerce fraud", "sslcommerz"]):
                result["links"].append({"text": link_text, "url": href})

        # Find tables — refund lists are usually in HTML tables
        tables = soup.find_all("table")
        for i, table in enumerate(tables):
            table_text = table.get_text(separator="|", strip=True)
            for term in SEARCH_TERMS:
                if term.lower() in table_text.lower():
                    result.setdefault("table_hits", []).append({
                        "table_index": i,
                        "term":        term,
                        "excerpt":     table_text[:500],
                    })

        status = f"[!!!] {len(result['hits'])} HITS" if result["hits"] else "[ok] No matches"
        print(f"    {status} — {target['name']}")
        if result["hits"]:
            print(f"      Matched terms: {result['hits']}")
        if result["links"]:
            print(f"      Interesting links ({len(result['links'])}):")
            for lnk in result["links"][:5]:
                print(f"        {lnk['text'][:60]:<60}  {lnk['url']}")

    except requests.exceptions.HTTPError as e:
        result["error"] = f"HTTP {e.response.status_code}"
        print(f"    [HTTP {e.response.status_code}] {target['name']}")
    except Exception as e:
        result["error"] = str(e)
        print(f"    [ERR] {target['name']}: {e}")
    return result


def scrape_rjsc(session: requests.Session) -> dict:
    """
    RJSC company search.
    The RJSC public search (rjsc.gov.bd) allows querying by company name.
    We search for Alesha Mart and related entities to get full filings.
    """
    result = {"name": "RJSC Company Search", "companies": []}
    search_names = [
        "Alesha Mart",
        "Alesha Technology",
        "Alesha Group",
        "Alesha Shopping",
        "AleshaShop",
    ]
    # RJSC public search endpoint (subject to change — verify URL before running)
    base = "https://www.rjsc.gov.bd/companySearch.do"
    for name in search_names:
        try:
            r = session.post(base, data={"companyName": name}, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "lxml")
            # Parse result table
            rows = soup.select("table tr")
            for row in rows[1:]:  # skip header
                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                if cols and any("alesha" in c.lower() for c in cols):
                    company_data = {
                        "search_term": name,
                        "columns":     cols,
                        "raw_row":     row.get_text(separator=" | ", strip=True),
                    }
                    result["companies"].append(company_data)
                    print(f"    [RJSC] Found: {' | '.join(cols[:5])}")
        except Exception as e:
            print(f"    [RJSC ERR | {name}] {e}")
        time.sleep(1)
    return result


# ────────────────────────────────────────────────────────────────────────────
# PHASE 2: Playwright dynamic scraping (JS-rendered pages + form interaction)
# ────────────────────────────────────────────────────────────────────────────

def playwright_scrape_dncrp() -> list[dict]:
    """
    DNCRP complaint status check via Playwright.
    The DNCRP portal may require JavaScript for the complaint search form.
    """
    if not PLAYWRIGHT_ENABLED:
        return []
    results = []
    complaint_queries = [
        "SM Nabil",
        "nabilshad50@gmail.com",
        "Alesha Mart",
        "NG79612021060967264",
    ]
    try:
        with sync_playwright() as pw:
            chromium_path = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
            browser = pw.chromium.launch(headless=True, executable_path=chromium_path)
            ctx = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                locale="en-US",
                ignore_https_errors=True,
            )
            page = ctx.new_page()

            for query in complaint_queries:
                try:
                    print(f"  [Playwright] DNCRP search: {query}")
                    page.goto("https://dncrp.gov.bd/site/complaint", timeout=30000)
                    page.wait_for_load_state("networkidle", timeout=15000)

                    # Try to find search input
                    search_inputs = page.query_selector_all('input[type="text"], input[type="search"]')
                    if search_inputs:
                        search_inputs[0].fill(query)
                        page.keyboard.press("Enter")
                        page.wait_for_load_state("networkidle", timeout=10000)
                        time.sleep(1)

                    content = page.content()
                    soup = BeautifulSoup(content, "lxml")
                    text = soup.get_text(separator=" ", strip=True)

                    hit = query.lower() in text.lower()
                    result = {
                        "source":     "DNCRP",
                        "query":      query,
                        "hit":        hit,
                        "screenshot": f"dncrp_{query[:20].replace(' ','_')}.png",
                    }

                    if hit:
                        print(f"    [!!!] HIT for '{query}'")
                        # Screenshot for evidentiary record
                        page.screenshot(path=result["screenshot"], full_page=True)
                        print(f"    Saved screenshot: {result['screenshot']}")

                    # Extract table data
                    for table in soup.find_all("table"):
                        for row in table.find_all("tr"):
                            row_text = row.get_text(separator=" | ", strip=True)
                            if any(t.lower() in row_text.lower() for t in SEARCH_TERMS):
                                result.setdefault("table_rows", []).append(row_text)
                    results.append(result)

                except Exception as e:
                    print(f"    [Playwright ERR | {query}] {e}")
                time.sleep(2)

            browser.close()
    except Exception as e:
        print(f"  [Playwright global ERR] {e}")
    return results


def playwright_scrape_ecc() -> list[dict]:
    """
    ECC (e-Commerce Cell / ecc.gov.bd) — scrape refund/victim lists.
    This is the key target: the ECC publishes periodic refund clearance lists
    which may name SM Nabil or reference SSLCommerz-Nagad transactions.
    """
    if not PLAYWRIGHT_ENABLED:
        return []
    results = []
    ecc_urls = [
        "https://ecc.gov.bd/",
        "https://ecc.gov.bd/notices",
        "https://ecc.gov.bd/victim-list",
        "https://ecc.gov.bd/refund-status",
        "https://ecc.gov.bd/alesha-mart",
        "https://mincom.gov.bd/site/page/cdcc",
    ]
    try:
        with sync_playwright() as pw:
            chromium_path = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
            browser = pw.chromium.launch(headless=True, executable_path=chromium_path)
            ctx = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                ignore_https_errors=True,
            )
            page = ctx.new_page()

            for url in ecc_urls:
                try:
                    print(f"  [Playwright] ECC: {url}")
                    page.goto(url, timeout=30000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    time.sleep(1)

                    content = page.content()
                    soup    = BeautifulSoup(content, "lxml")
                    text    = soup.get_text(separator=" ", strip=True)
                    hits    = [t for t in SEARCH_TERMS if t.lower() in text.lower()]

                    # Find all download links (PDFs, Excel sheets)
                    pdf_links = []
                    for a in soup.find_all("a", href=True):
                        href = urljoin(url, a["href"])
                        if href.lower().endswith((".pdf", ".xlsx", ".xls", ".csv")):
                            pdf_links.append({"text": a.get_text(strip=True), "url": href})

                    result = {
                        "url":       url,
                        "hits":      hits,
                        "pdf_links": pdf_links,
                    }

                    if hits:
                        print(f"    [!!!] HITS: {hits}")
                        page.screenshot(path=f"ecc_{urlparse(url).path.replace('/','_')}.png", full_page=True)

                    if pdf_links:
                        print(f"    [PDF links found] ({len(pdf_links)}):")
                        for pl in pdf_links[:5]:
                            print(f"      {pl['text'][:60]:<60}  {pl['url']}")

                    results.append(result)
                except Exception as e:
                    print(f"    [ERR {url}] {e}")
                time.sleep(2)

            browser.close()
    except Exception as e:
        print(f"  [Playwright ECC ERR] {e}")
    return results


# ────────────────────────────────────────────────────────────────────────────
# PHASE 3: PDF extraction
# ────────────────────────────────────────────────────────────────────────────

def extract_pdf(url: str, session: requests.Session) -> dict:
    """Download a PDF and extract all text — search for case-relevant terms."""
    if not PDF_ENABLED:
        return {"url": url, "error": "pdfplumber not installed"}
    result = {"url": url, "hits": {}, "pages_searched": 0}
    try:
        r = session.get(url, headers=HEADERS, timeout=30, stream=True)
        if r.status_code != 200:
            result["error"] = f"HTTP {r.status_code}"
            return result

        # Save temporarily
        tmp_path = "/tmp/alesha_govt_doc.pdf"
        with open(tmp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        with pdfplumber.open(tmp_path) as pdf:
            result["pages_searched"] = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                for term in SEARCH_TERMS:
                    if term.lower() in text.lower():
                        idx = text.lower().find(term.lower())
                        ctx = text[max(0, idx-150):idx+len(term)+150]
                        result["hits"].setdefault(term, []).append({
                            "page": page_num,
                            "context": ctx.strip(),
                        })

                # Try to extract tables from PDF
                tables = page.extract_tables()
                for tbl in tables:
                    for row in tbl:
                        row_str = " | ".join(str(cell or "") for cell in row)
                        if any(t.lower() in row_str.lower() for t in SEARCH_TERMS):
                            result.setdefault("table_hits", []).append({
                                "page": page_num,
                                "row":  row_str,
                            })

        if result["hits"]:
            print(f"  [!!!] PDF HIT: {url}")
            for term, occurrences in result["hits"].items():
                print(f"    Term '{term}' found on pages: {[o['page'] for o in occurrences]}")
                print(f"    Context: {occurrences[0]['context'][:200]}")
        else:
            print(f"  [clean] {url} ({result['pages_searched']} pages, no matches)")

    except Exception as e:
        result["error"] = str(e)
        print(f"  [PDF ERR] {url}: {e}")
    return result


# ────────────────────────────────────────────────────────────────────────────
# SECTION D: Bangladesh Bank MFS Oversight Report Parser
# BB publishes quarterly MFS reports — these contain aggregate transaction data
# that can be used to cross-reference the June 2021 transaction period
# ────────────────────────────────────────────────────────────────────────────

def scrape_bb_mfs_reports(session: requests.Session) -> list[dict]:
    """
    Bangladesh Bank quarterly MFS data reports — June 2021 issue.
    URL pattern: https://www.bb.org.bd/pub/halfyearly/fsr/index.php
    """
    results = []
    bb_report_urls = [
        "https://www.bb.org.bd/pub/quaterly/MFS/",
        "https://www.bb.org.bd/pub/regulationguideline/psd/",
        "https://www.bb.org.bd/fnansys/paymentsys/mfsdata.php",
    ]
    for url in bb_report_urls:
        try:
            r = session.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(r.text, "lxml")
            # Find all PDF links on BB pages
            for a in soup.find_all("a", href=True):
                href = urljoin(url, a["href"])
                link_text = a.get_text(strip=True)
                if any(kw in link_text.lower() or kw in href.lower()
                       for kw in ["mfs", "payment", "2021", "ecommerce", "e-commerce"]):
                    results.append({"text": link_text, "url": href, "source": url})
                    print(f"  [BB Report] {link_text[:60]:<60}  {href}")
        except Exception as e:
            print(f"  [BB ERR] {url}: {e}")
        time.sleep(1)
    return results


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────

def main(args):
    ts  = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    all_results = {"timestamp": ts, "static": [], "playwright": [], "pdfs": []}

    session = requests.Session()
    session.headers.update(HEADERS)

    # ── Phase 1: Static scraping ─────────────────────────────────────────────
    if args.phase in (0, 1):
        print(f"\n{'='*65}")
        print("  PHASE 1 — STATIC HTML SCRAPING")
        print(f"{'='*65}")
        for target in STATIC_TARGETS:
            print(f"\n  Scraping: {target['name']}")
            result = scrape_static(target, session)
            all_results["static"].append(result)
            time.sleep(1.5)

        print("\n  RJSC Company Registry Search:")
        rjsc_result = scrape_rjsc(session)
        all_results["rjsc"] = rjsc_result

        print("\n  Bangladesh Bank MFS Reports:")
        bb_reports = scrape_bb_mfs_reports(session)
        all_results["bb_reports"] = bb_reports

    # ── Phase 2: Playwright dynamic ─────────────────────────────────────────
    if args.phase in (0, 2):
        print(f"\n{'='*65}")
        print("  PHASE 2 — PLAYWRIGHT DYNAMIC SCRAPING")
        print(f"{'='*65}")
        print("\n  DNCRP Complaint Status Portal:")
        dncrp_results = playwright_scrape_dncrp()
        all_results["playwright"].extend(dncrp_results)

        print("\n  ECC / Ministry of Commerce Portal:")
        ecc_results = playwright_scrape_ecc()
        all_results["playwright"].extend(ecc_results)

    # ── Phase 3: PDF extraction ──────────────────────────────────────────────
    if args.phase in (0, 3):
        print(f"\n{'='*65}")
        print("  PHASE 3 — PDF DOCUMENT EXTRACTION")
        print(f"{'='*65}")

        # Collect all PDF links discovered in phases 1/2
        discovered_pdfs = []
        for r in all_results.get("static", []):
            for lnk in r.get("links", []):
                if lnk["url"].lower().endswith(".pdf"):
                    discovered_pdfs.append(lnk["url"])
        for r in all_results.get("playwright", []):
            for lnk in r.get("pdf_links", []):
                discovered_pdfs.append(lnk["url"])

        all_pdfs = KNOWN_PDF_URLS + list(set(discovered_pdfs))
        print(f"\n  PDF targets: {len(all_pdfs)}")
        for pdf_url in all_pdfs:
            print(f"\n  Extracting: {pdf_url}")
            pdf_result = extract_pdf(pdf_url, session)
            all_results["pdfs"].append(pdf_result)
            time.sleep(2)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*65}")
    print("  SUMMARY")
    print(f"{'='*65}")

    total_hits = 0
    for r in all_results["static"]:
        if r.get("hits"):
            print(f"  [HIT] {r['name']}: {r['hits']}")
            total_hits += len(r["hits"])
    for r in all_results["playwright"]:
        if r.get("hits") or r.get("hit"):
            print(f"  [HIT] {r.get('source', r.get('url'))}: {r.get('hits', r.get('query'))}")
            total_hits += 1
    for r in all_results["pdfs"]:
        if r.get("hits"):
            print(f"  [HIT PDF] {r['url']}: terms={list(r['hits'].keys())}")
            total_hits += len(r["hits"])

    print(f"\n  Total match events: {total_hits}")

    out_path = f"government_scrape_results_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"  [✓] Full results exported → {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bangladesh Government Portal Scraper")
    parser.add_argument(
        "--phase", type=int, default=0,
        help="0=all, 1=static_only, 2=playwright_only, 3=pdf_only"
    )
    main(parser.parse_args())
