#!/usr/bin/env python3
"""
Script 5: Multi-Case Procurement Investigation Framework
Purpose:  Systematically investigate five government procurement irregularities
          using corporate registry queries, procurement log analysis, and
          infrastructure pivoting

Cases:
1. Nagad / Third Wave Technologies / Exim Bank Loan
2. Meghna Cloud / BDCCL / GenNext Technologies
3. e-GP Syndicate (OrangeBD, Tappware Solutions, SoftBD)
4. Emergency Health Procurement (Zadid Automobiles / DGHS)
5. Ghost Employees / False e-TINs [audit trail only, no vulnerabilities]

Output: Sourced lead matrix with primary URLs, entity relationships,
        and recommended investigation angles
"""

import requests
import json
import time
import sys
from datetime import datetime
from collections import defaultdict

# ────────────────────────────────────────────────────────────────────────────
# CASE DEFINITIONS
# ────────────────────────────────────────────────────────────────────────────

CASES = {
    "CASE_1_NAGAD_EXIM": {
        "title": "Nagad / Third Wave Technologies / Exim Bank Loan (Feb 2021)",
        "entities": ["Third Wave Technologies", "Nagad", "Exim Bank"],
        "key_people": [],  # To be discovered
        "search_terms": {
            "corporate": [
                "Third Wave Technologies",
                "Third Wave Tech BD",
                "3W Technologies Bangladesh"
            ],
            "government": [
                "Exim Bank loan",
                "Nagad payment",
                "digital payment infrastructure"
            ],
            "keywords": ["Tk 500 crore", "deficit", "fund diversion"]
        },
        "registries": {
            "rjsc": "site:roc.gov.bd 'Third Wave'",
            "opencorp": "opencorporates.com 'Third Wave' Bangladesh",
            "icij": "offshoreleaks.icij.org search directors"
        },
        "sources": [
            ("RJSC Registry", "roc.gov.bd"),
            ("Bangladesh Bank", "bb.org.bd"),
            ("Ministry of Finance", "mof.gov.bd"),
            ("Nagad Press Releases", "nagad.com.bd"),
            ("News Archives", "bdnews24.com, dhakatribune.com")
        ]
    },

    "CASE_2_MEGHNACLOUD": {
        "title": "Meghna Cloud / BDCCL / GenNext Technologies",
        "entities": ["GenNext Technologies", "Meghna Cloud", "BDCCL"],
        "key_people": [],
        "search_terms": {
            "corporate": [
                "GenNext Technologies",
                "Meghna Cloud Limited",
                "BDCCL cloud infrastructure"
            ],
            "domain": [
                "meghnacloud.com",
                "gennextech.com",
                "gennext.com.bd"
            ],
            "keywords": ["76/24 revenue split", "cloud service", "contract asymmetry"]
        },
        "registries": {
            "rjsc": "site:roc.gov.bd 'GenNext'",
            "whois": "SecurityTrails/WhoisXMLAPI meghnacloud.com historical",
            "opencorp": "opencorporates.com GenNext Bangladesh"
        },
        "sources": [
            ("RJSC Registry", "roc.gov.bd"),
            ("BDCCL Tenders", "bcc.gov.bd or bdccl.gov.bd"),
            ("BTRC Reports", "btrc.gov.bd"),
            ("Domain WHOIS", "whoisxml.com, securitytrails.com"),
            ("DNS History", "ViewDNS, Censys")
        ]
    },

    "CASE_3_EGP_SYNDICATE": {
        "title": "e-GP Syndicate: OrangeBD, Tappware Solutions, SoftBD",
        "entities": ["OrangeBD", "Tappware Solutions", "SoftBD"],
        "key_people": [],
        "search_terms": {
            "corporate": [
                "OrangeBD Limited",
                "Tappware Solutions",
                "SoftBD Ltd"
            ],
            "procurement": [
                "e-GP tender",
                "government procurement",
                "CPTU award"
            ],
            "keywords": ["bid rotation", "collusive bidding", "complementary bids"]
        },
        "registries": {
            "egp": "site:eprocure.gov.bd OrangeBD OR Tappware OR SoftBD",
            "cptu": "site:cptu.gov.bd tender award",
            "rjsc": "site:roc.gov.bd (OrangeBD OR Tappware OR SoftBD)"
        },
        "sources": [
            ("e-GP Portal", "eprocure.gov.bd"),
            ("CPTU Archives", "cptu.gov.bd"),
            ("RJSC Registry", "roc.gov.bd"),
            ("Reverse-IP Analysis", "SecurityTrails, ViewDNS"),
            ("Shared Analytics", "BuiltWith, SpyOnWeb")
        ]
    },

    "CASE_4_EMERGENCY_HEALTH": {
        "title": "Emergency Health Procurement: Zadid Automobiles / DGHS",
        "entities": ["Zadid Automobiles", "DGHS", "World Bank Project"],
        "key_people": [],
        "search_terms": {
            "corporate": [
                "Zadid Automobiles",
                "Zadid Auto",
                "Zadid Ltd"
            ],
            "procurement": [
                "PPE procurement",
                "medical masks",
                "DGHS World Bank"
            ],
            "keywords": ["defective masks", "unusable equipment", "supply chain fraud"]
        },
        "registries": {
            "rjsc": "site:roc.gov.bd 'Zadid Automobiles'",
            "trade": "ImportGenius/Panjiva/Zauba Zadid 2020-2022",
            "wb_audit": "World Bank INT debarment list"
        },
        "sources": [
            ("RJSC Registry", "roc.gov.bd"),
            ("DGHS Procurement", "dghs.gov.bd"),
            ("ImportGenius", "importgenius.com"),
            ("Panjiva", "panjiva.com"),
            ("Zauba", "zauba.com"),
            ("World Bank INT", "integrity.worldbank.org")
        ]
    },

}

