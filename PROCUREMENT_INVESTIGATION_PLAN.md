# FIVE PROCUREMENT INVESTIGATIONS — SYSTEMATIC OSINT PLAN
**Investigation Date:** 2026-06-19  
**Status:** Active investigation into documented financial irregularities  
**Scope:** Public-records research only (corporate registries, government tenders, trade manifests, professional networks)

---

## INVESTIGATION FRAMEWORK

### Case 1: Nagad / Third Wave Technologies / Exim Bank Loan (Feb 2021)
**Known facts from public reporting:**
- Tk 500 crore loan from Exim Bank (alleged deficit/misuse)
- Third Wave Technologies as recipient entity
- Nagad payment integration suspected for fund diversion
- Period: February 2021 onwards

**Investigation angles:**
1. **Corporate registration trail:** RJSC history of Third Wave Technologies, director changes, address changes
2. **Offshore beneficial owner mapping:** ICIJ Offshore Leaks, OpenCorporates for any linked executives with foreign entities
3. **Financial flow:** Bank documents, loan documentation, disbursement schedules (available through RTI/court orders)
4. **Payment infrastructure:** SSLCommerz/Nagad merchant accounts linked to Third Wave

**Search targets:**
- RJSC Form XII (directors) for Third Wave Technologies
- OpenCorporates "Third Wave" + Bangladesh
- ICIJ Offshore Leaks database for director names
- Bangladesh Bank circulars (site:bb.org.bd) mentioning Nagad fraud
- Ministry of Finance audit reports
- News archives (bdnews24, dhakatribune) for reporting on the case
- Loan disbursement PDFs via Wayback Machine

**Data sources to query:**
- roc.gov.bd (RJSC registry)
- offshoreleaks.icij.org (Panama Papers, Paradise Papers, etc.)
- aleph.occrp.org (relationship database)
- banking/central bank press releases

---

### Case 2: Meghna Cloud / BDCCL / GenNext Technologies
**Known facts:**
- Asymmetric 76/24 revenue split between Meghna Cloud and GenNext
- BDCCL as procurement authority
- Suspected shell company structure for GenNext Technologies
- Cloud infrastructure contract with potential inflated pricing

**Investigation angles:**
1. **Shell company detection:** GenNext corporate registration, address, directors matching against other entities at same location
2. **Domain/infrastructure pivoting:** Historical WHOIS for meghnacloud.com, DNS records, shared IP blocks
3. **Contract approval chain:** BDCCL board minutes, approval documentation
4. **Director cross-matching:** GenNext directors cross-referenced with BDCCL officials

**Search targets:**
- RJSC "GenNext Technologies" + address matching
- SecurityTrails/WhoisXMLAPI historical WHOIS for meghnacloud.com
- OpenCorporates "GenNext" Bangladesh
- BDCCL procurement portal (site:bcc.gov.bd or site:bdccl.gov.bd)
- BTRC cloud service audit reports

**Data sources to query:**
- roc.gov.bd (RJSC)
- SecurityTrails/DomainTools (WHOIS history)
- BDCCL public tenders and contracts
- Bangladesh Communications Regulatory Authority

---

### Case 3: e-GP Syndicate — OrangeBD, Tappware Solutions, SoftBD
**Known facts:**
- Three entities bidding on similar government procurement tenders
- Suspected collusive bidding (bid rotation, complementary bidding patterns)
- e-GP portal as procurement mechanism
- Possible shared corporate infrastructure

**Investigation angles:**
1. **Collusion detection:** Export all e-GP tenders where ≥2 of the three bid → analyze bid patterns, margins, proposal boilerplate
2. **Shared infrastructure:** WHOIS/DNS/IP overlap, shared hosting, reverse-IP lookup
3. **Shared analytics:** BuiltWith, SpyOnWeb for shared Google Analytics/Tag Manager IDs across domains
4. **Mutual directors:** Corporate registry cross-match of all three companies

**Search targets:**
- e-GP historical tenders (site:eprocure.gov.bd)
- CPTU tender archives
- "OrangeBD" OR "Tappware" OR "SoftBD" + government contract
- Reverse-IP for all three corporate domains
- Analytics ID pivoting via BuiltWith/SpyOnWeb
- RJSC registration for all three

**Data sources to query:**
- eprocure.gov.bd (e-GP portal)
- cptu.gov.bd (Central Procurement Technical Unit)
- SecurityTrails (DNS/reverse-IP)
- BuiltWith (shared infrastructure markers)
- roc.gov.bd (corporate directors)

