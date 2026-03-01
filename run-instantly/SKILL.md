---
name: run-instantly
description: >
  Upload finalized emails to Instantly for sequencing and sending. Maps fields
  to Instantly lead schema, creates or finds campaigns, uploads leads with
  dedup, and provides a pre-send verification checklist. Triggers on: "upload
  to instantly", "run instantly", "send emails", "instantly campaign", "push
  to instantly", "start campaign", "load into instantly".
---

# Run Instantly

Upload finalized emails to Instantly for sequencing and sending. Last step in the pipeline.

## Auth

```python
from dotenv import load_dotenv
load_dotenv()
import os, requests, json, time

INSTANTLY_API_KEY = os.getenv("INSTANTLY_API_KEY")
INSTANTLY_BASE = "https://api.instantly.ai/api/v2"
INSTANTLY_HEADERS = {
    "Authorization": f"Bearer {INSTANTLY_API_KEY}",
    "Content-Type": "application/json"
}
```

## Workflow

### Step 1: Read final emails

Load the finalized email CSV (output from `email-generation`):

```python
import pandas as pd
emails_df = pd.read_csv("claude-code-gtm/csv/output/{campaign}/emails.csv")
```

Verify required columns exist:
- `email` — recipient email address
- `first_name` — for personalization
- `company_name` — for tracking
- `first_paragraph` through `fourth_paragraph` (or `email_body`)

### Step 2: Check DNC list

Read the context file and remove any domains on the DNC list:

```python
# Load DNC domains from context file
# Filter out any matching domains from the email list
dnc_domains = [...]  # parsed from context file
emails_df = emails_df[~emails_df["domain"].isin(dnc_domains)]
```

Report how many were removed.

### Step 3: Create or find campaign

**List existing campaigns:**

```python
resp = requests.get(
    f"{INSTANTLY_BASE}/campaigns",
    headers=INSTANTLY_HEADERS,
    params={"limit": 100}
)
campaigns = resp.json()
```

**Create new campaign:**

```python
resp = requests.post(
    f"{INSTANTLY_BASE}/campaigns",
    headers=INSTANTLY_HEADERS,
    json={"name": "Campaign Name - YYYY-MM-DD"}
)
campaign_id = resp.json()["id"]
```

Ask the user:
- Use existing campaign? (show list)
- Create new one? (suggest name based on vertical + date)

### Step 4: Map fields to Instantly lead schema

Instantly lead schema:

```python
lead = {
    "email": row["email"],
    "first_name": row["first_name"],
    "last_name": row.get("last_name", ""),
    "company_name": row["company_name"],
    "personalization": row.get("first_paragraph", ""),
    "phone": row.get("phone", ""),
    "website": row.get("domain", ""),
    "custom_variables": {
        "second_paragraph": row.get("second_paragraph", ""),
        "third_paragraph": row.get("third_paragraph", ""),
        "fourth_paragraph": row.get("fourth_paragraph", ""),
        "fifth_paragraph": row.get("fifth_paragraph", ""),
        "hypothesis": row.get("hypothesis_name", ""),
        "tier": row.get("tier", ""),
    }
}
```

### Step 5: Upload leads in batches

```python
def upload_leads(campaign_id, leads, batch_size=100):
    """Upload leads to Instantly campaign with dedup."""
    total = len(leads)
    uploaded = 0
    skipped = 0

    for i in range(0, total, batch_size):
        batch = leads[i:i+batch_size]
        resp = requests.post(
            f"{INSTANTLY_BASE}/leads",
            headers=INSTANTLY_HEADERS,
            json={
                "campaign_id": campaign_id,
                "leads": batch,
                "skip_if_in_workspace": True,  # dedup against entire workspace
            }
        )
        result = resp.json()
        uploaded += result.get("uploaded", 0)
        skipped += result.get("skipped", 0)
        time.sleep(0.5)  # rate limiting

    return {"uploaded": uploaded, "skipped": skipped, "total": total}
```

Report: uploaded count, skipped (dedup) count, total attempted.

### Step 6: Pre-send verification checklist

Present this checklist to the user BEFORE they activate the campaign:

```markdown
## Pre-Send Verification Checklist

Campaign: [name]
Leads uploaded: [N]
Leads skipped (dedup): [N]

### Verify in Instantly UI:

- [ ] **Email accounts connected** — at least 2-3 sending accounts are linked and warmed
- [ ] **Sending schedule set** — check timezone, sending hours, daily limits
- [ ] **Email sequence configured** — first email + follow-up(s) are set up in the campaign
- [ ] **Custom variables working** — preview 3-5 emails to confirm {{variables}} render correctly
- [ ] **Unsubscribe link present** — required for compliance
- [ ] **DNC list checked** — confirm no blacklisted domains made it through
- [ ] **Reply handling set** — auto-stop sequence on reply is enabled
- [ ] **Warmup active** — sending accounts have adequate warmup history

### Sample emails to spot-check:

[Show 3 random emails from the upload for the user to visually verify]
```

### Step 7: Remind about manual activation

**Never auto-activate a campaign.** Always tell the user:

> "Leads are uploaded. Please review the campaign in Instantly, check the sequence and sending settings, then manually activate when ready. I will not start the campaign automatically."

## After Sending: Feedback Loop

After the campaign has been running (typically 1-2 weeks), prompt the user to run the feedback loop:

1. Export results from Instantly (opens, replies, bounces)
2. Run `company-context-builder` in feedback loop mode to update Campaign History
3. Use results to refine hypotheses and improve future campaigns

## API Reference

See [references/instantly-api.md](references/instantly-api.md) for Instantly API endpoints and field mappings.
