---
name: email-generation
description: >
  Generate cold outreach emails from a contact CSV and a self-contained prompt
  template. Campaign-agnostic — no hardcoded product or voice. The prompt
  template (from email-prompt-building skill) contains all voice rules, research data,
  value prop, proof points, and personalization rules. This skill just runs it.
  Triggers on: "generate emails", "email generation", "run emails", "create
  emails", "email pipeline", "generate outreach", "write emails for campaign".
---

# Email Generation

Generate cold outreach emails from a contact CSV + prompt template. The prompt template is self-contained — it has all voice, research, value prop, proof points, and personalization rules baked in. This skill just runs it per row.

## Architectural Principle

**This skill is a runner, not a reasoner.** All strategic reasoning (voice, value angles, proof points, research data) was done by the `email-prompt-building` skill at prompt-build time and embedded in the prompt template. This skill reads the prompt + CSV and generates emails. It does NOT read the context file, hypothesis set, or research files.

```
prompt template (.md) ─┐
                       ├──▶ generate email per row ──▶ emails CSV
contact CSV ───────────┘
```

## Inputs Required

| Input | Source | Required |
|-------|--------|----------|
| Contact CSV | File with recipient data + enrichment columns | yes |
| Prompt template | `.md` file from `email-prompt-building` skill | yes |

That's it. No context file, no hypothesis set, no research files.

### Contact CSV Columns

The prompt template specifies which columns it needs. Check the prompt's "Enrichment data fields" section for the expected column names. Common columns:

**Required (always):**
- `first_name`, `last_name`, `company_name`, `job_title`

**Enrichment (campaign-specific):**
Listed in the prompt template. If the prompt references a field that's not in the CSV, the email quality degrades. Check column alignment before running.

## Name Sanitization

Before generating emails, run `scripts/sanitize-names.py` on the contact CSV:

```bash
python3 scripts/sanitize-names.py <contact.csv> [output.csv]
```

The script strips titles (`Dr`, `Prof`, etc.), removes rows with single-character names, emoji, junk values (`N/A`, `Test`, `-`), and fixes all-caps casing. It outputs a `*_sanitized.csv` and prints what was cleaned/removed.

Review the removed rows before proceeding. Do not generate emails for rows with invalid names.

## Running the Generator

**Script-first, not in-context.** Always generate via a script that calls the API per contact. Never generate emails inside the conversation — it's slow, expensive, and impossible to rerun after prompt edits.

### Step 1: Dry run

Before spending API credits, show the user a dry run:
1. Read the prompt template and contact CSV
2. For 2-3 sample contacts, display exactly what data will be passed (all enrichment fields, hypothesis match, structural variant selection)
3. Ask the user to confirm the data looks correct before proceeding
4. If enrichment fields are missing or misaligned, flag it and stop

### Step 2: Generate via script

Use the generation script template below. The script reads the prompt + CSV, calls the API per row, and writes output files.

```python
#!/usr/bin/env python3
"""
Email generation script.
Reads a prompt template + contact CSV, calls the API per row,
writes emails to CSV and MD.

Usage:
  python3 generate_emails.py \
    --prompt prompts/{vertical}/en_first_email.md \
    --contacts csv/input/{campaign}/contacts.csv \
    --output csv/output/{campaign}/emails \
    [--enrichment csv/input/{campaign}/enrichment.csv]
"""
import csv, json, os, sys, argparse
from pathlib import Path

# Add argument parsing, API client setup, and per-row generation logic here.
# The script should:
# 1. Read the prompt template as the system/user prompt
# 2. For each CSV row, format the row data as JSON and append to the prompt
# 3. Call the API and parse the JSON response
# 4. Write each result to both CSV and MD output files
# 5. Print progress (row N/total, company name, subject line)
```

Adapt this template to the user's API setup (Anthropic, OpenAI, etc.) and the specific prompt format.

### Step 3: Output both CSV and MD

Always generate two output files:
- `claude-code-gtm/csv/output/{campaign-slug}/emails.csv` — for upload to sequencer
- `claude-code-gtm/csv/output/{campaign-slug}/emails.md` — for human review (one email per section, with contact name and company as headers)

## Quality Checks

After generating, verify:
- [ ] Every email is within the word limit specified in the prompt
- [ ] No banned phrases from the prompt template appear
- [ ] Enrichment data was actually used — not just generic text
- [ ] Example queries in P2 are specific to each recipient's verticals
- [ ] Proof points vary across emails (not the same PS for everyone)
- [ ] Subject lines meet the prompt's length constraints

## Segmentation-Aware Generation

When the contact CSV includes segmentation data (from `list-segmentation`):

**Tier 1 companies:**
- Generate individually with full attention to enrichment data
- Route through `email-response-simulation` for review before sending

**Tier 2 companies:**
- Group by `hypothesis_number`
- Generate in batches within each hypothesis group
- Spot-check 2-3 from each group

**Tier 3 companies:**
- Do not generate emails
- Route back to `list-enrichment` or `list-building`

## Feedback Loop

When the user gives feedback on generated emails, the workflow is always:

1. User identifies what's wrong (tone, structure, missing data, wrong angle)
2. **Update the prompt template** — the fix must be systemic, never a one-off edit
3. **Rerun the script** with the updated prompt
4. Review the new output

Never hand-edit individual emails. If one email is bad, the prompt is bad — fix the source. Track changes made to the prompt so the user can see the evolution.

## Building a New Prompt Template

If no prompt template exists for this campaign, use the `email-prompt-building` skill to build one. That skill reads the context file and research, then synthesizes a self-contained prompt. Do not build prompts ad hoc in this skill.
