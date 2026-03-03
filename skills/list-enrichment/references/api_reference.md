# Extruct API — Column & Enrichment Reference

## Base Config

```
Base URL: https://api.extruct.ai/v1
Auth header: Authorization: Bearer $EXTRUCT_API_TOKEN
Content-Type: application/json
```

## Add Column to Existing Table

```
POST /v1/tables/{table_id}/columns
```

Payload:

```json
{
  "column_configs": [
    {
      "kind": "agent",
      "name": "Column Display Name",
      "key": "column_key_snake_case",
      "value": {
        "agent_type": "research_pro",
        "prompt": "Your prompt using {input} as the row value",
        "output_format": "text"
      }
    }
  ]
}
```

## Agent Types

| Type | When to use |
|---|---|
| `research_pro` | Deep web research with sources. Best for factual data points (funding, verticals, tech stack). Default choice. |
| `research` | Lighter web research. Use when speed matters more than depth. |
| `research_reasoning` | Research with chain-of-thought reasoning. Use for nuanced analysis or judgment calls. |
| `llm` | No web search — uses only the company profile + prompt. Use for classification, reformatting, or inference from existing data. |
| `linkedin` | LinkedIn-specific research. Use for people, roles, org structure. |

## Output Formats

### Simple (no extra params)

| Format | Use case | Example output |
|---|---|---|
| `text` | Free-form text, descriptions, summaries | "Cloud infrastructure, DevOps tooling" |
| `number` | Numeric values | 42 |
| `numeric` | Alias for number | 42 |
| `money` | Monetary amounts | 2500000 |
| `url` | URLs | "https://example.com" |
| `email` | Email addresses | "ceo@example.com" |
| `phone` | Phone numbers | "+1-555-0100" |
| `date` | Dates | "2024-03-15" |
| `grade` | Score/grade (1-5 scale) | 4 |
| `people` | People data | structured people info |

### With `labels` (required)

| Format | Use case | Example |
|---|---|---|
| `label` | Single tag from predefined list | "Series A" |
| `select` | Single choice from options | "SaaS" |
| `multiselect` | Multiple choices from options | ["SaaS", "Fintech"] |

Config:

```json
{
  "output_format": "select",
  "labels": ["SaaS", "Fintech", "Healthcare", "E-commerce", "Infrastructure"]
}
```

### With `output_schema` (required)

| Format | Use case | Example |
|---|---|---|
| `json` | Structured data with schema | {"aum": 2500, "currency": "USD"} |

Config:

```json
{
  "output_format": "json",
  "output_schema": {
    "type": "object",
    "properties": {
      "aum_millions": {"type": "number"},
      "source": {"type": "string"}
    }
  }
}
```

## Prompt Variables

Use `{input}` in prompts to reference the row's input value (domain). The system auto-injects `company_name` and `company_website` as dependencies.

## Trigger Enrichment Run

```
POST /v1/tables/{table_id}/run
```

**Run specific columns only (recommended):**
```json
{"mode": "new", "columns": ["column-uuid-1", "column-uuid-2"]}
```

| Param | Type | Description |
|-------|------|-------------|
| `mode` | string | `"new"` = only pending cells, `"all"` = re-run all cells |
| `columns` | string[] | Column UUIDs to scope the run to |

The `columns` param takes an array of column UUIDs. Only cells in those columns will be queued. Use this when adding a new column to avoid re-running existing enrichments. Always set `mode: "new"` to avoid re-running already completed cells.

**Run all pending cells:**
```json
{"mode": "new"}
```

Omitting `columns` runs pending cells across ALL columns. Use only when uploading new rows that need all columns enriched.

## Read Table Data

```
GET /v1/tables/{table_id}/data
```

Returns full table with all rows and cell values.

## Delete Column

```
DELETE /v1/tables/{table_id}/columns/{column_id}
```