# ────────────────────────────────────────────────────────────────────────────
# PHASE 1: CORPORATE REGISTRY QUERIES
# ────────────────────────────────────────────────────────────────────────────

def generate_search_queries():
    """Generate all search queries for Phase 1 intake."""

    output = {
        "generated_at": datetime.now().isoformat(),
        "phase": "PHASE 1: Search Query Generation",
        "cases": {}
    }

    for case_id, case_data in CASES.items():
        output["cases"][case_id] = {
            "title": case_data["title"],
            "google_dorks": [],
            "registry_queries": [],
            "data_sources": []
        }

        # Generate Google Dorks
        dorks = []
        for entity in case_data["entities"]:
            dorks.append(f'"{entity}" site:roc.gov.bd')
            dorks.append(f'"{entity}" filetype:pdf government')
            dorks.append(f'"{entity}" "annual report" OR "audit"')

        for keyword in case_data["search_terms"].get("keywords", []):
            dorks.append(f'"{keyword}" government Bangladesh')

        output["cases"][case_id]["google_dorks"] = dorks

        # Registry queries
        output["cases"][case_id]["registry_queries"] = case_data["registries"]

        # Data sources
        output["cases"][case_id]["data_sources"] = case_data["sources"]

    return output

# ────────────────────────────────────────────────────────────────────────────
# PHASE 2: INFRASTRUCTURE PIVOTING FRAMEWORK
# ────────────────────────────────────────────────────────────────────────────

def generate_infrastructure_pivot_queries():
    """Generate infrastructure pivoting queries (domains, DNS, IP, analytics)."""

    output = {
        "phase": "PHASE 2: Infrastructure & Network Pivoting",
        "cases": {}
    }

    # Case 2 (Meghna Cloud) — domain pivoting
    output["cases"]["CASE_2_MEGHNACLOUD"] = {
        "domain_whois_history": {
            "tools": ["SecurityTrails", "WhoisXMLAPI", "DomainTools"],
            "targets": ["meghnacloud.com", "gennextech.com", "gennext.com.bd"],
            "goal": "Find historical registrant info before privacy masking"
        },
        "dns_reverse_ip": {
            "tools": ["SecurityTrails", "ViewDNS", "Censys", "Shodan"],
            "targets": ["meghnacloud.com", "gennext"],
            "goal": "Identify shared hosting blocks, co-hosted entities"
        },
        "shared_analytics": {
            "tools": ["BuiltWith", "SpyOnWeb", "DNSlytics"],
            "markers": ["Google Analytics UA-*", "Google Tag Manager GTM-*", "AdSense"],
            "goal": "Find other sites with same analytics ID = common operator"
        }
    }

    # Case 3 (e-GP Syndicate) — multi-entity infrastructure comparison
    output["cases"]["CASE_3_EGP_SYNDICATE"] = {
        "reverse_ip_all_three": {
            "entities": ["OrangeBD", "Tappware Solutions", "SoftBD"],
            "goal": "Compare IP blocks, nameservers, hosting providers for overlap"
        },
        "shared_infrastructure": {
            "tools": ["SecurityTrails", "ViewDNS", "BuiltWith"],
            "signals": [
                "Same IP block (25x.*.*.*, 36x.*.*.* patterns)",
                "Same nameservers",
                "Same host provider (InterCloud, BRACNet, etc.)",
                "Same Analytics ID (indicates common operator)"
            ]
        },
        "dns_history_timeline": {
            "goal": "Compare domain registration dates and DNS changes around tender dates"
        }
    }

    # Case 4 (Zadid Automobiles) — supply chain pivoting
    output["cases"]["CASE_4_EMERGENCY_HEALTH"] = {
        "import_export_tracing": {
            "tools": ["ImportGenius", "Panjiva", "Zauba", "VolzaGlobal"],
            "search_terms": ["Zadid Automobiles", "Zadid Auto", "Zadid Ltd"],
            "period": "2020-2022",
            "extraction": [
                "HS codes (commodity classification)",
                "Origin country of imports",
                "Declared import value",
                "Shipper/exporter names",
                "Bill of Lading data"
            ]
        },
        "hs_code_analysis": {
            "historical_codes": ["8704 (vehicles)", "8708 (vehicle parts)", "7326 (metal structures)"],
            "alleged_codes": ["3926 (plastic articles)", "6307 (textiles/masks)", "9018 (medical devices)"],
            "anomaly": "Why did automotive parts supplier suddenly import medical masks?"
        }
    }

    return output

