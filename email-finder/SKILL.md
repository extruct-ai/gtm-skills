---
name: email-finder
description: >
  Get verified emails and phones for contacts found by linkedin-finder.
  Takes LinkedIn profiles from the Extruct people table and enriches them
  via Prospeo and/or Fullenrich. Supports single-provider and waterfall modes.
  Outputs a contact CSV ready for email-generation.
  Triggers on: "get emails", "find emails", "enrich contacts", "email finder",
  "get phone numbers", "enrich people", "contact enrichment", "verify emails",
  "email enrichment".
---

# Email Finder

Turn LinkedIn profiles into verified emails and phones. Takes the output of `linkedin-finder` and runs it through Prospeo, Fullenrich, or both.

## Where This Fits in the Pipeline

```
segment-and-tier → linkedin-finder → email-finder → email-generation → copy-feedback → run-instantly
```

After `linkedin-finder` finds WHO to contact (with LinkedIn URLs), this skill gets their verified contact info.

## Auth

```python
from dotenv import load_dotenv
load_dotenv()
import os, requests, json, time

# Extruct — read people table
API_TOKEN = os.getenv("EXTRUCT_API_TOKEN")
BASE_URL = "https://api.extruct.ai/v1"
EXTRUCT_HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

# Prospeo — fast enrich, good with LinkedIn URLs
PROSPEO_KEY = os.getenv("PROSPEO_API_KEY")
PROSPEO_BASE = "https://api.prospeo.io"
PROSPEO_HEADERS = {
    "X-KEY": PROSPEO_KEY,
    "Content-Type": "application/json"
}

# Fullenrich — waterfall enrichment (higher hit rate)
FULLENRICH_KEY = os.getenv("FULLENRICH_API_KEY")
FULLENRICH_BASE = "https://api.fullenrich.com/api/v1"
FULLENRICH_HEADERS = {
    "Authorization": f"Bearer {FULLENRICH_KEY}",
    "Content-Type": "application/json"
}
```

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| People table ID | Child table from `linkedin-finder` | yes (or CSV) |
| People CSV | `claude-code-gtm/csv/input/{campaign}/people_linkedin.csv` | yes (or table) |
| Provider preference | User choice | no (default: Prospeo) |
| Include mobile phones | User choice | no (default: no) |

## Provider Decision Tree

```
Have LinkedIn URLs?
  YES → Prospeo (fast, 1 credit/match, best with LinkedIn data)
  NO  → Fullenrich (waterfall, works with name + domain)

Need highest email hit rate?
  → Fullenrich (waterfall tries multiple providers)

Budget-conscious?
  → Prospeo first (1 credit/match), Fullenrich for misses

Need mobile phones?
  → Either (10 credits each), Fullenrich slightly better coverage

Want maximum coverage?
  → Waterfall: Prospeo first → Fullenrich for misses
```

Ask the user which approach they prefer, or recommend based on their data.

## Workflow

### Step 1: Load people data

**Option A: From Extruct people table (recommended)**

```python
people_table_id = "..."  # from linkedin-finder output

resp = requests.get(f"{BASE_URL}/tables/{people_table_id}/data", headers=EXTRUCT_HEADERS)
rows = resp.json().get("rows", [])

contacts = []
for r in rows:
    d = r.get("data", {})
    full_name = d.get("full_name", {}).get("value", {}).get("answer", "")
    profile_url = d.get("profile_url", {}).get("value", {}).get("answer", "")

    if not full_name or not profile_url:
        continue

    name_parts = full_name.strip().split(" ", 1)
    contacts.append({
        "first_name": name_parts[0],
        "last_name": name_parts[1] if len(name_parts) > 1 else "",
        "linkedin_url": profile_url,
        "role": d.get("role", {}).get("value", {}).get("answer", ""),
        "parent_row_id": r.get("parent_row_id", ""),
    })

print(f"Loaded {len(contacts)} contacts from people table")
```

**Option B: From CSV**

