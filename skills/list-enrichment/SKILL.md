---
name: list-enrichment
description: >
  Add research-powered enrichment columns to Extruct company tables.
  Use when the user wants to add enrichment columns (e.g. funding, verticals,
  tech stack) to an existing Extruct table, run column configs from
  enrichment-design, or monitor enrichment progress. Triggers on: "enrich",
  "add column", "add data point", "research column", "enrich table",
  "enrichment", "add a field", "run enrichment", "monitor enrichment".
---

# Table Enrichment

Add research-powered enrichment columns to Extruct company tables.

## Extruct API Operations

This skill delegates all Extruct API calls to the `extruct-api` skill.

**Resolution order:**
1. If the `extruct-api` skill is installed (via `/plugin install extruct-skills`), use it directly for all Extruct operations
2. Otherwise, read the skill instructions from GitHub and follow them: https://github.com/extruct-ai/skills/blob/main/skills/extruct-api/SKILL.md

All table reads, column creation, enrichment runs, polling, and data fetching are handled by the extruct-api skill. This skill focuses on **what** to enrich and **how to design columns** — the extruct-api skill handles the API execution.

## Workflow

### 1. Confirm the table

Get the table ID from the user (URL or ID). Use the extruct-api skill to fetch table metadata. Show the user: table name, row count, existing columns.

### 2. Get column configs

Two paths:

**Path A: From enrichment-design** — User has `column_configs` ready. Confirm and proceed.

**Path B: Design on the fly** — Confirm with the user:

1. **What data point?** — what to research (e.g. "funding stage", "primary vertical", "tech stack")
2. **Output format** — pick the right format:

| Format | When to use | Extra params |
|---|---|---|
| `text` | Free-form research output | — |
| `number` / `money` | Numeric data (revenue, headcount) | — |
| `select` | Single choice from known categories | `labels: [...]` |
| `multiselect` | Multiple tags from known categories | `labels: [...]` |
| `json` | Structured multi-field data | `output_schema: {...}` |
| `grade` | 1-5 score | — |
| `label` | Single tag from list | `labels: [...]` |
| `date` | Date values | — |
| `url` / `email` / `phone` | Contact info | — |

3. **Agent type** — default `research_pro`. Use `llm` when no web research needed (classification from existing profile data).

### 3. Write the prompt

Craft a clear prompt using `{input}` for the row's domain value. Prompt guidelines:

- Be specific about what to find
- Specify the exact output format in the prompt (e.g. "Return ONLY a number in millions USD")
- Include fallback instruction (e.g. "If not found, return N/A")
- For `select`/`multiselect`, the labels constrain the output — the prompt should guide which label to pick

### 4. Create the column(s)

Delegate column creation to the extruct-api skill with the `column_configs` array.

### 5. Trigger enrichment (only the new columns)

Delegate the enrichment run to the extruct-api skill. Always scope the run to the newly created column(s) only. Avoid broad or implicit run payloads when you only intend to enrich specific columns.

### 6. Monitor progress

Delegate progress monitoring to the extruct-api skill. Use it to poll table data and check cell statuses.

Show the user:
- Current % complete (done cells / total cells)
- Number of failed cells (if any)
- Estimated time remaining (based on rate so far)

Stop polling when all cells are done or failed.

### 7. Quality spot-check

After enrichment completes (or after 50%+ is done), fetch a sample of 5-10 enriched rows and display for review.

**Present to user as a table.** Ask:
- "Does the data quality look right?"
- "Any columns returning garbage or N/A too often?"
- "Should we adjust any prompts and re-run?"

If quality issues are found:
1. Delete the problematic column
2. Adjust the prompt
3. Re-create and re-run
