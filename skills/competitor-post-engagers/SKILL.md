---
name: competitor-post-engagers
description: >
  Extract people who engage (comment, react, repost) on competitor LinkedIn posts,
  enrich their emails and company data, and upload to an Extruct people table for outreach.
  Supports multiple LinkedIn scraping providers (Anysite MCP, RapidAPI, Apify, Phantombuster, etc.).
  Triggers on: "competitor engagers", "competitor post", "post engagers",
  "who commented on", "who liked", "who reacted", "steal audience",
  "competitor audience", "linkedin post engagers".
---

# Competitor Post Engagers

Turn competitor LinkedIn post engagement into a prospecting list. Extract commenters, reactors, and reposters — then enrich and upload to Extruct for outreach.

## Related Skills

```
competitor-post-engagers → email-search → email-generation → campaign-sending
```

This skill produces a people table. The next step (`email-search`) gets verified emails, then `email-generation` drafts personalized outreach.

## Extruct API Operations

This skill delegates all Extruct API calls to the `extruct-api` skill.

For all Extruct API operations, read and follow the instructions in `skills/extruct-api/SKILL.md`.

Table creation, row uploads, and data fetching are handled by the extruct-api skill. This skill focuses on **scraping LinkedIn engagers** and **preparing the data** — the extruct-api skill handles the API execution.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| LinkedIn post URL(s) | User provides | yes |
| Engagement types to scrape | User choice: comments, reactions, reposts (default: all) | no |
| LinkedIn scraping provider | User choice (see provider list below) | yes |
| Existing people table ID | Extruct table to append to (or create new) | no |

## LinkedIn Scraping Providers

This skill does **not** mandate a specific provider. Ask the user which LinkedIn scraping tool they want to use. Below are known options — the user may have others.

| Provider | Engagement types | Auth | Notes |
|----------|-----------------|------|-------|
| **Anysite MCP** | Comments, reactions, reposts | MCP connection | Built into Claude Code via MCP. Tools: `get_linkedin_post_comments`, `get_linkedin_post_reactions`, `get_linkedin_post_reposts` |
| **RapidAPI (LinkedIn scrapers)** | Comments, reactions, reposts | `X-RapidAPI-Key` header | Multiple scrapers available (e.g. Fresh LinkedIn Profile Data, LinkedIn Bulk Data Scraper). Check endpoint docs per scraper |
| **Apify** | Comments, reactions, reposts | `APIFY_API_TOKEN` | Actors: `curious_coder/linkedin-post-commentors`, `supreme_coder/linkedin-post-likers`. Run via Apify API |
| **Phantombuster** | Comments, reactions | `PHANTOMBUSTER_API_KEY` | Phantoms: "LinkedIn Post Commenters", "LinkedIn Post Likers" |
| **Custom / self-hosted** | Varies | Varies | User may have their own scraping setup |

If the user doesn't know where to start:
- **Anysite MCP** is the simplest if they have it connected — no extra credentials needed
- **Apify** is a good general choice with pay-per-use pricing
- **RapidAPI** has multiple scrapers with free tiers

## Workflow

### Step 1: Collect post URLs and choose provider

1. Get the LinkedIn post URL(s) from the user. Accept one or multiple.
2. Ask which engagement types to scrape: **comments**, **reactions**, **reposts**, or all three.
3. Ask which LinkedIn scraping provider they want to use (see table above).
4. If the provider requires credentials, confirm they're available.

Extract the activity URN from each post URL. The numeric ID is typically after `activity-` or `ugcPost-` in the URL (e.g. `activity:7433261939285385217`).

### Step 2: Scrape engagers

Use the chosen provider to fetch engagement data. The approach varies by provider:

**If using Anysite MCP:**
- Comments: `mcp__claude_ai_Anysite__get_linkedin_post_comments` with `urn: "activity:{id}"`, `count: 1500`
- Reactions: `mcp__claude_ai_Anysite__get_linkedin_post_reactions` with `urn: "activity:{id}"`, `count: 1500`
- Reposts: `mcp__claude_ai_Anysite__get_linkedin_post_reposts` with `urn: "activity:{id}"`, `count: 1500`

**If using another provider:**
- Read or fetch the provider's API documentation
- Identify the endpoint, input format, and response structure
- Implement the scraping calls accordingly

For each engager, extract (field names vary by provider):
```python
{
    "full_name": "...",
    "linkedin_url": "...",        # profile URL
    "headline": "...",            # job title / headline
    "engagement_type": "...",     # comment / reaction / repost
    "post_url": "...",            # which post they engaged with
}
```

If scraping multiple posts, tag each engager with the `post_url` they engaged with.

### Step 3: Deduplicate and classify