```python
import pandas as pd
df = pd.read_csv(f"claude-code-gtm/csv/input/{{campaign}}/people_linkedin.csv")
contacts = df.to_dict("records")
```

### Step 2: Check credits

Before running enrichment, check available credits:

**Prospeo:**
```python
# Credits shown in response headers after any API call
```

**Fullenrich:**
```python
resp = requests.get(f"{FULLENRICH_BASE}/account/credits", headers=FULLENRICH_HEADERS)
print(f"Fullenrich credits: {resp.json()['credits']}")
```

Present cost estimate:
- Prospeo: ~{N} credits (1/match email, 10/match mobile)
- Fullenrich: ~{N} credits (1/work email, 10/mobile)

### Step 3a: Enrich via Prospeo

Best when you have LinkedIn URLs. Fast, synchronous, up to 50 per batch.

```python
def enrich_via_prospeo(contacts, batch_size=50, enrich_mobile=False):
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
            else:
                entry["first_name"] = c["first_name"]
                entry["last_name"] = c["last_name"]
                entry["company_website"] = c.get("domain", "")
            data.append(entry)

        resp = requests.post(f"{PROSPEO_BASE}/bulk-enrich-person", headers=PROSPEO_HEADERS, json={
            "data": data,
            "only_verified_email": True,
            "enrich_mobile": enrich_mobile
        })
        result = resp.json()
        all_matched.extend(result.get("matched", []))
        all_not_matched.extend(result.get("not_matched", []))
        print(f"  Batch {i//batch_size + 1}: {len(result.get('matched', []))} matched, {len(result.get('not_matched', []))} missed")
        time.sleep(1)

    return all_matched, all_not_matched
```

### Step 3b: Enrich via Fullenrich

Best for highest hit rate. Async — needs polling or webhook. Up to 100 per batch.

```python
def enrich_via_fullenrich(contacts, batch_size=100):
    """Enrich contacts via Fullenrich. Async — poll for results."""
    enrichment_ids = []

    for i in range(0, len(contacts), batch_size):
        batch = contacts[i:i+batch_size]
        payload = []
        for c in batch:
            entry = {
                "first_name": c["first_name"],
                "last_name": c["last_name"],
                "domain": c.get("domain", "")
            }
            if c.get("linkedin_url"):
                entry["linkedin_url"] = c["linkedin_url"]
            payload.append(entry)

        resp = requests.post(f"{FULLENRICH_BASE}/contact/enrich/bulk", headers=FULLENRICH_HEADERS, json={
            "contacts": payload
        })
        eid = resp.json()["enrichment_id"]
        enrichment_ids.append(eid)
        print(f"  Batch {i//batch_size + 1}: enrichment_id = {eid}")
        time.sleep(1)

    return enrichment_ids


def poll_fullenrich(enrichment_id, max_polls=60, interval=30):
    """Poll Fullenrich for results. Average 30-90s per contact."""
    for attempt in range(max_polls):
        resp = requests.get(
            f"{FULLENRICH_BASE}/contact/enrich/bulk/{enrichment_id}",
            headers=FULLENRICH_HEADERS
        )
        data = resp.json()
        status = data["status"]
        if status == "completed":
            return data["results"]
        print(f"  Poll {attempt+1}: {status}")
        time.sleep(interval)
    return None
```

### Step 3c: Waterfall — Prospeo first, Fullenrich for misses

Run both providers sequentially for maximum coverage:

```python
# 1. Run all through Prospeo
matched, not_matched = enrich_via_prospeo(contacts)
print(f"Prospeo: {len(matched)} matched, {len(not_matched)} missed")

# 2. Run Prospeo misses through Fullenrich
if not_matched:
    # Rebuild contacts list from not_matched
    fullenrich_contacts = []
    for nm in not_matched:
        entry = {
            "first_name": nm.get("first_name", ""),
            "last_name": nm.get("last_name", ""),
            "domain": nm.get("company_website", ""),
        }
        if nm.get("linkedin_url"):
            entry["linkedin_url"] = nm["linkedin_url"]
        fullenrich_contacts.append(entry)

    enrichment_ids = enrich_via_fullenrich(fullenrich_contacts)

    # Poll each batch
    fullenrich_results = []
    for eid in enrichment_ids:
        results = poll_fullenrich(eid)
        if results:
            fullenrich_results.extend(results)

    print(f"Fullenrich: {len(fullenrich_results)} additional results")

# 3. Merge
all_results = matched + fullenrich_results
```

