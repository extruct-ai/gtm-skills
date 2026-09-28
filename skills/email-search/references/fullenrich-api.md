# Fullenrich API Reference

Waterfall contact enrichment: tries 20+ data providers to maximize the hit rate on work emails, personal emails and mobile phones. Also reverse email lookup and a synchronous people/company search.

**Base URL:** `https://app.fullenrich.com/api/v2`
**Auth:** `Authorization: Bearer YOUR_API_KEY`
**API Key:** https://app.fullenrich.com/app/api
**Docs:** https://docs.fullenrich.com/api/v2 (index: https://docs.fullenrich.com/llms.txt)

## Credit Costs

| Data point | Credits |
|-----------|---------|
| Work email found (DELIVERABLE, HIGH_PROBABILITY or CATCH_ALL) | 1 |
| Personal email found | 3 |
| Mobile phone found | 10 |
| Reverse email lookup match | 1 |
| Search or lookup result returned | 0.25 per person/company (0 if exported before) |
| No result found | 0 (no charge) |
| Same input re-enriched within 3 months | 0 (no charge) |

Re-enrichment is free only when the input is identical (name, domain, LinkedIn URL) and the first enrichment has finished. Contacts are not deduplicated within one bulk, or when two requests for the same contact run at the same time. `custom` does not affect deduplication.

## Endpoints

### Check Credits

```
GET /account/credits
```

Response: `{ "balance": 1234 }`

### Verify API Key

```
GET /account/keys/verify
```

### Bulk Enrich Contacts (async)

```
POST /contact/enrich/bulk?silentFail=true
```

**Batch size:** up to 100 contacts per request.

**Request body:**

```json
{
  "name": "Sales Ops London",
  "data": [
    {
      "first_name": "Jane",
      "last_name": "Doe",
      "domain": "acme.com",
      "company_name": "Acme Corp",
      "linkedin_url": "https://www.linkedin.com/in/janedoe/",
      "enrich_fields": ["contact.work_emails"],
      "custom": { "row": "0" }
    }
  ]
}
```

**Required:** `name` and `data`. Each contact needs either `first_name` + `last_name` + a company (`domain` or `company_name`), or `linkedin_url`. A LinkedIn URL (standard or Sales Navigator) lifts email hit rate 5-20% and phone hit rate 10-60%, and adds a full person + company `profile` to the result.

**`enrich_fields`** (required, per contact): any of `contact.work_emails`, `contact.personal_emails`, `contact.phones`. Ask only for what you will pay for.

**`custom`:** up to 10 keys, string values only (a number is an error), 100 characters max per value. It comes back unchanged on every result record, found or not, so put your own row id here and match results by it.

**`silentFail`** (query param): when `true`, a contact with invalid or missing input is skipped and returned without contact data instead of failing the whole request. Always set it for bulk runs.

**Response:** `{ "enrichment_id": "uuid" }`

### Get Enrichment Results

```
GET /contact/enrich/bulk/{enrichment_id}
```

**Answers:**
- `200` with the job below. **Job `status`:** `CREATED` or `IN_PROGRESS` (still running), `FINISHED` (done), or `CANCELED`, `CREDITS_INSUFFICIENT`, `RATE_LIMIT`, `UNKNOWN` (ended without finishing).
- `400` `error.enrichment.in_progress` while the job is still running: wait and poll again.
- `402` with the job body, status `CREDITS_INSUFFICIENT`, when credits run out.
- `404` `error.enrichment.not_found` for an unknown or expired id.

**Polling:** the in-progress answer says to try again in 30 seconds, while the webhooks page asks pollers to wait 5-10 minutes and never poll every few seconds. Polling about once a minute stays far under the rate limit and picks up a finished bulk within a minute. Back off exponentially on 429. `?forceResults=true` returns what is done so far; contacts still running come back empty, so do not record them as misses.

**Response:**

