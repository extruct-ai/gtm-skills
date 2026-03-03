# Prospeo API Reference

Person and company enrichment with 200M+ contact database and 30+ search filters.

**Base URL:** `https://api.prospeo.io`
**Auth header:** `X-KEY: your_api_key`
**Content-Type:** `application/json`
**Method:** All endpoints use POST
**API Key:** https://app.prospeo.io/api

## Credit Costs

| Endpoint | Credits |
|----------|---------|
| Enrich Person (email only) | 1 per match |
| Enrich Person (with mobile) | 10 per match |
| Bulk Enrich Person | Same as single, per matched record |
| Search Person | 1 per page (up to 25 results) |
| No match found | 0 (no charge) |
| Duplicate enrichment | 0 (no charge, lifetime dedup) |

## Rate Limits

Tier-based. Check response headers:
- `x-daily-request-left` — remaining daily requests
- `x-minute-request-left` — remaining per-minute requests
- `x-second-rate-limit` — per-second limit
- `x-daily-reset-seconds` — seconds until daily reset
- `x-minute-reset-seconds` — seconds until minute reset

Returns `429` when exceeded.

## Endpoints

### Search Person

```
POST /search-person
```

Search 200M+ contacts with 30+ filters. Returns person + company data but **no email/mobile** — use Enrich Person for that.

**Request:**

```json
{
  "filters": {
    "job_title": {
      "v": ["VP of Sales", "Head of Sales"],
      "condition": "or"
    },
    "seniority": {
      "v": ["VP", "Director", "C-Suite"],
      "condition": "or"
    },
    "department": {
      "v": ["Sales"],
      "condition": "or"
    },
    "person_location": {
      "v": ["United States"],
      "condition": "or"
    },
    "industry": {
      "v": ["Software", "Information Technology"],
      "condition": "or"
    },
    "employee_range": {
      "v": ["51-200", "201-500"],
      "condition": "or"
    },
    "company_website": {
      "v": ["acme.com", "example.com"],
      "condition": "or"
    }
  },
  "page": 1
}
```

**Available filters:**

| Filter | Type | Notes |
|--------|------|-------|
| `job_title` | string[] | Free text, use Search Suggestions for exact values |
| `seniority` | enum[] | C-Suite, VP, Director, Manager, Senior, Entry, Training, Intern |
| `department` | enum[] | Sales, Marketing, Engineering, Finance, HR, Operations, etc. |
| `person_location` | string[] | Country, state, or city names |
| `industry` | enum[] | 150+ industries |
| `employee_range` | enum[] | 1-10, 11-20, 21-50, 51-100, 101-200, 201-500, 501-1000, 1001-5000, 5001-10000, 10001+ |
| `company_website` | string[] | Up to 500 domains per request |
| `company_name` | string[] | Company names |
| `company_location` | string[] | Country, state, or city |
| `funding_stage` | enum[] | Seed, Series A, Series B, Series C, etc. |
| `technologies` | enum[] | Salesforce, HubSpot, etc. |
| `mx_provider` | enum[] | Gmail, Outlook, etc. |
| `years_of_experience` | range | Min/max years |

All filters use `"condition": "or"` (match any) or `"condition": "and"` (match all) within the same filter field.

**Response:**

```json
{
  "error": false,
  "results": [
    {
      "person": {
        "id": "person-uuid",
        "first_name": "Jane",
        "last_name": "Doe",
        "full_name": "Jane Doe",
        "linkedin_url": "https://linkedin.com/in/janedoe",
        "title": "VP of Sales",
        "seniority": "VP",
        "department": "Sales",
        "location": "San Francisco, CA, US",
        "skills": ["B2B Sales", "SaaS", "Revenue Operations"]
      },
      "company": {
        "name": "Acme Corp",
        "website": "acme.com",
        "linkedin_url": "https://linkedin.com/company/acme",
        "industry": "Software",
        "headcount": 250,
        "founded_year": 2018,
        "location": "San Francisco, CA, US"
      }
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 25,
    "total_page": 40,
    "total_count": 1000
  }
}
```

**Pagination:** 25 results per page, max 1000 pages (25,000 results).

### Enrich Person

```
POST /enrich-person
```

Get verified email and optional mobile for a specific person.

**Request:**

```json
{
  "data": {
    "first_name": "Jane",
    "last_name": "Doe",
    "company_website": "acme.com"
  },
  "only_verified_email": true,
  "enrich_mobile": true,
  "only_verified_mobile": false
}
```

**Required fields (at least one combo):**
- `first_name` + `last_name` + (`company_website` | `company_name` | `company_linkedin_url`)
- `full_name` + company info
- `linkedin_url` alone
- `email` alone
- `person_id` (from Search Person results)

**Optional params:**
- `only_verified_email` (bool) — only return if email is verified
- `enrich_mobile` (bool) — include mobile lookup (costs 10 credits instead of 1)
- `only_verified_mobile` (bool) — only return if mobile is verified

**Response:**

```json
{
  "error": false,
  "free_enrichment": false,
  "person": {
    "first_name": "Jane",
    "last_name": "Doe",
    "full_name": "Jane Doe",
    "linkedin_url": "https://linkedin.com/in/janedoe",
    "title": "VP of Sales",
    "email": "jane.doe@acme.com",
    "email_verified": true,
    "mobile": "+14155551234",
    "mobile_verified": true,
    "location": "San Francisco, CA, US",
    "skills": ["B2B Sales", "SaaS"]
  },
  "company": {
    "name": "Acme Corp",
    "website": "acme.com",
    "industry": "Software",
    "headcount": 250
  }
}
```

**Error codes:** `NO_MATCH`, `INVALID_DATAPOINTS`, `INSUFFICIENT_CREDITS`, `INVALID_API_KEY`, `RATE_LIMITED`

### Bulk Enrich Person

```
POST /bulk-enrich-person
```

Enrich up to 50 records at once. Same matching rules as single enrich.

**Request:**

```json
{
  "only_verified_email": true,
  "enrich_mobile": false,
  "only_verified_mobile": false,
  "data": [
    {
      "first_name": "Jane",
      "last_name": "Doe",
      "company_website": "acme.com"
    },
    {
      "linkedin_url": "https://linkedin.com/in/johndoe"
    }
  ]
}
```

**Batch size:** Max 50 records per request.

**Response:**

```json
{
  "error": false,
  "total_cost": 5,
  "matched": [
    {
      "person": { ... },
      "company": { ... }
    }
  ],
  "not_matched": [
    { "first_name": "Unknown", "last_name": "Person", "company_website": "none.com" }
  ],
  "invalid_datapoints": []
}
```

### Search Suggestions

```
POST /search-suggestions
```

Get exact filter values for job titles, locations, etc. Use before Search Person to get precise values.

### Enrich Company

```
POST /enrich-company
```

Get verified company data including funding and technology details.

### Search Company

```
POST /search-company
```

Search 30M+ company records.

## Removed Endpoints (removed March 1, 2026)

These endpoints have been removed. Use the replacements listed:

- ~~Email Finder~~ → use Enrich Person
- ~~Mobile Finder~~ → use Enrich Person with `enrich_mobile: true`
- ~~Email Verifier~~ → use Enrich Person with `only_verified_email: true`
- ~~Domain Search~~ → use Search Person with `company_website` filter
- ~~Social URL Enrichment~~ → use Enrich Person with `linkedin_url`
