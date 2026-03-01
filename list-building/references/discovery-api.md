# Discovery API Reference

`POST /v1/discovery_tasks` — find companies via deep web research with AI evaluation.

## Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | yes | Natural-language description of target companies |
| `desired_num_results` | int | no | 1-10,000. Default: 100 |
| `criteria` | array | no | Evaluation criteria (see below) |
| `table` | object | no | Auto-import results to a table |
| `auto_data_sources` | bool | no | Let system pick sources. Default: true |
| `data_sources` | array | no | Manual: `web_search`, `linkedin`, `maps` |

## Criteria

Each criterion grades discovered companies 1-5.

```json
{
  "key": "has_api",
  "name": "API Available",
  "criterion": "Company offers a public API for data integration"
}
```

Rules:
- `key`: alphanumeric + underscore, starts with letter
- `name`: 1-100 chars
- `criterion`: 10-500 chars

## Table Auto-Import

```json
{
  "table": {
    "id": "uuid-of-existing-table",
    "run": true,
    "auto_import": true
  }
}
```

## Response

```json
{
  "id": "task-uuid",
  "status": "created",
  "num_results_discovered": 0,
  "num_results_enriched": 0,
  "num_results_evaluated": 0,
  "num_results": 0,
  "is_exhausted": false
}
```

Status values: `created` -> `in_progress` -> `done` | `failed`

## Polling

`GET /v1/discovery_tasks/{task_id}`

Returns same shape as creation response with updated counts.

## Fetching Results

`GET /v1/discovery_tasks/{task_id}/results?limit=200`

Each result:

```json
{
  "company_name": "Matchory",
  "company_website": "matchory.com",
  "company_description": "Global supplier discovery...",
  "relevance": 100,
  "founding_year": 2019,
  "source": "web_search",
  "scores": {
    "has_api": {
      "grade": 5,
      "explanation": "...",
      "sources": ["https://..."]
    }
  }
}
```