# ────────────────────────────────────────────────────────────────────────────
# PHASE 3: DIRECTOR & OWNERSHIP MAPPING
# ────────────────────────────────────────────────────────────────────────────

def generate_director_mapping_queries():
    """Generate queries to map corporate officers, directors, and UBOs."""

    output = {
        "phase": "PHASE 3: Director & Ownership Mapping",
        "methodology": "Extract director names from RJSC, cross-reference against ICIJ leaks and professional profiles",
        "cases": {}
    }

    # Only include Cases 1-4
    for case_id in list(CASES.keys())[:4]:  # Skip Case 5
        output["cases"][case_id] = {
            "step_1_extract_directors": {
                "source": "RJSC Bangladesh (roc.gov.bd)",
                "action": "Query each entity, extract Form XII director names"
            },
            "step_2_cross_reference_icij": {
                "source": "ICIJ Offshore Leaks (offshoreleaks.icij.org)",
                "action": "Search each director name for offshore company connections"
            },
            "step_3_opencorporates_check": {
                "source": "OpenCorporates (opencorporates.com)",
                "action": "Search each director for directorships in other jurisdictions"
            },
            "step_4_address_pivoting": {
                "action": "Identify entities registered at the SAME address = potential shell network"
            },
            "step_5_linkedin_professional": {
                "action": "Professional profiles only (LinkedIn company pages, board bios, conference speakers)"
            }
        }

    return output

# ────────────────────────────────────────────────────────────────────────────
# PHASE 4: PROCUREMENT PATTERN ANALYSIS
# ────────────────────────────────────────────────────────────────────────────

def generate_procurement_analysis_framework():
    """Generate framework for analyzing procurement patterns (collusion detection)."""

    output = {
        "phase": "PHASE 4: Procurement Pattern Analysis",
        "case": "CASE_3_EGP_SYNDICATE",
        "methodology": "Export all tenders where ≥2 of {OrangeBD, Tappware, SoftBD} bid, analyze patterns",
        "signals": {
            "bid_rotation": {
                "definition": "Predictable winner rotation (Entity A wins in Month X, Entity B in Month Y)",
                "red_flag": "High: indicates pre-arranged winner assignments"
            },
            "complementary_bidding": {
                "definition": "Consistent bid margins (e.g., winner always 5% lower than runner-up)",
                "red_flag": "High: indicates knowledge of competitors' bids"
            },
            "identical_boilerplate": {
                "definition": "Technical proposals share identical text, formatting, or rare phrases",
                "red_flag": "Medium-High: indicates shared proposal source"
            },
            "bidder_exclusion": {
                "definition": "When all three bid, smaller competitors bid unusually high or withdraw",
                "red_flag": "Medium: indicates coordination to favor certain players"
            }
        },
        "data_extraction": {
            "source": "e-GP portal (eprocure.gov.bd)",
            "fields": [
                "Tender ID",
                "Tender date",
                "Contract value",
                "Bidder name",
                "Bid amount",
                "Bid date/time",
                "Award decision",
                "Technical proposal (text)"
            ]
        }
    }

    return output

# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────

def main():
    print("[*] Generating multi-case procurement investigation framework...")
    print(f"[*] Timestamp: {datetime.now().isoformat()}")
    print(f"[*] Cases: {len(CASES)}")
    print()

    # Phase 1: Search queries
    print("[PHASE 1] Generating search queries...")
    phase1 = generate_search_queries()

    with open("phase1_search_queries.json", "w") as f:
        json.dump(phase1, f, indent=2)
    print(f"  ✓ Saved to phase1_search_queries.json")

    # Phase 2: Infrastructure pivoting
    print("[PHASE 2] Generating infrastructure pivoting queries...")
    phase2 = generate_infrastructure_pivot_queries()

    with open("phase2_infrastructure_pivots.json", "w") as f:
        json.dump(phase2, f, indent=2)
    print(f"  ✓ Saved to phase2_infrastructure_pivots.json")

    # Phase 3: Director mapping
    print("[PHASE 3] Generating director mapping framework...")
    phase3 = generate_director_mapping_queries()

    with open("phase3_director_mapping.json", "w") as f:
        json.dump(phase3, f, indent=2)
    print(f"  ✓ Saved to phase3_director_mapping.json")

    # Phase 4: Procurement analysis
    print("[PHASE 4] Generating procurement analysis framework...")
    phase4 = generate_procurement_analysis_framework()

    with open("phase4_procurement_analysis.json", "w") as f:
        json.dump(phase4, f, indent=2)
    print(f"  ✓ Saved to phase4_procurement_analysis.json")

    print()
    print("[✓] Investigation framework generated. Four phase files created.")
    print("[→] NEXT: Execute Phase 1 searches using tools/spiderfoot, Google Dorks, and public APIs")

if __name__ == "__main__":
    main()
