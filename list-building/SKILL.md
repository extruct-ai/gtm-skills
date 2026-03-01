---
name: list-building
description: >
  Build targeted company lists for outbound campaigns using the Extruct API.
  Use when the user wants
  to: (1) find companies matching an ICP, (2) build a prospect or outbound
  list, (3) search for companies by description, (4) discover companies in a
  market segment, (5) create a target account list, (6) research a competitive
  landscape, (7) find lookalike companies from a seed list. Triggers on: "find
  companies", "build a list", "company search", "prospect list", "target
  accounts", "outbound list", "discover companies", "ICP search", "lookalike
  search", "seed company".
---

# List Building

Build company lists using Extruct API methods, guided by a decision tree. Reads from the company context file for ICP and seed companies.

## Official API Reference

- https://www.extruct.ai/docs/api-reference/introduction

## Decision Tree

Before running any queries, determine the right approach:

```
Have a seed company from win cases or context file?
  YES → Method 1: Lookalike Search (pass seed domain)
  NO  ↓

New vertical, need broad exploration?
  YES → Method 2: Semantic Search (3-5 queries from different angles)
  NO  ↓

Need qualification against specific criteria?
  YES → Method 3: Discovery API (criteria-scored async research)
  NO  ↓

Need maximum coverage?
  YES → Combine Search + Discovery (~15% overlap expected)
```

## Before You Start

Read the company context file if it exists:

```
claude-code-gtm/context/extruct_context.md
```

Extract:
- **ICP profiles** — for query design and filters
- **Win cases** — for seed companies in lookalike mode
- **DNC list** — domains to exclude from results

## Auth

```python
import os, json, requests, time
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("EXTRUCT_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
BASE = "https://api.extruct.ai/v1"
```

## Method 1: Lookalike Search

Use when you have a seed company (from win cases, existing customers, or user input). Use the Similar Companies endpoint with a company identifier (domain or UUID).

```python
company_identifier = "seedcompany.com"  # domain or company UUID

resp = requests.get(f"{BASE}/companies/{company_identifier}/similar", headers=HEADERS, params={
    "filters": json.dumps({
        "include": {"size": ["11-50", "51-200"], "country": ["United States"]}
    }),
    "limit": 100,
    "offset": 0,
})
resp.raise_for_status()
results = resp.json()["results"]
```

**When to use lookalike:**
- You have a happy customer and want more like them
- Context file has win cases with domains
- User says "find companies similar to X"

**Tips:**
- Run multiple similar-company searches with different seed companies for broader coverage
- Combine with filters to constrain geography or size
- Deduplicate across runs by domain
- Default to `limit=100`; increase up to `200` when broader coverage is needed

## Method 2: Semantic Search — Fast, Broad

`GET /v1/companies/search` — instant semantic search against Extruct's 4M+ company index.

```python
resp = requests.get(f"{BASE}/companies/search", headers=HEADERS, params={
    "q": "supplier discovery platform with searchable database",
    "filters": json.dumps({
        "include": {"size": ["11-50", "51-200"], "country": ["United States"]},
        "range": {"founded": {"min": 2018}}
    }),
    "limit": 100,
})
resp.raise_for_status()
results = resp.json()["results"]
```

**Query strategy:**
- Write 3-5 queries per campaign, each from a different angle on the same ICP
- Describe the product/use case, not the company type
- Deduplicate across queries by domain — overlap is expected
- Default to `limit=100` per query; increase up to `200` when needed
- Target 200-800 companies total across all queries

**Filters:** See [references/search-filters.md](references/search-filters.md)

**Response fields:** `name`, `domain`, `short_description`, `founding_year`, `employee_count`, `hq_country`, `hq_city`, `relevance_score`

## Method 3: Discovery API — Deep, Qualified

`POST /v1/discovery_tasks` — async deep web research with criteria scoring.

```python
resp = requests.post(f"{BASE}/discovery_tasks", headers=HEADERS, json={
    "query": "US-based SaaS startups that offer supplier discovery and search features...",
    "desired_num_results": 50,
    "criteria": [
        {"key": "has_feature", "name": "Core Feature",
         "criterion": "Company offers X as a core product feature"},
        {"key": "needs_data", "name": "Data Need",
         "criterion": "Company relies on external data to power Y"},
    ],
})
resp.raise_for_status()
task_id = resp.json()["id"]
```

**Poll for completion:**
```python
while True:
    status = requests.get(f"{BASE}/discovery_tasks/{task_id}", headers=HEADERS).json()
    # status["status"]: created | in_progress | done | failed
    if status["status"] in ("done", "failed"):
        break
    time.sleep(60)  # poll once a minute
```

**Fetch results when done:**
```python
results = requests.get(
    f"{BASE}/discovery_tasks/{task_id}/results",
    headers=HEADERS,
    params={"limit": 100, "offset": 0}
).json()["results"]
```

**Query strategy:**
- Write queries like a job description — 2-3 sentences describing the ideal company
- Use criteria to auto-qualify — each company gets graded 1-5 per criterion
- Default `desired_num_results=50` for first pass; expand after quality review
- Use up to 5 criteria per task; keep criteria focused and non-overlapping
- Run separate tasks for different ICP segments
- Scans many candidates to find qualified matches — runtime depends on query scope
- Up to 250 results per task

See [references/discovery-api.md](references/discovery-api.md) for full parameters.

## Upload to Table

Create a `company` kind table — Extruct auto-enriches each domain with a Company Profile.

```python
table = requests.post(f"{BASE}/tables", headers=HEADERS, json={
    "name": "My Target List",
    "kind": "company",
    "column_configs": [{"kind": "input", "name": "Website", "key": "input"}],
}).json()
table_id = table["id"]

# Upload in batches of 50
for i in range(0, len(domains), 50):
    batch = [{"data": {"input": d}} for d in domains[i:i+50]]
    requests.post(f"{BASE}/tables/{table_id}/rows", headers=HEADERS, json={"rows": batch})
    time.sleep(0.5)
```

Pass `"run": True` in the rows payload to trigger agent columns on upload.

## Step 5 Note: Re-run After Enrichment

After the `table-enrichment` skill adds data points to this list, consider re-running list building using enrichment insights as Discovery criteria. For example:

- If enrichment reveals that "companies using legacy ERP" are the best fit, create a Discovery task with that as a criterion
- If enrichment shows a geographic cluster, run a Search with tighter geo filters
- This creates a feedback loop: list → enrich → learn → refine list

## Result Size Guidance

| Campaign stage | Target list size | Method |
|---------------|-----------------|--------|
| Exploration | 50-100 | Search (2-3 queries) |
| First campaign | 200-500 | Search (5 queries) + Discovery |
| Scaling | 500-2000 | Discovery (high desired_num_results) + multiple Search |

## Workflow

1. Read context file for ICP, seed companies, and DNC list
2. Follow the decision tree to pick the right method
3. Draft queries (3-5 for Search, 1-2 for Discovery)
4. Run queries and collect results
5. Deduplicate across all results by domain
6. Remove DNC domains
7. Upload to Extruct company table for auto-enrichment
8. Add agent columns if user needs custom research
9. Ask user for preferred output: Extruct table link, local CSV, or both
