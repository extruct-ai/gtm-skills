---
name: linkedin-finder
description: >
  Find LinkedIn profiles of decision makers at target companies using Extruct's
  company_people_finder. Takes a company table, adds a people finder column,
  and produces a linked child people table with names, roles, and LinkedIn URLs.
  Triggers on: "find linkedin", "find people", "find contacts", "find decision makers",
  "people search", "linkedin search", "who to contact", "find profiles".
---

# LinkedIn Finder

Find the right people at target companies via Extruct. Produces a people table with LinkedIn profiles.

## Where This Fits in the Pipeline

```
segment-and-tier → linkedin-finder → email-finder → email-generation → copy-feedback → run-instantly
```

After you know WHICH companies to target, this skill finds WHO to contact. The next step (`email-finder`) gets their verified emails and phones.

## Auth

```python
from dotenv import load_dotenv
load_dotenv()
import os, requests, json, time

API_TOKEN = os.getenv("EXTRUCT_API_TOKEN")
BASE_URL = "https://api.extruct.ai/v1"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}
```

## Official API Reference

- https://www.extruct.ai/docs/api-reference/introduction

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Extruct table ID | Company table from `list-building` or `table-enrichment` | yes |
| Target roles | User input or context file ICP | yes |
| Max results per company | User preference (default: 5) | no |

## Workflow

### Step 1: Confirm the table

Fetch table metadata to confirm it's a company table with rows:

```python
resp = requests.get(f"{BASE_URL}/tables/{table_id}", headers=HEADERS)
resp.raise_for_status()
table = resp.json()
num_rows = table.get("num_rows")
if num_rows is None:
    num_rows = (table.get("status") or {}).get("num_rows", "unknown")
print(f"Table: {table['name']}, Kind: {table['kind']}, Rows: {num_rows}")
```

### Step 2: Define roles

Ask the user: "Who are we trying to reach at these companies?"

Then expand into a role list. Use **broad role descriptions**, not exact titles — Extruct's people finder matches on role semantics, not exact title strings.

**Role list guidelines:**
- 3-7 roles is the sweet spot
- Use broad terms: "VP Sales" not "Vice President of Enterprise Sales"
- Cover the decision maker + influencer + champion if possible
- Include department variations

**Role expansion examples:**

```
User says: "Sales and ops leaders"
→ Roles: ["VP Sales", "Head of Sales", "Sales Operations", "RevOps", "Business Development", "CRO"]

User says: "People who buy data tools"
→ Roles: ["Revenue Operations", "Sales Operations", "Data Operations", "Business Intelligence", "CRM Admin"]

User says: "Innovation and strategy at corporates"
→ Roles: ["Head of Innovation", "VP Strategy", "Corporate Development", "Ventures", "Technology Scouting"]
```

**Read context file** for ICP role targets if available:
```
claude-code-gtm/context/extruct_context.md → ## ICP → Roles column
```

### Step 3: Add company_people_finder column

```python
column_config = {
    "kind": "company_people_finder",
    "name": "Key Decision Makers",
    "key": "decision_makers",
    "value": {
        "roles": ["VP Sales", "Head of Sales", "Revenue Operations"],
        "provider": "research_pro",
        "max_results": 5
    }
}

resp = requests.post(
    f"{BASE_URL}/tables/{table_id}/columns",
    headers=HEADERS,
    json={"column_configs": [column_config]}
)
resp.raise_for_status()
column_id = resp.json()[0]["id"]
print(f"Column created: {column_id}")
```

| Param | Description | Recommended |
|-------|-------------|-------------|
| `roles` | Broad role descriptions to search for | 3-7 roles |
| `provider` | Search provider | `research_pro` (always) |
| `max_results` | Max people per company | 3-5 (more = slower + noisier) |

### Step 4: Trigger enrichment run

```python
resp = requests.post(
    f"{BASE_URL}/tables/{table_id}/run",
    headers=HEADERS,
    json={"columns": [column_id]}
)
run_id = resp.json()["id"]
num_cells = resp.json()["num_requested_cells"]
print(f"Run {run_id}: {num_cells} cells queued")
```

