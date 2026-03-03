# Fullenrich API Reference

Waterfall contact enrichment — tries multiple data providers to maximize hit rate on emails and phones.

**Base URL:** `https://api.fullenrich.com/api/v1`
**Auth:** `Authorization: Bearer YOUR_API_KEY`
**API Key:** https://app.fullenrich.com/app/api

## Credit Costs

| Data point | Credits |
|-----------|---------|
| Work email found | 1 |
| Personal email found | 3 |
| Mobile phone found | 10 |
| Search result returned | 0.25 per contact/company |
| No result found | 0 (no charge) |
| Duplicate (enriched within 3 months) | 0 (no charge) |

## Endpoints

### Check Credits

```
GET /account/credits
```

Response: `{ "credits": 1234 }`

### Verify API Key

```
GET /account/keys/verify
```

### Bulk Enrich Contacts (async)

```
POST /contact/enrich/bulk
```

**Batch size:** Up to 100 contacts per request.

**Request body:**

```json
{
  "contacts": [
    {
      "first_name": "Jane",
      "last_name": "Doe",
      "domain": "acme.com",
      "linkedin_url": "https://www.linkedin.com/in/janedoe/"
    }
  ],
  "webhook_url": "https://your-server.com/webhook",
  "webhook_events": ["contact_finished"]
}
```

**Required fields (at least one combo):**
- `first_name` + `last_name` + `domain` (or `company_name`)
- `linkedin_url` (improves accuracy 5-20% for emails, 10-60% for phones)

**Optional fields:**
- `company_name` — company name (use `domain` when possible for better accuracy)
- `webhook_url` — URL for async result delivery (recommended over polling)
- `webhook_events` — `["contact_finished"]` for per-contact notifications
- `silentFail` — query param, `true` to skip invalid contacts quietly

**Response:**

```json
{
  "enrichment_id": "uuid",
  "status": "processing",
  "total_contacts": 5
}
```

### Get Enrichment Results

```
GET /contact/enrich/bulk/{enrichment_id}
```

**Response:**

```json
{
  "enrichment_id": "uuid",
  "status": "completed",
  "results": [
    {
      "input": { "first_name": "Jane", "last_name": "Doe", "domain": "acme.com" },
      "work_email": {
        "email": "jane.doe@acme.com",
        "verification_status": "DELIVERABLE"
      },
      "personal_email": {
        "email": "jane@gmail.com",
        "verification_status": "DELIVERABLE"
      },
      "mobile_phone": {
        "number": "+14155551234",
        "region": "US"
      },
      "profile": {
        "full_name": "Jane Doe",
        "title": "VP of Sales",
        "location": "San Francisco, CA",
        "linkedin_url": "https://linkedin.com/in/janedoe",
        "employment_history": [...],
        "education": [...]
      },
      "company": {
        "name": "Acme Corp",
        "domain": "acme.com",
        "industry": "Software",
        "employee_count": 250
      }
    }
  ]
}
```

**Email verification statuses:**

| Status | Bounce rate | Use |
|--------|-----------|-----|
| `DELIVERABLE` | ~2% | Safe to email |
| `HIGH_PROBABILITY` | ~9% | Safe (catch-all validated) |
| `CATCH_ALL` | Higher | Use with caution |
| `INVALID` | Likely bounces | Do not email |

### Reverse Email Lookup (async)

```
POST /contact/reverse/email/bulk
```

```json
{
  "emails": ["jane@acme.com", "john@example.com"],
  "webhook_url": "https://your-server.com/webhook"
}
```

Cost: 1 credit per match. Works with work and personal emails.

```
GET /contact/reverse/email/bulk/{enrichment_id}
```

### People Search (sync)

```
POST /people/search
```

```json
{
  "filters": {
    "job_title": ["VP of Sales", "Head of Sales"],
    "seniority": ["VP", "Director"],
    "location": ["United States"],
    "company_size": ["51-200", "201-500"],
    "industry": ["Software"]
  },
  "page": 1
}
```

Cost: 0.25 credits per result returned. Synchronous response.

### Company Search (sync)

```
POST /company/search
```

Similar filter structure to people search but with company-level filters.

## Rate Limits

- **60 API calls per minute** (default, can be increased on request)
- **100 contacts per bulk enrichment request**
- **100 concurrent enrichments** in queue
- **100 concurrent reverse lookups** in queue
- Search API is synchronous (no queue)
- Effective throughput: ~6,000 contacts/minute

## Processing Time

- Average: 30-90 seconds per contact
- Varies by data availability and waterfall depth
- Use webhooks (recommended) instead of polling for results

## Webhook Integration (recommended)

Set `webhook_url` in bulk requests. Fullenrich will POST results as they complete:
- Per-contact: `webhook_events: ["contact_finished"]`
- Retries: up to 5 times on delivery failure
- Verify delivery using a test endpoint

## Test Contact (0 credits)

```json
{
  "first_name": "Grégoire",
  "last_name": "Démogé",
  "domain": "fullenrich.com",
  "linkedin_url": "https://www.linkedin.com/in/demoge/"
}
```

## Data Retention

Results retained for 3 months (GDPR). Re-enrichment within window costs 0 credits.
