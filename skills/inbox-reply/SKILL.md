---
name: inbox-reply
description: >
  Manage and reply to lead responses in Instantly unibox. Fetches unread
  conversations, classifies reply intent, drafts contextual responses, and
  sends replies via Instantly API. Fits after campaign-sending in the GTM
  pipeline. Triggers on: "reply to leads", "inbox replies", "instantly
  inbox", "unibox", "respond to replies", "manage replies", "instantly
  replies", "check inbox", "lead replies", "answer leads".
---

# Inbox Reply

Manage and reply to lead responses in the email sequencing inbox.

## Environment

| Variable | Service |
|----------|---------|
| `INSTANTLY_API_KEY` | Instantly |

Base URL: `https://api.instantly.ai/api/v2`

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| Instantly API key | yes | env var |
| Context file | yes | context file (voice, product, proof points) |
| Campaign ID | no | user selection or list from API |

## Workflow

### Step 1: Fetch unread replies

Fetch unread received emails from the unibox.

**List unread:** `GET /emails` with `is_unread=true`, `email_type=received`, `sort_order=desc`, `limit=50`.

If the user specifies a campaign, add `campaign_id` filter. If they want focused inbox only, add `mode=emode_focused`.

Present a summary table:

```
| # | From | Company | Subject | Preview | Received |
```

Ask the user which conversations to work on, or process all.

### Step 2: Load full threads

For each selected reply, load the full conversation thread.

**Get thread:** `GET /emails?search=thread:{thread_id}&sort_order=asc`

This returns the original outbound email(s) and all replies in chronological order, giving full context for drafting a response.

### Step 3: Classify reply intent

Read each lead reply and classify into one of these categories:

```
Interested        → wants to learn more, asks questions, requests a call
Objection         → raises concern but door is not closed (pricing, timing, fit)
Not interested    → clear rejection, asks to stop
Auto-reply        → OOO, bounce, auto-responder
Meeting request   → explicitly asks to book time
Question          → asks a specific question without clear buying signal
Referral          → redirects to someone else at the company
```

Present classifications to the user for confirmation before drafting.

### Step 4: Draft replies

Read the context file for voice rules, product description, proof points, and use case framings. Draft a reply for each conversation based on intent:

```
Interested       → confirm interest, propose next step (call or resource)
Objection        → address concern directly, offer proof point if relevant
Question         → answer the question, bridge to value
Meeting request  → confirm availability, suggest booking link or times
Referral         → thank them, ask for intro or reach out to referral directly
Not interested   → short, respectful close; do not push
Auto-reply       → skip, no reply needed
```

Rules for all replies:
- Match the lead's tone and length — short replies get short responses
- Reference specifics from their message to show it is not a template
- Reference the original outbound context when relevant
- Never start with "I" as the first word
- No generic openers ("Thanks for getting back to me", "Great to hear from you")
- One clear call to action per reply, never two
- No attachments unless the user explicitly provides one
- Plain text unless the original thread was HTML-formatted

Present each draft alongside the original thread for the user to review and edit.

### Step 5: Confirm and send

Before sending, present a final checklist for each reply:

```
| # | To | Via Account | Subject | Intent | Action |
```

The user must confirm before any reply is sent.

**Send reply:** `POST /emails/reply` with:
- `eaccount`: the same email account that sent the original outbound
- `reply_to_uuid`: the ID of the lead's most recent message
- `subject`: keep the existing thread subject (Re: ...)
- `body`: the approved reply in `{ "text": "...", "html": "..." }`

Send one at a time. Report success or failure for each.

### Step 6: Post-reply housekeeping

After sending:

1. **Mark thread as read:** `POST /emails/threads/{thread_id}/mark-as-read`
2. **Update lead interest status** if the classification warrants it: `POST /leads/update-interest-status` with `lead_email` and appropriate `interest_value`
3. Report final summary:

```
| # | Lead | Intent | Reply Sent | Status Updated |
```

### Step 7: Skip and defer handling

For replies the user wants to skip or defer:

- **Skip (not interested / auto-reply):** mark as read, optionally update interest status
- **Defer:** leave unread, note for next session

Never send a reply the user has not explicitly approved.

## Reference

See [references/instantly-inbox-api.md](references/instantly-inbox-api.md) for full Instantly Unibox and Reply API documentation.
