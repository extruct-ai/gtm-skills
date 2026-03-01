---
name: table-enrichment
description: >
  Add research-powered enrichment columns to Extruct company tables via the API.
  Use when the user wants to add enrichment columns (e.g. funding, verticals,
  tech stack) to an existing Extruct table, run column configs from
  data-points-builder, or monitor enrichment progress. Triggers on: "enrich",
  "add column", "add data point", "research column", "enrich table",
  "enrichment", "add a field", "run enrichment", "monitor enrichment".
---

# Table Enrichment

Add research-powered enrichment columns to Extruct company tables.

## Auth

```python
from dotenv import load_dotenv
import os, requests, json, time
load_dotenv()

API_TOKEN = os.getenv("EXTRUCT_API_TOKEN")
BASE_URL = "https://api.extruct.ai/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}
```

## Workflow

### 1. Confirm the table

Get the table ID from the user (URL or ID). Fetch table metadata to confirm:

```python
resp = requests.get(f"{BASE_URL}/tables/{table_id}", headers=HEADERS)
table = resp.json()
```

Show the user: table name, row count, existing columns.

### 2. Get column configs

Two paths:

**Path A: From data-points-builder** — User has `column_configs` ready. Confirm and proceed.

**Path B: Design on the fly** — Confirm with the user:

1. **What data point?** — what to research (e.g. "funding stage", "primary vertical", "tech stack")
2. **Output format** — pick the right format:

| Format | When to use | Extra params |
|---|---|---|
| `text` | Free-form research output | — |
| `number` / `money` | Numeric data (revenue, headcount) | — |
| `select` | Single choice from known categories | `labels: [...]` |
| `multiselect` | Multiple tags from known categories | `labels: [...]` |
| `json` | Structured multi-field data | `output_schema: {...}` |
| `grade` | 1-5 score | — |
| `label` | Single tag from list | `labels: [...]` |
| `date` | Date values | — |
| `url` / `email` / `phone` | Contact info | — |

3. **Agent type** — default `research_pro`. Use `llm` when no web research needed (classification from existing profile data).

### 3. Write the prompt

Craft a clear prompt using `{input}` for the row's domain value. Prompt guidelines:

- Be specific about what to find
- Specify the exact output format in the prompt (e.g. "Return ONLY a number in millions USD")
- Include fallback instruction (e.g. "If not found, return N/A")
- For `select`/`multiselect`, the labels constrain the output — the prompt should guide which label to pick

### 4. Create the column(s)

```python
resp = requests.post(
    f"{BASE_URL}/tables/{table_id}/columns",
    headers=HEADERS,
    json={"column_configs": column_configs}
)
new_column_ids = [col["id"] for col in resp.json()]
```

### 5. Trigger enrichment (only the new columns)

**Important:** Always scope the run to the newly created column(s) only. Passing an empty body runs ALL pending cells across ALL columns, which re-triggers already-completed enrichments.

```python
resp = requests.post(
    f"{BASE_URL}/tables/{table_id}/run",
    headers=HEADERS,
    json={"columns": new_column_ids}
)
```

Report: run ID, rows queued, and table URL.

### 6. Monitor progress

Poll the table to track enrichment progress. Show a progress update every 30 seconds.

```python
def monitor_enrichment(table_id, column_ids, interval=30, max_polls=40):
    """Monitor enrichment progress. Polls every `interval` seconds."""
    for i in range(max_polls):
        resp = requests.get(f"{BASE_URL}/tables/{table_id}/data", headers=HEADERS)
        data = resp.json()
        rows = data.get("rows", [])
        total = len(rows)

        if total == 0:
            print("No rows found.")
            return

        # Count completed cells for our columns
        completed = 0
        pending = 0
        failed = 0

        for row in rows:
            for col_id in column_ids:
                cell = row.get("cells", {}).get(col_id, {})
                status = cell.get("status", "pending")
                if status == "done":
                    completed += 1
                elif status == "failed":
                    failed += 1
                else:
                    pending += 1

        total_cells = total * len(column_ids)
        pct = (completed / total_cells * 100) if total_cells > 0 else 0
        print(f"Progress: {completed}/{total_cells} cells ({pct:.0f}%) | Failed: {failed} | Pending: {pending}")

        if pending == 0:
            print("Enrichment complete.")
            return

        time.sleep(interval)

    print("Monitoring timed out. Check the table in Extruct UI.")
```

Show the user:
- Current % complete
- Number of failed cells (if any)
- Estimated time remaining (based on rate so far)

### 7. Quality spot-check

After enrichment completes (or after 50%+ is done), fetch a sample and display for review.

```python
def spot_check(table_id, column_ids, sample_size=5):
    """Fetch a sample of enriched rows for quality review."""
    resp = requests.get(f"{BASE_URL}/tables/{table_id}/data", headers=HEADERS)
    data = resp.json()
    rows = data.get("rows", [])

    # Filter to rows where our columns have data
    enriched = [r for r in rows if any(
        r.get("cells", {}).get(cid, {}).get("status") == "done"
        for cid in column_ids
    )]

    sample = enriched[:sample_size]

    for row in sample:
        domain = row.get("data", {}).get("input", "unknown")
        print(f"\n--- {domain} ---")
        for col_id in column_ids:
            cell = row.get("cells", {}).get(col_id, {})
            value = cell.get("value", "N/A")
            print(f"  {col_id}: {value}")
```

**Present to user as a table.** Ask:
- "Does the data quality look right?"
- "Any columns returning garbage or N/A too often?"
- "Should we adjust any prompts and re-run?"

If quality issues are found:
1. Delete the problematic column
2. Adjust the prompt
3. Re-create and re-run

## API Reference

See [references/api_reference.md](references/api_reference.md) for full API spec: all output formats, agent types, prompt variables, and endpoints.
