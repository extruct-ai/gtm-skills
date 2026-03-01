---
name: find-people
description: >
  Find contact people at target companies. Takes a company list (from
  list-building or segment-and-tier), generates relevant job titles, searches
  for matching contacts via Prospeo, and enriches them with verified emails
  and phones via Fullenrich or Prospeo. Outputs a contact CSV ready for
  email-generation. Triggers on: "find people", "find contacts", "get emails",
  "find decision makers", "who to email", "contact search", "people search",
  "get phone numbers", "enrich contacts".
---

# Find People

Find the right people at target companies. Turn a company list into a contact list with verified emails and phones.

## Where This Fits in the Pipeline

```
segment-and-tier → find-people → email-generation → copy-feedback → run-instantly
```

After you know WHICH companies to target (from `segment-and-tier` or `list-building`), this skill finds WHO to contact at each company.

## Auth

```python
from dotenv import load_dotenv
load_dotenv()
import os, requests, json, time

# Prospeo — search + enrich
PROSPEO_KEY = os.getenv("PROSPEO_API_KEY")
PROSPEO_BASE = "https://api.prospeo.io"
PROSPEO_HEADERS = {
    "X-KEY": PROSPEO_KEY,
    "Content-Type": "application/json"
}

# Fullenrich — waterfall enrichment (higher hit rate for emails/phones)
FULLENRICH_KEY = os.getenv("FULLENRICH_API_KEY")
FULLENRICH_BASE = "https://api.fullenrich.com/api/v1"
FULLENRICH_HEADERS = {
    "Authorization": f"Bearer {FULLENRICH_KEY}",
    "Content-Type": "application/json"
}
```

## Workflow

### Step 1: Load company list

Read the segmented list or company table:

```python
import pandas as pd
companies = pd.read_csv("claude-code-gtm/csv/input/{campaign}/segmented_list.csv")
# Needed columns: company_name, domain
```

Or fetch from Extruct table via API.

### Step 2: Generate title list

Based on the ICP from the context file and the campaign's target roles, generate a list of relevant job titles.

**Read context file** for ICP role targets:
```
claude-code-gtm/context/extruct_context.md → ## ICP → Roles column
```

**Title generation approach:**

Ask the user: "Who are we trying to reach at these companies?"

Then expand into a title list using seniority levels and department variations:

```
User says: "People who run marketing at mid-market SaaS companies"

Expanded title list:
- VP of Marketing
- Director of Marketing
- Head of Demand Generation
- Head of Growth
- CMO
- Director of Product Marketing
- Senior Marketing Manager
```

**Title list guidelines:**
- Start broad: 8-15 titles covering the ICP
- Include seniority variations (VP, Director, Head of, Senior)
- Include department variations (Business Development, Deal Sourcing, Acquisitions)
- Avoid titles that are too generic ("Manager") or too niche
- If unsure, use Prospeo Search Suggestions to validate titles exist in the database

### Step 3: Search for people via Prospeo

Use Prospeo Search Person to find matching contacts at the target companies.

**Option A: Search by company domains (recommended for targeted lists)**

```python
def search_people_at_companies(domains, titles, seniorities):
    """Search for people at specific companies."""
    all_results = []

    # Prospeo accepts up to 500 domains per request
    for i in range(0, len(domains), 500):
        batch = domains[i:i+500]
        resp = requests.post(f"{PROSPEO_BASE}/search-person", headers=PROSPEO_HEADERS, json={
            "filters": {
                "company_website": {
                    "v": batch,
                    "condition": "or"
                },
                "job_title": {
                    "v": titles,
                    "condition": "or"
                },
                "seniority": {
                    "v": seniorities,
                    "condition": "or"
                }
            },
            "page": 1
        })
        data = resp.json()
        all_results.extend(data.get("results", []))

        # Paginate if needed
        total_pages = data.get("pagination", {}).get("total_page", 1)
        for page in range(2, min(total_pages + 1, 20)):  # cap at 20 pages per batch
            resp = requests.post(f"{PROSPEO_BASE}/search-person", headers=PROSPEO_HEADERS, json={
                "filters": {
                    "company_website": {"v": batch, "condition": "or"},
                    "job_title": {"v": titles, "condition": "or"},
                    "seniority": {"v": seniorities, "condition": "or"}
                },
                "page": page
            })
            all_results.extend(resp.json().get("results", []))
            time.sleep(0.5)

    return all_results
```

**Option B: Broad search (for new market exploration)**

```python
resp = requests.post(f"{PROSPEO_BASE}/search-person", headers=PROSPEO_HEADERS, json={
    "filters": {
        "job_title": {"v": titles, "condition": "or"},
        "seniority": {"v": ["VP", "Director", "C-Suite"], "condition": "or"},
        "industry": {"v": ["your_industry_1", "your_industry_2"], "condition": "or"},
        "employee_range": {"v": ["51-200", "201-500"], "condition": "or"},
        "person_location": {"v": ["United States"], "condition": "or"}
    },
    "page": 1
})
```

**Seniority enum values:** C-Suite, VP, Director, Manager, Senior, Entry, Training, Intern

**Important:** Prospeo Search returns person + company data but **no email or phone**. You must enrich separately in Step 4.

### Step 4: Enrich contacts (get emails + phones)

Two providers available. Use the decision tree:

```
Need highest hit rate on emails? → Fullenrich (waterfall, tries multiple providers)
Need speed + have LinkedIn URLs? → Prospeo (fast, good with LinkedIn data)
Budget-conscious?                → Prospeo (1 credit/match vs Fullenrich variable)
Need mobile phones?              → Fullenrich (10 credits) or Prospeo (10 credits)
Want both?                       → Run Prospeo first, then Fullenrich for misses
```