1. **Deduplicate** by `linkedin_url` across all posts and engagement types. If someone both commented and reacted, keep both engagement types as a comma-separated value.
2. **Apply the segment classifier** to job titles (first match wins):

| Priority | Pattern | Segment |
|----------|---------|---------|
| 1 | `founder\|co-founder\|ceo\|owner` | Founders / CEOs |
| 2 | `cto\|vp.*eng\|head of eng\|director.*eng` | Engineering Leadership |
| 3 | `cmo\|vp.*market\|head of market\|director.*market` | Marketing Leadership |
| 4 | `cro\|vp.*sales\|head of sales\|director.*sales\|head of revenue` | Sales Leadership |
| 5 | `director\|vp\|vice president\|head of\|chief` | Directors / VPs / Heads |
| 6 | `revops\|revenue ops\|sales ops\|growth ops\|gtm ops\|gtm eng` | RevOps / Growth Ops |
| 7 | `product manag\|head of product\|product lead` | Product |
| 8 | `data scien\|machine learn\|ml eng\|ai eng\|data eng` | Data / ML |
| 9 | `account exec\|sdr\|bdr\|sales dev\|business dev\|sales rep` | Sales ICs |
| 10 | `market\|content\|brand\|growth\|demand gen\|copywrite` | Marketing / Content |
| 11 | `sales\|commercial\|partnerships\|revenue` | Sales (General) |
| 12 | `ai\|automat\|gpt\|llm\|agent\|no.?code` | AI / Automation Builders |
| 13 | `consult\|freelanc\|advisor\|coach\|mentor\|agenc` | Consultants / Agencies |
| 14 | `engineer\|develop\|software\|fullstack\|backend\|frontend` | Engineering / Product / Data |
| — | (no match) | Other |

3. Present a **segment breakdown** to the user before proceeding:

```
Engager Summary:
- Total unique engagers: N
- Comments: N | Reactions: N | Reposts: N

Segment Breakdown:
  Founders / CEOs:         N (X%)
  Sales Leadership:        N (X%)
  Marketing Leadership:    N (X%)
  ...
  Other:                   N (X%)
```

4. Ask the user: "Want to filter to specific segments before uploading? (e.g. only Founders + Leadership)"

### Step 4: Upload to Extruct people table

Create a new Extruct generic table or append to an existing one. Delegate to the extruct-api skill.

**If creating a new table:**

```json
{
  "name": "{user-provided name or 'Competitor Post Engagers - {date}'}",
  "kind": "generic",
  "column_configs": [
    {"kind": "input", "name": "Full Name", "key": "full_name"},
    {"kind": "input", "name": "LinkedIn URL", "key": "linkedin_url"},
    {"kind": "input", "name": "Job Title", "key": "job_title"},
    {"kind": "input", "name": "Segment", "key": "segment"},
    {"kind": "input", "name": "Engagement Type", "key": "engagement_type"},
    {"kind": "input", "name": "Source Post", "key": "source_post"},
    {"kind": "input", "name": "Company", "key": "company"},
    {"kind": "input", "name": "Domain", "key": "domain"}
  ]
}
```

Upload rows in batches of 50 via the extruct-api skill.

**If appending to an existing table:**
- Fetch existing rows to deduplicate against current `linkedin_url` values
- Upload only new engagers

### Step 5: Review and next steps

Present upload summary:

```
Upload Complete:
- Engagers uploaded: N
- Table: {table_name}
- URL: https://app.extruct.ai/tables/{table_id}

Segment Breakdown (uploaded):
  Founders / CEOs:     N
  Sales Leadership:    N
  ...
```

Suggest next steps:
- **"Get emails"** → run `email-search` on the people table to enrich with verified emails
- **"Enrich companies"** → run `list-enrichment` to add company data (industry, size, funding)
- **"Draft outreach"** → run `email-generation` after emails are found
- **"Monitor more posts"** → re-run with additional competitor post URLs and deduplicate against this table

## Tips

- **Multiple posts = richer list.** Scrape 3-5 recent posts from the same competitor to build a larger pool. Engagers across multiple posts are highly engaged — flag them.
- **Repeat engagers are warmer leads.** If someone engaged on 2+ posts, note that in the data — they're more likely to respond to outreach.
- **Filter aggressively.** Not all engagers are prospects. Use segment filtering to focus on decision makers and skip students, recruiters, etc.
- **Respect rate limits.** LinkedIn scraping providers have varying rate limits. Don't hammer the API — space out requests if scraping many posts.

## Output

| Output | Format | Location |
|--------|--------|----------|
| People table | Extruct generic table | `https://app.extruct.ai/tables/{table_id}` |
| Engagers CSV | CSV backup | `claude-code-gtm/csv/input/{campaign}/competitor_engagers.csv` |
