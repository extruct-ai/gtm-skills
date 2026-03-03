# Instantly API Reference

Base URL: `https://api.instantly.ai/api/v2`
Auth: Bearer token via `INSTANTLY_API_KEY` environment variable.

## Campaigns

### List campaigns

```
GET /campaigns?limit=100&skip=0
```

Response:
```json
{
  "items": [
    {
      "id": "campaign-uuid",
      "name": "Campaign Name",
      "status": "active" | "paused" | "draft" | "completed"
    }
  ]
}
```

### Create campaign

```
POST /campaigns
```

Body:
```json
{
  "name": "PE Rollup - Blue Collar - 2026-03"
}
```

Response: `{ "id": "campaign-uuid", "name": "..." }`

### Get campaign

```
GET /campaigns/{campaign_id}
```

## Leads

### Upload leads

```
POST /leads
```

Body:
```json
{
  "campaign_id": "campaign-uuid",
  "skip_if_in_workspace": true,
  "leads": [
    {
      "email": "jane@example.com",
      "first_name": "Jane",
      "last_name": "Doe",
      "company_name": "Acme Corp",
      "personalization": "First paragraph text here",
      "website": "acme.com",
      "custom_variables": {
        "second_paragraph": "...",
        "third_paragraph": "...",
        "fourth_paragraph": "...",
        "hypothesis": "Database blind spot"
      }
    }
  ]
}
```

Response:
```json
{
  "uploaded": 95,
  "skipped": 5
}
```

**Dedup options:**
- `skip_if_in_workspace: true` — skip if email exists in ANY campaign
- `skip_if_in_campaign: true` — skip only if in THIS campaign
- Default (both false): always upload

**Batch size:** Max 100 leads per request.

### List leads in campaign

```
GET /leads?campaign_id={id}&limit=100&skip=0
```

### Delete lead

```
DELETE /leads/{lead_id}
```

## Campaign Analytics

### Get campaign summary

```
GET /campaigns/{campaign_id}/analytics/overview
```

Response:
```json
{
  "total_leads": 500,
  "contacted": 450,
  "emails_sent": 1200,
  "opens": 380,
  "replies": 42,
  "bounces": 15,
  "unsubscribes": 3
}
```

### Get lead status

```
GET /leads?campaign_id={id}&status=replied
```

Status values: `not_yet_contacted`, `contacted`, `replied`, `bounced`, `unsubscribed`, `interested`, `not_interested`, `meeting_booked`

## Email Accounts

### List accounts

```
GET /email-accounts?limit=100
```

### Check warmup status

```
GET /email-accounts/{account_id}
```

Look for `warmup_status` and `reputation_score` in response.

## Rate Limits

- 10 requests per second
- 100 leads per upload request
- Add 0.5s pause between consecutive uploads

## Custom Variables in Email Templates

In the Instantly email template editor, reference custom variables as:

```
{{personalization}}   → first paragraph (maps to lead.personalization)
{{second_paragraph}}  → from custom_variables
{{third_paragraph}}   → from custom_variables
{{fourth_paragraph}}  → from custom_variables
{{first_name}}        → lead first name
{{company_name}}      → lead company name
```

## Typical Email Template in Instantly

```
Hey {{first_name}},

{{personalization}}

{{second_paragraph}}

{{third_paragraph}}

{{fourth_paragraph}}
```

This maps cleanly to the P1-P4 structure from `email-generation`.
