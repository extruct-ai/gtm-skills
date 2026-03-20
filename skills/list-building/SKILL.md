---
name: list-building
description: >
  Build targeted company lists for outbound campaigns using Extruct.
  Use when the user wants
  to: (1) find companies matching an ICP, (2) build a prospect or outbound
  list, (3) search for companies by description, (4) discover companies in a
  market segment, (5) create a target account list, (6) research a competitive
  landscape, (7) find lookalike companies from a seed list. Triggers on: "find
  companies", "build a list", "company search", "prospect list", "target
  accounts", "outbound list", "discover companies", "ICP search", "lookalike
  search", "seed company".
---

# List Building

Build company lists using Extruct, guided by a decision tree. Reads from the company context file for ICP and seed companies.

## Extruct API Operations

This skill delegates all Extruct API calls to the `extruct-api` skill.

For all Extruct API operations, read and follow the instructions in `skills/extruct-api/SKILL.md`.

All company search, lookalike search, deep search, table creation, row uploads, and enrichment runs are handled by the extruct-api skill. This skill focuses on **what** to search for and **why** — the extruct-api skill handles the **how**.

## Decision Tree

Before running any queries, determine the right approach:

```
Have a seed company from win cases or context file?
  YES → Lookalike Search (pass seed domain)
  NO  ↓

New vertical, need broad exploration?
  YES → Semantic Search (3-5 queries from different angles)
  NO  ↓

Need qualification against specific criteria?
  YES → Deep Search (criteria-scored async research)
  NO  ↓

Need maximum coverage?
  YES → Combine Search + Deep Search (~15% overlap expected)
```

## Before You Start

Read the company context file if it exists:

```
claude-code-gtm/context/{company}_context.md
```

Extract:
- **ICP profiles** — for query design and filters
- **Win cases** — for seed companies in lookalike mode
- **DNC list** — domains to exclude from results. If no DNC list exists in the context file, ask the user: (1) run an Extruct search for competitors to auto-populate, (2) accept a CSV of existing customers/partners, or (3) skip for now

Also check for a hypothesis set at `claude-code-gtm/context/{vertical-slug}/hypothesis_set.md`. If it exists, use the **Search angle** field from each hypothesis to design search queries — these are pre-defined query suggestions tailored to each pain point.

## Method 1: Lookalike Search

Use when you have a seed company (from win cases, existing customers, or user input). Delegate to the extruct-api skill to run a lookalike search with the seed domain.

**When to use:**
- You have a happy customer and want more like them
- Context file has win cases with domains
- User says "find companies similar to X"

**Tips:**
- Run multiple lookalike searches with different seed companies for broader coverage
- Combine with filters to constrain geography or size
- Deduplicate across runs by domain

## Method 2: Semantic Search — Fast, Broad

Delegate to the extruct-api skill to run semantic company search queries.

**Query strategy:**
- Write 3-5 queries per campaign, each from a different angle on the same ICP
- Describe the product/use case, not the company type
- Deduplicate across queries by domain — overlap is expected
- Target 200-800 companies total across all queries

## Method 3: Deep Search — Deep, Qualified

Delegate to the extruct-api skill to create and run deep search tasks.

**Query strategy:**
- Write queries like a job description — 2-3 sentences describing the ideal company
- Use criteria to auto-qualify — each company gets graded 1-5 per criterion
- Default 50 results for first pass; expand after quality review
- Use up to 5 criteria per task; keep criteria focused and non-overlapping
- Run separate tasks for different ICP segments

## Upload to Table

After collecting results, delegate to the extruct-api skill to create a company table and upload domains. Extruct auto-enriches each domain with a Company Profile.

## Re-run After Enrichment

After the `list-enrichment` skill adds data points to this list, consider re-running list building using enrichment insights as Deep Search criteria. For example:

- If enrichment reveals that "companies using legacy ERP" are the best fit, create a Deep Search task with that as a criterion
- If enrichment shows a geographic cluster, run a Search with tighter geo filters
- This creates a feedback loop: list → enrich → learn → refine list

## Result Size Guidance

| Campaign stage | Target list size | Method |
|---------------|-----------------|--------|
| Exploration | 50-100 | Search (2-3 queries) |
| First campaign | 200-500 | Search (5 queries) + Deep Search |
| Scaling | 500-2000 | Deep Search (high result count) + multiple Search |

## Workflow

1. Read context file for ICP, seed companies, and DNC list
2. Follow the decision tree to pick the right method
3. Draft queries (3-5 for Search, 1-2 for Deep Search)
4. Delegate to the extruct-api skill to run queries and collect results
5. Deduplicate across all results by domain
6. Remove DNC domains
7. Delegate to the extruct-api skill to upload to a company table
8. Add agent columns if user needs custom research
9. Ask user for preferred output: Extruct table link, local CSV, or both
