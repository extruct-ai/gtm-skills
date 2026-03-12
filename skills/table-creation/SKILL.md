---
name: table-creation
description: >
  Create an Extruct company table from user-provided data, upload rows, and
  optionally add enrichment columns. Handles the full flow: parse input (CSV,
  pasted list, or structured data), create or reuse a table, upload domains in
  batches, add agent columns, and trigger enrichment. Triggers on: "create table",
  "upload companies", "add to extruct", "new extruct table", "import companies",
  "upload list to extruct".
---

# Create Table

End-to-end workflow: parse company data → create/reuse Extruct table → upload rows → add columns → run enrichment.

## Extruct API Operations

This skill delegates all Extruct API calls to the `extruct-api` skill.

**Resolution order:**
1. If the `extruct-api` skill is installed (via `/plugin install extruct-skills`), use it directly for all Extruct operations
2. Otherwise, read the skill instructions from GitHub and follow them: https://github.com/extruct-ai/skills/blob/main/skills/extruct-api/SKILL.md

All table creation, row uploads, column creation, and enrichment runs are handled by the extruct-api skill. This skill focuses on **parsing input data** and **orchestrating the flow** — the extruct-api skill handles the API execution.

## Workflow

### 1. Parse input data

Accept data in any of these formats:

**Pasted list** (most common): User pastes company names, URLs, and metadata as freeform text. Parse into structured records. Extract domains by stripping protocol, `www.`, and trailing slashes.

**CSV file**: Read CSV, map columns to find the URL/domain column.

**Extruct table URL**: Use the extruct-api skill to fetch data from existing table.

Key rules:
- Skip entries with no URL (e.g., "Stealth" companies)
- Deduplicate by domain
- Ask which metadata fields to preserve (country, stage, industry, etc.)

### 2. Decide: create new table or add to existing

Ask the user:
- **New table**: Delegate to the extruct-api skill to create a company table
- **Existing table**: User provides table ID or URL (`https://app.extruct.ai/tables/{id}`)

### 3. Upload rows

Delegate row upload to the extruct-api skill with the parsed domains.

Report progress to the user.

### 4. Add agent columns (optional)

If the user wants enrichment columns (industry, funding, etc.), delegate column creation to the extruct-api skill.

**Column types by use case:**

| User says | Agent type | Output format | Notes |
|-----------|------------|---------------|-------|
| "add industry" | `llm` | `select` with labels | Classification from profile, no web research needed |
| "add funding" | `research_pro` | `text` | Needs web research |
| "classify by vertical" | `llm` | `select` with labels | Classification |
| "find their tech stack" | `research_pro` | `text` | Needs web research |
| "score fit 1-5" | `llm` or `research_reasoning` | `grade` | Assessment |
| "tag multiple categories" | `llm` | `multiselect` with labels | Multiple tags |

See the [list-enrichment skill](../list-enrichment/SKILL.md) for full column types and output formats.

### 5. Trigger enrichment

Delegate the enrichment run to the extruct-api skill, scoped to only the newly added agent columns.

If no agent columns were added, skip this step.

### 6. Report to user

Provide:
- Table URL: `https://app.extruct.ai/tables/{table_id}`
- Row count uploaded
- Columns added
- Cells queued for enrichment
- Any rows skipped (stealth, duplicates, invalid URLs)

## Input Parsing Patterns

### Freeform pasted list (5-line groups)

```
Company Name
URL (or "Stealth")
Country
Industry
Funding Stage
```

Parse by splitting into 5-line chunks. Filter where URL == "Stealth".

### CSV

Map columns: look for "website", "url", "domain", "Company Website". Extract domain from whichever column contains URLs.

### Single-column domain list

```
example.com
startup.io
company.ai
```

Direct upload — each line is a domain.

## Common Pitfalls

- **Domain format**: Strip protocol and trailing slash. `https://www.example.com/` → `example.com`
- **Stealth companies**: Skip — no domain to enrich
- **Duplicates**: Deduplicate by domain before upload
- **Column labels**: For `select`/`multiselect`, collect unique values from user data to build the label list
