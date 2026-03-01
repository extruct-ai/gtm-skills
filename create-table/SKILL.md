---
name: create-table
description: >
  Create an Extruct company table from user-provided data, upload rows, and
  optionally add enrichment columns. Handles the full flow: parse input (CSV,
  pasted list, or structured data), create or reuse a table, upload domains in
  batches, add agent columns, and trigger enrichment. Triggers on: "create table",
  "upload companies", "add to extruct", "new extruct table", "import companies",
  "upload list to extruct".
---

# Create Table

End-to-end workflow: parse company data → create/reuse Extruct table → upload rows → add columns → run enrichment.

## Auth

```python
import os, json, requests, time
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("EXTRUCT_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
BASE = "https://api.extruct.ai/v1"
```

## Workflow

### 1. Parse input data

Accept data in any of these formats:

**Pasted list** (most common): User pastes company names, URLs, and metadata as freeform text. Parse into structured records. Extract domains by stripping `https://`, `http://`, `www.`, and trailing slashes.

```python
def extract_domain(url):
    """Extract clean domain from URL."""
    domain = url.replace("https://", "").replace("http://", "").rstrip("/")
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.lower()
```

**CSV file**: Read with pandas, map columns.

**Extruct table URL**: Fetch data from existing table via API.

Key rules:
- Skip entries with no URL (e.g., "Stealth" companies)
- Deduplicate by domain
- Collect metadata fields the user wants to preserve (country, stage, industry, etc.)

### 2. Decide: create new table or add to existing

Ask the user:
- **New table**: Create via `POST /tables`
- **Existing table**: User provides table ID or URL (`https://app.extruct.ai/tables/{id}`)

#### Create a new company table

```python
payload = {
    "name": "Table Name",
    "kind": "company",
    "column_configs": [
        {"kind": "input", "name": "Website", "key": "input"}
    ]
}
resp = requests.post(f"{BASE}/tables", headers=HEADERS, json=payload)
table_id = resp.json()["id"]
```

The `company` kind auto-enriches each domain with Company Profile, Company Name, and Company Website columns.

### 3. Upload rows in batches

```python
domains = [extract_domain(url) for url in urls]

for i in range(0, len(domains), 50):
    batch = domains[i:i+50]
    rows = [{"data": {"input": d}} for d in batch]
    resp = requests.post(
        f"{BASE}/tables/{table_id}/rows",
        headers=HEADERS,
        json={"rows": rows}
    )
    time.sleep(0.5)
```

Batch size: 50 rows per request. Add 0.5s delay between batches.

Report progress: "Batch 1: uploaded 50 rows OK"

### 4. Add agent columns (optional)

If the user wants enrichment columns (industry, funding, etc.), add them after upload.

#### Select column (classification from predefined options)

Best for: industry, stage, vertical, region — when you know the categories.

```python
requests.post(f"{BASE}/tables/{table_id}/columns", headers=HEADERS, json={
    "column_configs": [{
        "kind": "agent",
        "name": "Industry",
        "key": "industry",
        "value": {
            "agent_type": "llm",
            "prompt": "Based on the company profile of {input}, classify this company into ONE of the provided categories. Pick the single best match.",
            "output_format": "select",
            "labels": ["Accounting", "Insurance", "IT MSP", "Logistics", ...]
        }
    }]
})
```

Use `llm` agent type for classification (no web research needed — uses existing company profile data).

#### Text column (free-form research)

Best for: funding details, tech stack, competitive analysis.

```python
requests.post(f"{BASE}/tables/{table_id}/columns", headers=HEADERS, json={
    "column_configs": [{
        "kind": "agent",
        "name": "Funding",
        "key": "funding",
        "value": {
            "agent_type": "research_pro",
            "prompt": "Find the total funding raised by {input}. Include latest round, amount, date, and lead investors.",
            "output_format": "text"
        }
    }]
})
```

Use `research_pro` for data that requires web research.

See the [table-enrichment skill](../table-enrichment/SKILL.md) for full column types and output formats.

### 5. Trigger enrichment

```python
resp = requests.post(f"{BASE}/tables/{table_id}/run", headers=HEADERS, json={})
run = resp.json()
print(f"Run started: {run['num_requested_cells']} cells queued")
```

### 6. Report to user

Provide:
- Table URL: `https://app.extruct.ai/tables/{table_id}`
- Row count uploaded
- Columns added
- Cells queued for enrichment
- Any rows skipped (stealth, duplicates, invalid URLs)

## Input Parsing Patterns

### Freeform pasted list (5-line groups)

```
Company Name
URL (or "Stealth")
Country
Industry
Funding Stage
```

Parse by splitting into 5-line chunks. Filter where URL == "Stealth".

### CSV

```python
import pandas as pd
df = pd.read_csv(path)
# Map columns: look for "website", "url", "domain", "Company Website"
# Extract domain from whichever column contains URLs
```

### Single-column domain list

```
example.com
startup.io
company.ai
```

Direct upload — each line is a domain.

## Column Decision Guide

| User says | Column type | Agent type | Output format |
|-----------|-------------|------------|---------------|
| "add industry" | agent | `llm` | `select` with labels |
| "add funding" | agent | `research_pro` | `text` |
| "classify by vertical" | agent | `llm` | `select` with labels |
| "find their tech stack" | agent | `research_pro` | `text` |
| "score fit 1-5" | agent | `llm` or `research_reasoning` | `grade` |
| "tag multiple categories" | agent | `llm` | `multiselect` with labels |

## Common Pitfalls

- **Domain format**: Strip protocol and trailing slash. `https://www.example.com/` → `example.com`
- **Stealth companies**: Skip — no domain to enrich
- **Duplicates**: Deduplicate by domain before upload
- **Batch limits**: Max 50 rows per API call
- **Column labels**: For `select`/`multiselect`, collect unique values from user data to build the label list
- **Run timing**: Trigger run AFTER all rows and columns are added
