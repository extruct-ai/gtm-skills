---
name: people-search
description: >
  Find LinkedIn profiles of decision makers at target companies using Extruct's
  company_people_finder. Takes a company table, adds a people finder column,
  and produces a linked child people table with names, roles, and LinkedIn URLs.
  No external API credits — uses Extruct's index only.
  Triggers on: "find linkedin", "find people", "find contacts", "find decision makers",
  "people search", "linkedin search", "who to contact", "find profiles".
---

# LinkedIn Finder

Find the right people at target companies via Extruct. Produces a people table with LinkedIn profiles — no external API credits needed.

## Related Skills

```
list-segmentation → people-search → email-search → email-generation → email-response-simulation → campaign-sending
```

After you know WHICH companies to target, this skill finds WHO to contact. The next step (`email-search`) gets their verified emails and phones.

## Extruct API Operations

This skill delegates all Extruct API calls to the `extruct-api` skill.

For all Extruct API operations, read and follow the instructions in `skills/extruct-api/SKILL.md`.

All table reads, column creation (including `company_people_finder`), enrichment runs, child table discovery, and data fetching are handled by the extruct-api skill. This skill focuses on **who** to search for and **role strategy** — the extruct-api skill handles the API execution.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Extruct table ID | Company table from `list-building` or `list-enrichment` | yes |
| Target roles | User input or context file ICP | yes |
| Max results per company | User preference (default: 5) | no |

## Workflow

### Step 1: Confirm the table

Use the extruct-api skill to fetch table metadata. Show the user: table name, kind, row count.

### Step 2: Define roles

Ask the user: "Who are we trying to reach at these companies?"

Then expand into a role list. Use **broad role descriptions**, not exact titles — Extruct's people finder matches on role semantics, not exact title strings.

**Role list guidelines:**
- 3-7 roles is the sweet spot
- Use broad terms: "VP Sales" not "Vice President of Enterprise Sales"
- Cover the decision maker + influencer + champion if possible
- Include department variations

**Role expansion examples:**

```
User says: "Sales and ops leaders"
→ Roles: ["VP Sales", "Head of Sales", "Sales Operations", "RevOps", "Business Development", "CRO"]

User says: "People who buy data tools"
→ Roles: ["Revenue Operations", "Sales Operations", "Data Operations", "Business Intelligence", "CRM Admin"]

User says: "Innovation and strategy at corporates"
→ Roles: ["Head of Innovation", "VP Strategy", "Corporate Development", "Ventures", "Technology Scouting"]
```

**Read context file** for ICP role targets if available:
```
claude-code-gtm/context/{company}_context.md → ## ICP → Roles column
```

### Step 3: Add company_people_finder column

Delegate to the extruct-api skill to add a `company_people_finder` column to the table with:
- **roles** — the expanded role list from Step 2
- **provider** — `research_pro` (always)
- **max_results** — 3-5 per company (more = slower + noisier)

### Step 4: Trigger enrichment run

Delegate to the extruct-api skill to run the new column.

### Step 5: Monitor and discover child table

The `company_people_finder` column auto-creates a **child people table**. Use the extruct-api skill to fetch the parent table metadata and discover the child people table via `child_relationships`.

### Step 6: Optionally add LinkedIn data column

For richer profile data (experience, education, skills), use the extruct-api skill to add a `linkedin` agent column to the people table. This is optional — skip if you only need name + role + LinkedIn URL for the `email-search` step.

### Step 7: Fetch and review people data

Use the extruct-api skill to fetch data from the people table.

Present summary:
- Total companies in table: N
- People found: N
- Avg people per company: N
- Companies with 0 people: N

Show a sample of 10 people for spot-checking:

| Name | Role | LinkedIn URL | Parent Company |
|------|------|-------------|----------------|
| ... | ... | ... | ... |

Ask:
- "Does the role mix look right?"
- "Any roles missing? Want to add more?"
- "Ready to proceed to `email-search` for verified emails?"

### Step 8: Export for email-search

Save the people list as CSV at `claude-code-gtm/csv/input/{campaign}/people_linkedin.csv` with columns: `full_name`, `role`, `profile_url`, `parent_row_id`.

The `email-search` skill takes this CSV (or reads the people table directly) and enriches with verified emails via contact enrichment providers (e.g. Prospeo, Fullenrich).

## Output

| Output | Format | Location |
|--------|--------|----------|
| People table | Extruct child table | Auto-created, linked to parent |
| People CSV | CSV with name, role, LinkedIn URL | `claude-code-gtm/csv/input/{campaign}/people_linkedin.csv` |

## Key Table IDs to Pass Forward

After this skill completes, pass these to `email-search`:
- **People table ID** — for direct access to people data
- **Parent table ID** — for cross-referencing company data
- **Campaign slug** — for file paths