### Step 4: Deduplicate and clean

```python
def clean_contacts(prospeo_matched, fullenrich_results=None):
    """Deduplicate by email, filter out invalid."""
    seen_emails = set()
    clean = []

    # Process Prospeo results
    for c in prospeo_matched:
        person = c.get("person", {})
        email = person.get("email")
        if not email or email in seen_emails:
            continue
        seen_emails.add(email)
        clean.append({
            "first_name": person.get("first_name", ""),
            "last_name": person.get("last_name", ""),
            "email": email,
            "email_verified": person.get("email_verified", False),
            "job_title": person.get("title", ""),
            "company_name": c.get("company", {}).get("name", ""),
            "domain": c.get("company", {}).get("website", c.get("company", {}).get("domain", "")),
            "linkedin_url": person.get("linkedin_url", ""),
            "phone": person.get("mobile", ""),
            "location": person.get("location", ""),
            "source": "prospeo",
        })

    # Process Fullenrich results
    if fullenrich_results:
        for c in fullenrich_results:
            work_email = c.get("work_email", {})
            email = work_email.get("email")
            verification = work_email.get("verification_status", "")
            if not email or email in seen_emails or verification == "INVALID":
                continue
            seen_emails.add(email)
            profile = c.get("profile", {})
            company = c.get("company", {})
            clean.append({
                "first_name": profile.get("first_name", c.get("input", {}).get("first_name", "")),
                "last_name": profile.get("last_name", c.get("input", {}).get("last_name", "")),
                "email": email,
                "email_verified": verification in ("DELIVERABLE", "HIGH_PROBABILITY"),
                "job_title": profile.get("title", ""),
                "company_name": company.get("name", ""),
                "domain": company.get("domain", ""),
                "linkedin_url": profile.get("linkedin_url", ""),
                "phone": c.get("mobile_phone", {}).get("number", ""),
                "location": profile.get("location", ""),
                "source": "fullenrich",
            })

    return clean
```

### Step 5: Output contact CSV

Save the enriched contact list ready for `email-generation`:

```python
import pandas as pd

df = pd.DataFrame(clean)
df.to_csv(f"claude-code-gtm/csv/input/{{campaign}}/contacts.csv", index=False)
```

### Step 6: Review with user

Present summary:

```
Enrichment Results:
- Contacts submitted: N
- Emails found: N (X% hit rate)
- Emails verified: N
- Phones found: N
- No match: N
- Provider breakdown: Prospeo N / Fullenrich N
```

Show a sample of 10 contacts for spot-checking:

| Name | Title | Company | Email | Phone | Source |
|------|-------|---------|-------|-------|--------|
| ... | ... | ... | ... | ... | ... |

Ask:
- "Hit rate look acceptable? (>60% is good, >80% is great)"
- "Want to run the misses through another provider?"
- "Ready to proceed to `email-generation`?"

## Prospeo-Only Quick Path

For speed and simplicity when you have LinkedIn URLs:

```python
# 1. Load from Extruct people table
contacts = load_from_people_table(people_table_id)

# 2. Enrich via Prospeo
matched, not_matched = enrich_via_prospeo(contacts)

# 3. Clean and save
clean = clean_contacts(matched)
pd.DataFrame(clean).to_csv("contacts.csv", index=False)
```

## API References

- [references/prospeo-api.md](references/prospeo-api.md) — Prospeo Search, Enrich, Bulk Enrich
- [references/fullenrich-api.md](references/fullenrich-api.md) — Fullenrich Bulk Enrich, Reverse Lookup
