# DETAILED OSINT INVESTIGATION MANUAL
## Four Procurement Fraud Cases — Step-by-Step Procedures

**Created:** 2026-06-19  
**Classification:** Investigation Reference Material  
**Scope:** Public-records OSINT methodology for four Bangladesh procurement cases

---

## TABLE OF CONTENTS
1. [Case 1: Nagad/Exim Bank](#case-1-nagadexim-bank-loan)
2. [Case 2: Meghna Cloud/BDCCL](#case-2-meghna-cloudbdccl)
3. [Case 3: e-GP Syndicate](#case-3-egp-syndicate)
4. [Case 4: Zadid Automobiles/DGHS](#case-4-zadid-automobilesdghs)
5. [Cross-Cutting Analysis Tools](#cross-cutting-analysis-tools)
6. [Lead Documentation Template](#lead-documentation-template)

---

## CASE 1: NAGAD/EXIM BANK LOAN

### Known Facts (from public reporting)
- **Loan date:** February 2021
- **Amount:** Tk 500 crore
- **Lender:** Exim Bank of Bangladesh
- **Recipient entity:** Third Wave Technologies
- **Allegation:** Funds misused/diverted; deficit recovery case pending

### Investigation Sequence

#### Step 1.1: Corporate Registration (RJSC)
**Objective:** Extract complete official profile of Third Wave Technologies  
**Primary source:** Bangladesh Registrar of Joint Stock Companies (roc.gov.bd)

**Procedure:**
1. Go to roc.gov.bd → Company Search
2. Search: "Third Wave Technologies"
3. Extract:
   - Official company name (exact spelling)
   - Registration number
   - Date of incorporation
   - Registered address (street, division)
   - Object/scope of business (stated purpose)
   - Current status (active/dissolved/struck off)

**Critical documents to request:**
- Form I (Memorandum of Association) — lists objectives
- Form XII (Director declaration) — lists all directors, dates appointed/removed
- Annual returns (if publicly available) — shows shareholder structure

**Red flags to note:**
- Recently incorporated (< 6 months before Feb 2021 loan)
- Multiple address changes
- Director turnover around loan dates
- Object clause amended after loan received
- Registered address is residential or shared office

#### Step 1.2: Director Network Extraction
**Objective:** Map all directors and their other corporate roles  
**Procedure:**

1. Extract all directors from RJSC Form XII
2. For each director, search:
   - **OpenCorporates** (opencorporates.com): "director name" + Bangladesh → other boards
   - **ICIJ Offshore Leaks** (offshoreleaks.icij.org): search director name → offshore connections
   - **LinkedIn** (professional roles only, not personal): company pages mentioning the director

**Record template:**
```
Director Name: [Full name]
Date appointed (Third Wave): [Date]
Other directorships: [Entity 1, Entity 2...]
Other entities at same address: [Yes/No, which]
Offshore connections: [None/Confirmed via ICIJ]
Professional background: [LinkedIn title, company]
```

#### Step 1.3: Financial Flow Documentation
**Objective:** Trace the disbursement of the Tk 500 crore  
**Procedure:**

1. **Exim Bank official announcements:**
   - Search site:eximbankbd.com OR site:exim.gov.bd for "Third Wave" + "loan" + "500 crore"
   - Look for: Loan agreement date, disbursement schedule, conditions

2. **Ministry of Finance / Bangladesh Bank circulars:**
   - site:mof.gov.bd + "Third Wave" OR "loan"
   - site:bb.org.bd + "Nagad" + "digital payment" + "irregularities"

3. **Court/ACC documents (if published):**
   - Site:dhakahighcourt.gov.bd OR site:supremecourt.gov.bd + "Third Wave"
   - News archives (bdnews24.com, dhakatribune.com)

4. **Payment integration records:**
   - Nagad merchant registration details (obtained via legal process)
   - SSLCommerz integration documentation (if any)

#### Step 1.4: Red Flag Checklist
- ✓ Was Third Wave registered **after** Exim Bank loan announced?
- ✓ Are directors of Third Wave also directors of **other financial/tech entities**?
- ✓ Is the registered address a **private residence or virtual office**?
- ✓ Did **any directors appear in ICIJ Offshore Leaks**?
- ✓ What is the **actual stated business scope** in RJSC Form I?
- ✓ Are there **amendment records** changing scope after loan received?

#### Step 1.5: Specific Queries to Execute
```
Google Dorks:
"Third Wave Technologies" site:roc.gov.bd
"Third Wave Technologies" "Exim Bank" filetype:pdf
site:eximbankbd.com "Third Wave"
site:bb.org.bd "Nagad" "payment" "fraud" OR "irregularities"
"Third Wave Technologies" Bangladesh "loan" "2021"

OpenCorporates:
Search: "Third Wave Technologies" + filter: Bangladesh

ICIJ Leaks:
Search each director name individually
```

---

## CASE 2: MEGHNA CLOUD/BDCCL

### Known Facts
- **Arrangement:** GenNext Technologies provides cloud infrastructure to BDCCL
- **Alleged issue:** Asymmetric 76/24 revenue split (favors GenNext disproportionately)
- **Suspicion:** GenNext is a shell company front for another entity

### Investigation Sequence

#### Step 2.1: Corporate Profiles (Both Entities)
**Targets:** GenNext Technologies, BDCCL (Bangladesh Computer Council)

**GenNext Technologies:**
1. RJSC search (roc.gov.bd) for "GenNext" variants:
   - GenNext Technologies
   - GenNext Tech
   - GenNext Bangladesh
2. Extract: Registration date, address, directors, scope
3. **Address check:** Is it at same address as other tech companies?

**BDCCL:**
1. Not a private company — government body
2. Search site:bcc.gov.bd OR site:bdccl.gov.bd for:
   - Board composition
   - Procurement policy
   - Contract approvals

#### Step 2.2: Shell Company Detection
**Objective:** Determine if GenNext is controlled by another entity

**Procedures:**

**Procedure A: Address Pivoting**
- Extract GenNext's registered address
- Query RJSC for all entities at that address
- Compare directors across entities
- Pattern: Multiple shell companies share office = common operator

**Procedure B: Director Cross-Matching**
- Extract all GenNext directors
- OpenCorporates search: same directors on other boards
- Pattern: Director appears on 8+ boards simultaneously = red flag

**Procedure C: Domain & Infrastructure Pivoting**
- Primary targets: meghnacloud.com, gennext.com.bd (if exists)
- Extract WHOIS history using:
  - SecurityTrails (securitytrails.com) — free tier has historical DNS
  - WhoisXMLAPI (whoisxml.com) — historical registrant data
- Look for: Who registered the domain before current privacy masking?
  - Is registrant email shared with other domains?
  - Pattern: Same email registering multiple domain = network operator

#### Step 2.3: Contract Terms Analysis
**Objective:** Understand the 76/24 revenue split approval

**Procedure:**
1. Search BDCCL website for: "GenNext" + "contract" OR "revenue" OR "agreement"
2. Request via RTI (Right to Information): Contract signed between BDCCL and GenNext
3. Key questions from contract:
   - Who approved the asymmetric split?
   - What deliverables does GenNext provide?
   - Is pricing market-rate?
   - What happens to revenue?

**Red flags:**
- Contract lacks competitive bidding justification
- GenNext has no prior cloud infrastructure track record
- Deliverables are vague ("provide infrastructure")
- Revenue split favors GenNext with minimal stated obligations

#### Step 2.4: Specific Queries
```
Google Dorks:
"GenNext Technologies" site:roc.gov.bd
"Meghna Cloud" site:bcc.gov.bd OR site:bdccl.gov.bd
"GenNext" "BDCCL" "revenue split" OR "contract"
site:bcc.gov.bd "GenNext" filetype:pdf

WHOIS History:
meghnacloud.com historical WHOIS (SecurityTrails, WhoisXMLAPI)
Historical registrant email/organization

Infrastructure:
Reverse-IP: meghnacloud.com → IP address → other sites on same IP
DNS history: meghnacloud.com nameserver changes over time
```

---

## CASE 3: E-GP SYNDICATE

### Known Facts
- **Three entities:** OrangeBD, Tappware Solutions, SoftBD
- **Channel:** e-GP (e-Procurement portal) for government tenders
- **Suspicion:** Collusive bidding, mutual coordination

### Investigation Sequence

#### Step 3.1: Tender Pattern Analysis
**Objective:** Extract all e-GP tenders and identify bidding patterns

**Primary source:** e-GP portal (eprocure.gov.bd) + CPTU archives

**Procedure:**
1. Go to eprocure.gov.bd → Tender Search
2. Search tenders where **any of the three entities bid**
3. Export data with columns:
   - Tender ID
   - Tender date
   - Contract value
   - Bidder name
   - Bid amount
   - Bid date/time
   - Award decision

4. **Collusion pattern analysis:**

   **Pattern A: Bid Rotation**
   - Does OrangeBD win Tender 1 (lowest bid)?
   - Does Tappware win Tender 2 (lowest bid)?
   - Does SoftBD win Tender 3 (lowest bid)?
   - Repeat monthly?
   - → Indicates pre-arranged winner assignments

   **Pattern B: Complementary Bidding**
   - When all three bid on same tender:
     - Winning bid: 45 lakh
     - Runner-up bid: 47 lakh (consistent margin)
     - Third bid: 52 lakh
   - → Indicates knowledge of competitors' bids

   **Pattern C: Boilerplate Comparison**
   - Get technical proposals from all three bidders (request from CPTU)
   - Compare text: Are sections **identical** or use **rare phrases**?
   - → Indicates shared proposal source

**Red flag checklist:**
- ✓ Do the three always bid against same competitor group?
- ✓ Do they never compete when they need the contract most?
- ✓ Are bid margins **predictable**?
- ✓ Do they all submit bids **within seconds of each other**?

#### Step 3.2: Corporate Registration Cross-Check
**Objective:** Identify if entities share directors or infrastructure

**Procedure:**
1. RJSC registry for all three entities
2. Extract directors — any name appears on multiple boards?
3. Extract registered addresses — are they same or clustered?
4. Extract email addresses (from filings) — do they share patterns?

**Infrastructure pivoting:**
1. Find corporate websites (orangebd.com, etc.)
2. Use **BuiltWith** (builtwith.com):
   - Search each domain
   - Extract tech stack: CMS, analytics, hosting
   - Compare: Do they all use **same Google Analytics ID**?
     - → Indicates common admin/operator
   - Compare: Same hosting provider?

3. Use **ViewDNS reverse-IP**:
   - orangebd.com → IP → other sites on that IP
   - Pattern: Multiple company websites on same server = infrastructure sharing

#### Step 3.3: Specific Queries
```
Google Dorks:
site:eprocure.gov.bd "OrangeBD" OR "Tappware" OR "SoftBD"
site:cptu.gov.bd "OrangeBD" "tender" OR "award"
"OrangeBD" "Tappware" "SoftBD" Bangladesh
site:roc.gov.bd (OrangeBD OR Tappware OR SoftBD)

e-GP Tender Export:
eprocure.gov.bd → Advanced Search → Filter by bidder
Export: All tenders 2019-2024 with these three entities

Infrastructure:
Reverse-IP (ViewDNS): orangebd.com, tappware.com, softbd.com
BuiltWith: Compare analytics, hosting, CMS across three domains
DNS WHOIS: Registrant email/organization for each domain
```

---

## CASE 4: ZADID AUTOMOBILES/DGHS

### Known Facts
- **Entity:** Zadid Automobiles (historically automotive supplier)
- **Transaction:** Supplied masks to DGHS under World Bank health project
- **Issue:** Masks were defective/unusable; supplier mismatch (auto → medical)

### Investigation Sequence

#### Step 4.1: Corporate Scope Change Analysis
**Objective:** Did Zadid's business scope actually allow medical equipment?

**Procedure:**
1. RJSC registry (roc.gov.bd) — search "Zadid Automobiles"
2. Extract:
   - Registration date
   - Original object clause (stated business purpose)
   - **All amendments to object clause** with dates
   - Look for: When was "medical equipment" OR "masks" OR "PPE" added to scope?

**Red flag:**
- Original scope: "Automotive parts, vehicles, spare parts"
- Amendment dated **June 2020** adds: "Masks, medical equipment, PPE"
- → Suggests scope changed **to enable** the fraudulent contract

#### Step 4.2: Import/Export Trace
**Objective:** Trace actual supply chain of masks — origin country, declared value, shipper

**Primary sources:**
- **ImportGenius** (importgenius.com) — US-Bangladesh import data
- **Panjiva** (panjiva.com, owned by S&P) — global supply chain database
- **Zauba** (zauba.com) — India-Bangladesh trade data (if applicable)
- **VolzaGlobal** (volza.com) — import/export records

**Procedure:**
1. Search each database for "Zadid" OR "Zadid Automobiles"
2. Filter period: 2020-2022
3. Extract from each shipment record:
   - **HS code** (Harmonized Tariff code):
     - Automotive codes: 8704, 8708, etc.
     - Textile/mask codes: 6307, 6306 (woven fabrics)
     - Medical device codes: 9018 (surgical instruments)
   - **Shipper name** (who exported from origin country?)
   - **Origin country** (where did masks come from?)
   - **Declared import value** (cost per unit × quantity)
   - **Bill of Lading** data
   - **Destination** (confirmation it went to DGHS or intermediary)

**Analysis:**
- Compare declared import cost vs. invoiced sale price to DGHS
- HS code mismatch: Did masks import as "automotive parts"?
- Shipper profile: Is shipper a legitimate PPE manufacturer or trading house?

#### Step 4.3: DGHS Procurement Records
**Objective:** Verify contract terms, payment records, delivery inspection

**Procedure:**
1. Site:dghs.gov.bd search for "Zadid" + "masks" OR "PPE" OR "procurement"
2. Request via RTI: Purchase order, delivery inspection report, QC testing
3. Extract:
   - Contract date
   - Quantity, unit price
   - Total contract value
   - Delivery date
   - Inspection findings (pass/fail)
   - Payment records

**World Bank Audit:**
1. World Bank Integrity Vice Presidency (INT) sanctions list:
   - integrity.worldbank.org/debarment
   - Search "Zadid Automobiles"
   - Check: Has Zadid been debarred for this project?

#### Step 4.4: Specific Queries
```
Google Dorks:
"Zadid Automobiles" site:roc.gov.bd
site:dghs.gov.bd "Zadid" OR "masks" OR "PPE" 2020 OR 2021
"Zadid" "masks" "World Bank" filetype:pdf

Import/Export:
ImportGenius: "Zadid" shipper 2020-2022
Panjiva: "Zadid" importer Bangladesh
Zauba: "Zadid" India-Bangladesh trade

Analysis:
HS code trace: 6307 (masks) vs. 8704 (vehicles)
Shipper profile: Is shipper a PPE manufacturer?
```

---

## CROSS-CUTTING ANALYSIS TOOLS

### Tool 1: Address Pivoting (Shell Network Detection)
```
Procedure:
1. Extract entity registered address
2. RJSC search: All entities at that address
3. Extract directors from all entities at address
4. Compare: Do directors overlap?
Result: Co-located entities + overlapping directors = shell network

Example:
Entity A: Registered at "House 5, Road 10, Dhaka"
Entity B: Registered at "House 5, Road 10, Dhaka" (same)
Director overlap: 2 of 3 directors in common
→ Probable shell company structure
```

### Tool 2: Analytics ID Pivoting (Infrastructure Mapping)
```
Procedure:
1. Visit target websites: orangebd.com, tappware.com, etc.
2. View page source (Ctrl+U)
3. Search for: "UA-" (Google Analytics) OR "GTM-" (Google Tag Manager)
4. Extract ID (e.g., UA-123456-1)
5. Reverse lookup (BuiltWith, SpyOnWeb): Which other sites use this ID?
Result: Same Analytics ID across sites = common admin = network operator

Example:
- orangebd.com uses: UA-87654321-1
- tappware.com uses: UA-87654321-1
- softbd.com uses: UA-87654321-1
→ All three run by same administrator/network
```

### Tool 3: DNS/IP Reverse Lookup (Hosting Infrastructure)
```
Procedure:
1. Extract IP of domain: nslookup orangebd.com → 36.255.68.100
2. ViewDNS reverse-IP: What other domains resolve to 36.255.68.100?
3. Extract: Entity names, domain registration dates
Result: Multiple entities on same IP = shared infrastructure

Example:
36.255.68.100 hosts:
- orangebd.com (registered 2019)
- tappware.com (registered 2020)
- another-startup.com (registered 2021)
→ Likely hosted by same operator/ISP
```

---

## LEAD DOCUMENTATION TEMPLATE

### Standard Format for Each Finding:

```
═══════════════════════════════════════════════════════════════════

LEAD ID: [CASE]_[DATE]_[#]
Case: [Case 1/2/3/4]
Date Discovered: 2026-06-19

FINDING:
[Clear, factual statement of what was discovered]

ENTITY/PERSON:
[Name of company, director, or system affected]

SOURCE:
Primary: [URL with full path]
Secondary: [Alternative sources confirming]
Confidence: [High/Medium/Low]

STATUS:
[ ] Verified (independently confirmed)
[ ] Alleged (reported by reliable source, not independently confirmed)
[ ] Unconfirmed (pattern noted, awaiting confirmation)

DETAILS:
[Specific data extracted: registration dates, director names, amounts, etc.]

RED FLAGS:
□ Recently incorporated
□ Address matches other entities
□ Directors overlap with other entities
□ Incorporated shortly before alleged transaction
□ Scope of business amended post-transaction
□ No prior experience in stated sector
□ Unusual pricing/terms
□ Shared infrastructure (IP, Analytics ID, hosting)

NEXT STEPS:
1. [Specific follow-up investigation]
2. [Data to request via RTI/court order]
3. [Cross-reference with related lead]

NOTES:
[Additional context, limitations, or caveats]

═══════════════════════════════════════════════════════════════════
```

---

## EVIDENCE PRESERVATION CHECKLIST

**Critical data to secure immediately** (before deletion/alteration):

**Case 1 (Nagad/Exim Bank):**
- [ ] RJSC Form XII (directors) for Third Wave Technologies
- [ ] Exim Bank loan disbursement documentation
- [ ] Bangladesh Bank audit reports on Nagad
- [ ] Director profiles (LinkedIn, professional bios)

**Case 2 (Meghna Cloud):**
- [ ] RJSC registration for GenNext Technologies
- [ ] Meghnacloud.com WHOIS history (archive before domain expires)
- [ ] BDCCL contract with GenNext (court order if needed)
- [ ] Board meeting minutes approving the contract

**Case 3 (e-GP Syndicate):**
- [ ] e-GP tender history (all tenders with these three entities)
- [ ] CPTU award decisions and technical proposal files
- [ ] Corporate websites (BuiltWith, Google Analytics ID records)
- [ ] DNS history (SecurityTrails, Censys historical snapshots)

**Case 4 (Zadid Automobiles):**
- [ ] RJSC registration including object clause amendments
- [ ] Import shipment records (Bill of Lading, HS codes)
- [ ] DGHS delivery inspection reports
- [ ] World Bank project audit documentation

---

## FINAL NOTES

**Investigation Standards:**
- Never speculate beyond documented facts
- Always source claims with primary URLs
- Distinguish: verified vs. alleged vs. unconfirmed
- Build case on **multiple converging signals**, not single anomaly
- Preserve evidence by citing sources (don't assume websites persist)

**Legal Admissibility:**
- Publicly available documents are fair OSINT
- Screenshots with timestamps are admissible evidence
- Chain of custody matters: document how and when you accessed data
- Hearsay (allegation from news report) is noted but not conclusive

**Escalation Path:**
- For high-confidence findings: Refer to CID/ACC/appropriate enforcement agency
- Provide sourced lead matrix with preservation requests
- Recommend court orders for private data (bank records, server logs)
- Work through attorneys for formal evidence submission