```json
{
  "id": "uuid",
  "name": "Sales Ops London",
  "status": "FINISHED",
  "cost": { "credits": 14 },
  "data": [
    {
      "input": {
        "first_name": "Jane",
        "last_name": "Doe",
        "company_domain": "acme.com",
        "company_name": "Acme Corp",
        "professional_network_url": "https://www.linkedin.com/in/janedoe/"
      },
      "custom": { "row": "0" },
      "contact_info": {
        "most_probable_work_email": { "email": "jane.doe@acme.com", "status": "DELIVERABLE" },
        "most_probable_personal_email": { "email": "jane@gmail.com", "status": "DELIVERABLE" },
        "most_probable_phone": { "number": "+1 415-555-1234", "region": "US", "line_type": "MOBILE" },
        "work_emails": [{ "email": "jane.doe@acme.com", "status": "DELIVERABLE" }],
        "personal_emails": [{ "email": "jane@gmail.com", "status": "DELIVERABLE" }],
        "phones": [{ "number": "+1 415-555-1234", "region": "US", "line_type": "MOBILE" }]
      },
      "profile": {
        "full_name": "Jane Doe",
        "headline": "VP of Sales at Acme Corp",
        "location": { "country": "United States", "country_code": "US", "city": "San Francisco" },
        "social_profiles": { "professional_network": { "url": "https://www.linkedin.com/in/janedoe", "handle": "janedoe" } },
        "employment": {
          "current": {
            "title": "VP of Sales",
            "company": { "name": "Acme Corp", "domain": "acme.com", "headcount": 250 }
          }
        }
      }
    }
  ]
}
```

Reading a record:
- The email to use is `contact_info.most_probable_work_email`: the candidate with the lowest bounce rate, never `INVALID`. When it is absent, no usable email was found; `work_emails[]` then holds only invalid candidates. Always check its `status`: `CATCH_ALL` is billed but bounces more.
- A contact with nothing found comes back as `"contact_info": { "most_probable_phone": null }` with no email keys. A skipped contact (silentFail) comes back without contact data. Both still carry `custom`.
- `profile` (person and current company) is returned when you pass `linkedin_url`. Title and company live under `profile.employment.current`.
- `input.professional_network_url` echoes the submitted `linkedin_url`. Match results to inputs through `custom`, not by comparing LinkedIn URLs.

**Email verification statuses:**

| Status | Bounce rate | Use |
|--------|-----------|-----|
| `DELIVERABLE` | ~2% | Safe to email |
| `HIGH_PROBABILITY` | ~9% | Safe (catch-all, validated by triple verification) |
| `CATCH_ALL` | Higher | Use with caution |
| `INVALID` | Likely bounces | Do not email |
| `INVALID_DOMAIN` | Likely bounces | Do not email |

### Reverse Email Lookup (async)

```
POST /contact/reverse/email/bulk?silentFail=true
GET  /contact/reverse/email/bulk/{enrichment_id}
```

Body: `{ "name": "Inbound leads", "data": [{ "email": "jane@acme.com", "custom": { "row": "0" } }] }`. Up to 100 emails per request, work or personal; 1 credit per match. Results poll like enrichment. A matched record carries the person and company `profile`; an unmatched one has no `profile`.

### Search and Lookup (sync)

```
POST /people/search
POST /people/lookup
POST /company/search
POST /company/lookup
```

```json
{
  "current_position_titles": [{ "value": "VP of Sales" }, { "value": "Head of Sales" }],
  "current_company_headcounts": [{ "min": 50, "max": 500 }],
  "person_locations": [{ "value": "United States" }],
  "limit": 100
}
```

Text filters are lists of `{ "value", "exact_match", "exclude" }`; range filters (headcounts, founded years, years in role) are lists of `{ "min", "max", "exclude" }`. Accepted values: https://docs.fullenrich.com/api/v2/general/enums. `limit` max 100; page with `offset` up to 10,000, then with the `search_after` cursor from `metadata`. Lookup returns the one best match: a person by `person_professional_network_url` (or `person_name` plus `company_domain`), a company by `domain` or `professional_network_url`. 0.25 credits per result returned.

## Rate Limits

- **60 API calls per minute** across all endpoints (429 `error.rate.limit`, "try again in 1m")
- **100 contacts per bulk** enrichment or reverse lookup request
- A workspace works on **100 contacts at a time** for enrichment and 100 for reverse lookup; further bulks wait in the queue
- Search is synchronous (no queue)

## Processing Time

- Typically 30-90 seconds per contact
- Previously enriched contacts return from history and finish faster

## Webhooks

For a server that can receive them, instead of polling: `webhook_url` gets one POST when the whole bulk ends (same body as the GET), and `webhook_events.contact_finished` (a URL, not a list) gets one POST per contact. Each is signed with an `X-Signature-SHA1` header, the hex HMAC-SHA1 of the raw body keyed with your API key, and retried every minute up to 5 times on a non-2xx.

## Test Contact (0 credits)

```json
{
  "first_name": "Grégoire",
  "last_name": "Démogé",
  "domain": "fullenrich.com",
  "company_name": "FullEnrich",
  "linkedin_url": "https://www.linkedin.com/in/demoge/"
}
```

Use this exact data; any variation is a normal, billed enrichment.

## Data Retention

Results are stored for 3 months (GDPR). Fetching an enrichment ID older than that returns an error.