---

### Case 4: Emergency Health Procurement — Zadid Automobiles / DGHS
**Known facts:**
- Zadid Automobiles (automotive supplier) supplied medical equipment (masks) under World Bank project
- Unusable/defective masks supplied to DGHS
- Category jump: automotive → medical equipment
- Timeline: 2020-2022 procurement period

**Investigation angles:**
1. **Scope change detection:** RJSC object clause before/after amendment dates
2. **Supply chain tracing:** ImportGenius/Panjiva/Zauba for Zadid imports 2020-2022
3. **HS code analysis:** Track supplier's historical HS codes (automotive) vs. claimed medical products
4. **Price comparison:** Declared import value vs. invoiced sale price (markup analysis)
5. **World Bank project audit:** INT (Integrity Vice Presidency) sanctions/debarment list

**Search targets:**
- RJSC "Zadid Automobiles" + object clause amendment
- ImportGenius "Zadid" 2020-2022
- Panjiva "Zadid" (shipper/supplier tracking)
- Zauba "Zadid" (India-Bangladesh trade data)
- DGHS procurement portal (site:dghs.gov.bd)
- World Bank INT debarment list
- World Bank project documents

**Data sources to query:**
- roc.gov.bd (corporate history)
- ImportGenius/Panjiva/Zauba (trade manifests)
- dghs.gov.bd (procurement records)
- World Bank sanctions database
- News archives for DGHS medical procurement failures

---

### Case 5: Ghost Employees & False e-TINs — *AUDIT TRAIL ONLY (NOT VULNERABILITIES)*
**Known facts:**
- Bulk generation of duplicate e-TIN profiles reported
- Ministry of Finance / NBR system
- Suspected control failures in NID/e-TIN infrastructure

**Investigation angles (legitimate oversight only):**
1. **Macro control-failure signals:** Year-over-year TIN registration growth anomalies vs. filing rates
2. **Audit trail:** C&AG audit reports, management letters identifying control gaps
3. **Oversight body reporting:** PAC proceedings on payroll/ghost employee audits
4. **Structural findings:** How auditors have documented the system's weaknesses

**Search targets:**
- C&AG Bangladesh audit reports (site:cag.org.bd)
- Ministry of Finance annual reports (TIN registration statistics)
- PAC proceedings (Parliament)
- NBR press releases on TIN registration irregularities
- News archives (investigative reporting on ghost employees)

**Data sources to query:**
- cag.org.bd (auditor general reports)
- mof.gov.bd (ministry finance)
- parliament.gov.bd (PAC records)
- nbr.gov.bd (national board of revenue)

---

## EXECUTION PLAN

**Phase 1: Search & Intake**
1. Run Google Dorks for each case to identify public documents
2. Query corporate registries (RJSC, OpenCorporates, ICIJ)
3. Extract entity names, directors, addresses, affiliated companies

**Phase 2: Infrastructure & Network Pivoting**
1. Domain WHOIS history and DNS records
2. Shared hosting/IP analysis
3. Analytics/tracking ID correlation
4. Executive social media profiles (LinkedIn, professional bios)

**Phase 3: Financial Flow Tracing**
1. Procurement tender patterns (collusion detection)
2. Trade manifest analysis (import costs vs. invoiced prices)
3. Corporate registration timeline alignment with contract awards

**Phase 4: Anomaly Detection**
1. Compare declared corporate scope vs. actual procurement activity
2. Flag director overlaps, shared addresses, co-located entities
3. Identify year-over-year statistical anomalies

**Phase 5: Report Generation**
1. Documented lead matrix (each finding tied to primary source URL)
2. Recommended next steps for law enforcement / court orders
3. Preservation requests for live data (server records, CRM databases, etc.)

---

## CRITICAL RULES

✓ **ALL findings will be sourced** — every claim includes the primary URL/document  
✓ **No unsupported accusations** — flag anomalies, let investigators follow  
✓ **No vulnerability research** — skip Target 5 system-probing, stick to audit trails  
✓ **No private-life dossiers** — professional roles and corporate conduct only  
✓ **Allegations clearly marked** — "reported," "alleged," "suspected" language throughout  

---

## NEXT STEPS

1. Begin Phase 1 searches (Google Dorks + corporate registry queries)
2. Extract entity names and director lists
3. Cross-reference against offshore leaks and relationship databases
4. Document all findings in sourced lead matrix