### Step 5: Monitor and discover child table

The `company_people_finder` column auto-creates a **child people table**. Check the parent table's `child_relationships` field:

```python
resp = requests.get(f"{BASE_URL}/tables/{table_id}", headers=HEADERS)
relationships = resp.json().get("child_relationships", [])
for rel in relationships:
    if rel["relationship_type"] == "company_people":
        people_table_id = rel["table_id"]
        print(f"People table: {people_table_id}")
```

The child people table has auto-created columns:

| Column | Key | Kind | Description |
|--------|-----|------|-------------|
| Person Input | `input` | input | Raw person context string |
| Full Name | `full_name` | agent | Parsed full name |
| Role | `role` | agent | Current role/title |
| Profile URL | `profile_url` | agent (url) | LinkedIn URL |

### Step 6: Optionally add LinkedIn data column

For richer profile data (experience, education, skills), add a `linkedin` agent column to the people table:

This is optional and may be expensive at scale. Confirm with the user before running.

```python
linkedin_col = {
    "kind": "agent",
    "key": "linkedin_data",
    "name": "LinkedIn Data",
    "value": {
        "agent_type": "linkedin",
        "prompt": "{profile_url}"
    }
}

resp = requests.post(
    f"{BASE_URL}/tables/{people_table_id}/columns",
    headers=HEADERS,
    json={"column_configs": [linkedin_col]}
)
resp.raise_for_status()
linkedin_col_id = resp.json()[0]["id"]

# Trigger run for linkedin_data only
run_resp = requests.post(
    f"{BASE_URL}/tables/{people_table_id}/run",
    headers=HEADERS,
    json={"columns": [linkedin_col_id]}
)
run_resp.raise_for_status()
```

This is optional — skip if you only need name + role + LinkedIn URL for the `email-finder` step.

### Step 7: Fetch and review people data

```python
resp = requests.get(f"{BASE_URL}/tables/{people_table_id}/data", headers=HEADERS)
rows = resp.json().get("rows", [])

people = []
for r in rows:
    d = r.get("data", {})
    people.append({
        "full_name": d.get("full_name", {}).get("value", {}).get("answer", ""),
        "role": d.get("role", {}).get("value", {}).get("answer", ""),
        "profile_url": d.get("profile_url", {}).get("value", {}).get("answer", ""),
        "parent_row_id": r.get("parent_row_id", ""),
    })

print(f"People found: {len(people)}")
```

Present summary:
- Total companies in table: N
- People found: N
- Avg people per company: N
- Companies with 0 people: N

Show a sample of 10 people for spot-checking:

| Name | Role | LinkedIn URL | Parent Company |
|------|------|-------------|----------------|
| ... | ... | ... | ... |

Ask:
- "Does the role mix look right?"
- "Any roles missing? Want to add more?"
- "Ready to proceed to `email-finder` for verified emails?"

### Step 8: Export for email-finder

Save the people list for the next step:

```python
import pandas as pd

df = pd.DataFrame(people)
df.to_csv(f"claude-code-gtm/csv/input/{{campaign}}/people_linkedin.csv", index=False)
```

The `email-finder` skill takes this CSV (or reads the people table directly) and enriches with verified emails via Prospeo/Fullenrich.

## Output

| Output | Format | Location |
|--------|--------|----------|
| People table | Extruct child table | Auto-created, linked to parent |
| People CSV | CSV with name, role, LinkedIn URL | `claude-code-gtm/csv/input/{campaign}/people_linkedin.csv` |

## Key Table IDs to Pass Forward

After this skill completes, pass these to `email-finder`:
- **People table ID** — for direct API access to people data
- **Parent table ID** — for cross-referencing company data
- **Campaign slug** — for file paths

## API Reference

See [references/api_reference.md](references/api_reference.md) for the full `company_people_finder` column spec, child table behavior, and people table columns.