**Option A: Prospeo Bulk Enrich (fast, up to 50 per request)**

```python
def enrich_via_prospeo(contacts, batch_size=50):
    """Enrich contacts via Prospeo. Max 50 per request."""
    all_matched = []
    all_not_matched = []

    for i in range(0, len(contacts), batch_size):
        batch = contacts[i:i+batch_size]
        data = []
        for c in batch:
            entry = {}
            if c.get("linkedin_url"):
                entry["linkedin_url"] = c["linkedin_url"]
            elif c.get("person_id"):
                entry["person_id"] = c["person_id"]
            else:
                entry["first_name"] = c["first_name"]
                entry["last_name"] = c["last_name"]
                entry["company_website"] = c["domain"]
            data.append(entry)

        resp = requests.post(f"{PROSPEO_BASE}/bulk-enrich-person", headers=PROSPEO_HEADERS, json={
            "data": data,
            "only_verified_email": True,
            "enrich_mobile": False
        })
        result = resp.json()
        all_matched.extend(result.get("matched", []))
        all_not_matched.extend(result.get("not_matched", []))
        time.sleep(1)

    return all_matched, all_not_matched
```

**Option B: Fullenrich Bulk Enrich (async waterfall, up to 100 per request)**

```python
def enrich_via_fullenrich(contacts, batch_size=100):
    """Enrich contacts via Fullenrich. Async — poll or use webhook."""
    enrichment_ids = []

    for i in range(0, len(contacts), batch_size):
        batch = contacts[i:i+batch_size]
        payload = []
        for c in batch:
            entry = {
                "first_name": c["first_name"],
                "last_name": c["last_name"],
                "domain": c["domain"]
            }
            if c.get("linkedin_url"):
                entry["linkedin_url"] = c["linkedin_url"]
            payload.append(entry)

        resp = requests.post(f"{FULLENRICH_BASE}/contact/enrich/bulk", headers=FULLENRICH_HEADERS, json={
            "contacts": payload
        })
        enrichment_ids.append(resp.json()["enrichment_id"])
        time.sleep(1)

    return enrichment_ids


def poll_fullenrich(enrichment_id, max_polls=60, interval=30):
    """Poll Fullenrich for results. Average 30-90s per contact."""
    for _ in range(max_polls):
        resp = requests.get(
            f"{FULLENRICH_BASE}/contact/enrich/bulk/{enrichment_id}",
            headers=FULLENRICH_HEADERS
        )
        data = resp.json()
        if data["status"] == "completed":
            return data["results"]
        time.sleep(interval)
    return None
```

**Option C: Waterfall — Prospeo first, Fullenrich for misses**

1. Run all contacts through Prospeo Bulk Enrich
2. Collect `not_matched` list
3. Run misses through Fullenrich
4. Merge results

### Step 5: Deduplicate and clean

```python
def clean_contacts(matched_contacts):
    """Deduplicate by email, filter out invalid emails."""
    seen_emails = set()
    clean = []
    for c in matched_contacts:
        email = c.get("person", {}).get("email") or c.get("work_email", {}).get("email")
        if not email or email in seen_emails:
            continue
        # Skip invalid emails (Fullenrich)
        verification = c.get("work_email", {}).get("verification_status", "")
        if verification == "INVALID":
            continue
        seen_emails.add(email)
        clean.append(c)
    return clean
```

### Step 6: Output contact CSV

Save the enriched contact list ready for `email-generation`:

```python
output_rows = []
for c in clean_contacts:
    person = c.get("person", {})
    company = c.get("company", {})
    output_rows.append({
        "first_name": person.get("first_name", ""),
        "last_name": person.get("last_name", ""),
        "email": person.get("email", ""),
        "job_title": person.get("title", ""),
        "company_name": company.get("name", ""),
        "domain": company.get("website", company.get("domain", "")),
        "linkedin_url": person.get("linkedin_url", ""),
        "phone": person.get("mobile", ""),
        "location": person.get("location", ""),
    })

df = pd.DataFrame(output_rows)
df.to_csv("claude-code-gtm/csv/input/{campaign}/contacts.csv", index=False)
```

Present summary:
- Total companies searched: N
- People found: N
- Emails verified: N
- Phones found: N
- No match: N

### Step 7: Review with user

Show a sample of 10 contacts for spot-checking:

| Name | Title | Company | Email | Phone |
|------|-------|---------|-------|-------|
| ... | ... | ... | ... | ... |

Ask:
- "Does the title mix look right?"
- "Any companies missing contacts? Want to broaden the title list?"
- "Ready to proceed to `email-generation`?"

## Title List Patterns

Common title expansion strategies:

**By seniority:** For each target department, include VP, Director, Head of, Senior, and Manager variations.

**By department alias:** Many functions have multiple names (e.g., "Revenue Operations" = "Sales Operations" = "Business Operations"). Include all common aliases.

**By company size:**
- At smaller companies (< 50), people hold broader titles ("Head of Growth" covers marketing + sales)
- At larger companies (500+), titles are more specialized ("Director of Demand Generation")

Pull the specific ICP roles from the context file and expand from there.

## API References

- [references/prospeo-api.md](references/prospeo-api.md) — Prospeo Search, Enrich, Bulk Enrich
- [references/fullenrich-api.md](references/fullenrich-api.md) — Fullenrich Bulk Enrich, Reverse Lookup
