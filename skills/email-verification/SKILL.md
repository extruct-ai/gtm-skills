---
name: email-verification
description: >
  Validate email addresses before campaign sending. Takes a contact CSV,
  validates each email via a verification provider, removes
  invalid/do_not_mail/abuse/unknown addresses, and optionally cleans them
  from sequencer campaigns. Outputs a verified CSV ready for
  campaign-sending. Fits between email-generation and campaign-sending in
  the pipeline. Triggers on: "verify emails", "validate emails", "email
  verification", "clean emails", "check emails before sending", "remove
  bad emails", "email hygiene".
---

# Email Verification

Validate emails before sending. Sits between `email-generation` and `campaign-sending`:

```
email-generation → email-verification → campaign-sending
```

## Environment

Provider selection and credentials are handled in Step 0 of the workflow.

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| Contact CSV with email column | yes | From `email-generation` output or any CSV |
| Sequencer campaign IDs | no | From `campaign-sending` — only if cleaning uploaded leads |

## Workflow

### Step 0: Confirm provider and learn API

1. Ask the user which email verification provider they want to use. If they're unsure, pre-configured options with local reference docs are available in [references/](references/).
2. Fetch or read the provider's API documentation and identify:
   - Credit check endpoint
   - Single email validation endpoint
   - Required input fields and authentication method
   - Rate limits and request constraints
   - Response format (status, sub_status)
   - Status values and which to keep vs remove
3. Ask for their API credentials and confirm access

### Step 1: Check API access and credits

1. Call the provider's credit check endpoint
2. Count unique emails in the input CSV
3. If credits < unique emails, warn the user and ask whether to proceed with partial validation or stop

### Step 2: Extract and deduplicate emails

1. Read the input CSV, auto-detect the email column (common names: `email`, `Email`, `email_address`)
2. Build a set of unique email addresses
3. Skip rows with empty/missing email
4. Report: `{N} unique emails to validate, {M} rows without email skipped`

### Step 3: Validate emails

For each unique email, call the provider's validation endpoint:

- Respect the provider's rate limits (from Step 0)
- Print progress every 50 emails
- Store results as `{email: {status, sub_status}}`
- On error (timeout, JSON parse failure), mark as `unknown`

### Step 4: Categorize and report

Group results by the provider's status values. Use the status mapping identified in Step 0 to determine which emails to keep and which to remove.

General guidance (confirm against provider docs):

| Action | Typical statuses |
|--------|-----------------|
| Keep | `valid`, `catch-all` (flag in report) |
| Remove | `invalid`, `do_not_mail`, `abuse`, `unknown`, `spamtrap` |

Present summary table with counts per status, then list all emails to remove with their status and sub_status.

### Step 5: Output cleaned CSV

1. Filter the original CSV: keep only rows where email status maps to "keep"
2. Write cleaned CSV to same directory as input, named `{original_name}_verified.csv`
3. Save full validation results to `{original_name}_verification_results.json` for reference
4. Report: `{kept} emails kept, {removed} removed, {catch_all} catch-all (flagged)`

### Step 6: Clean from sequencer (optional)

If the user provides sequencer campaign IDs:

1. Ask which sequencer they use (Instantly, etc.) and read its API docs from `skills/campaign-sending/references/`
2. For each removed email, call the sequencer's lead deletion endpoint
3. Respect rate limits
4. Report: `{N} leads removed from sequencer`

If no campaigns are provided, skip this step and note that the user should remove bad emails manually or re-upload with the cleaned CSV.

## Output

| File | Contents |
|------|----------|
| `*_verified.csv` | Cleaned CSV with only valid emails |
| `*_verification_results.json` | Full validation results for all emails |
| Console report | Summary table + list of removed emails |

## API References

Pre-configured provider docs in [references/](references/) directory. For other providers, docs are fetched during Step 0.
