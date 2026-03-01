# Extruct API — People Finder Reference

## Base Config

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

## company_people_finder Column

Finds people (LinkedIn profiles) at a company. Not an `agent` kind — it's a dedicated column type.

```json
{
  "kind": "company_people_finder",
  "name": "Key Decision Makers",
  "key": "decision_makers",
  "value": {
    "roles": ["VP Sales", "Head of Sales", "Business Development"],
    "provider": "research_pro",
    "max_results": 5
  }
}
```

| Param | Description |
|-------|-------------|
| `roles` | List of role descriptions to search for (broad terms, not exact titles) |
| `provider` | `research_pro` (recommended) |
| `max_results` | Max people per company (3-5 recommended) |

**Output:** Returns a list of people with name, title, LinkedIn URL, and company association.

## Child Table Behavior

Adding a `company_people_finder` column to a company table automatically creates a linked child table of kind `people`. The relationship appears in the parent table's `child_relationships` field:

```json
{
  "child_relationships": [
    {
      "table_id": "child-people-table-uuid",
      "relationship_type": "company_people"
    }
  ]
}
```

The child people table has columns:

| Column | Key | Kind | Output |
|--------|-----|------|--------|
| Person Input | `input` | input | Raw person context string |
| Full Name | `full_name` | agent | Parsed full name |
| Role | `role` | agent | Current role/title |
| Profile URL | `profile_url` | agent (url) | LinkedIn URL |

Cell values are nested: `row["data"]["full_name"]["value"]["answer"]`

Fetch people data via `GET /v1/tables/{child_table_id}/data`.

## LinkedIn Data Column (optional)

Add to the people table for richer profile data:

```json
{
  "kind": "agent",
  "key": "linkedin_data",
  "name": "LinkedIn Data",
  "value": {
    "agent_type": "linkedin",
    "prompt": "{profile_url}"
  }
}
```

Uses the `linkedin` agent type to parse the person's LinkedIn profile. References the `profile_url` column key (not `linkedin_url`).

## Trigger Enrichment Run

```
POST /v1/tables/{table_id}/run
```

Run specific columns only:
```json
{"columns": ["column-uuid"]}
```

Run all pending cells:
```json
{}
```

## Read Table Data

```
GET /v1/tables/{table_id}/data
```

Returns full table with all rows and cell values.
