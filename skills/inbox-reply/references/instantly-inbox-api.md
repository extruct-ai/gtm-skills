# Instantly Inbox & Reply API Reference

Base URL: `https://api.instantly.ai/api/v2`
Auth: Bearer token via `INSTANTLY_API_KEY` environment variable.

## List Emails (Unibox)

```
GET /emails?limit=50&is_unread=true&email_type=received&sort_order=desc
```

Rate limit: **20 requests per minute** (stricter than other endpoints).

Key query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer (1-100) | Number of items to return |
| `starting_after` | UUID | Pagination cursor |
| `search` | string | Filter by email or `thread:UUID` |
| `campaign_id` | UUID | Filter by campaign |
| `is_unread` | boolean | Unread status filter |
| `email_type` | enum | `received`, `sent`, or `manual` |
| `i_status` | number | Interest status filter |
| `eaccount` | string | Filter by sender email (comma-separated) |
| `lead` | string | Filter by lead email |
| `company_domain` | string | Filter by company domain |
| `mode` | enum | `emode_focused`, `emode_others`, `emode_all` |
| `preview_only` | boolean | Return preview only |
| `sort_order` | enum | `asc` or `desc` (default: desc) |
| `assigned_to` | UUID | Filter by assigned user |
| `marked_as_done` | boolean | Done status filter |
| `min_timestamp_created` | ISO datetime | Created after |
| `max_timestamp_created` | ISO datetime | Created before |

Response:
```json
{
  "items": [
    {
      "id": "UUID",
      "timestamp_email": "ISO datetime",
      "subject": "string",
      "from_address_email": "email",
      "to_address_email_list": "string",
      "body": { "text": "string", "html": "string" },
      "campaign_id": "UUID or null",
      "lead": "email or null",
      "lead_id": "UUID or null",
      "eaccount": "string",
      "ue_type": 1 | 2 | 3 | 4,
      "is_unread": 0 | 1,
      "is_auto_reply": 0 | 1,
      "ai_interest_value": "number or null",
      "i_status": "number or null",
      "thread_id": "UUID or null",
      "content_preview": "string or null",
      "attachment_json": "object or null"
    }
  ],
  "next_starting_after": "string"
}
```

`ue_type` values: 1 = sent from campaign, 2 = received, 3 = sent manually, 4 = scheduled.

## Get Single Email

```
GET /emails/{id}
```

Returns full email object including `body.text` and `body.html`.

## Get Thread

To load a full conversation thread, use the list endpoint with thread filter:

```
GET /emails?search=thread:{thread_id}&sort_order=asc
```

## Reply to an Email

```
POST /emails/reply
```

Body:
```json
{
  "eaccount": "sender@domain.com",
  "reply_to_uuid": "email-uuid-to-reply-to",
  "subject": "Re: Original Subject",
  "body": {
    "html": "<p>Reply content here</p>",
    "text": "Reply content here"
  },
  "cc_address_email_list": "optional@cc.com",
  "bcc_address_email_list": "optional@bcc.com"
}
```

Required fields: `eaccount`, `reply_to_uuid`, `subject`, `body`.

Response: full email object of the sent reply.

## Mark Thread as Read

```
POST /emails/threads/{thread_id}/mark-as-read
```

Response: `{ "success": true }`

## Patch Email

```
PATCH /emails/{id}
```

Patchable fields (at least one required):

| Field | Type | Description |
|-------|------|-------------|
| `is_unread` | number or null | Mark read (0) or unread (1) |
| `reminder_ts` | datetime or null | Set/clear reminder |

## Count Unread Emails

```
GET /emails/unread/count
```

Response: `{ "count": 100 }`

## Update Lead Interest Status

```
POST /leads/update-interest-status
```

Body:
```json
{
  "lead_email": "lead@company.com",
  "interest_value": 1,
  "campaign_id": "optional-campaign-uuid"
}
```

Set `interest_value` to `null` to reset to default "Lead" status.

Response (202): `{ "message": "Lead interest status update background job submitted" }`

## Rate Limits

- List emails: 20 requests per minute
- All other endpoints: 10 requests per second
