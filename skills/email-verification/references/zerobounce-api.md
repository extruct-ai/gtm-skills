# ZeroBounce API Reference

Base URL: `https://api.zerobounce.net/v2`
Auth: API key passed as query parameter `api_key`.
Env var: `ZEROBOUNCE_API_KEY`

## Check Credits

```
GET /getcredits?api_key={key}
```

Response:
```json
{"Credits": "1461"}
```

## Validate Single Email

```
GET /validate?api_key={key}&email={email}&ip_address=
```

`ip_address` can be blank.

Response:
```json
{
  "address": "user@example.com",
  "status": "valid",
  "sub_status": "",
  "free_email": false,
  "domain": "example.com",
  "domain_age_days": "2991",
  "smtp_provider": "g-suite",
  "mx_found": "true",
  "mx_record": "aspmx.l.google.com",
  "processed_at": "2026-03-19 11:38:13.279"
}
```

## Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `valid` | Confirmed deliverable | Keep |
| `catch-all` | Domain accepts all mail, can't confirm mailbox | Keep (flag) |
| `invalid` | Mailbox doesn't exist or domain rejects | Remove |
| `do_not_mail` | Role-based, disposable, or suppressed | Remove |
| `abuse` | Known abuse/complaint address | Remove |
| `unknown` | Could not be determined (greylisted, timeout) | Remove |
| `spamtrap` | Known spam trap | Remove |

## Common Sub-Statuses

| Sub-Status | Meaning |
|-----------|---------|
| `mailbox_not_found` | Inbox doesn't exist |
| `does_not_accept_mail` | Domain rejects inbound mail |
| `role_based` | Generic address (info@, contact@, bd@) |
| `global_suppression` | On global suppression list |
| `greylisted` | Temporarily rejected, can't verify |

## Rate Limits

- Safe rate: ~10 req/s
- Use 0.15s delay between calls
- Response time: 1-5 seconds average, up to 30 seconds max
