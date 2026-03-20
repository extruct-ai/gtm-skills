---
name: competitor-monitoring
description: >
  Set up and run competitive intelligence monitoring. Discover competitors
  via user input, lookalike search, web research, or G2/review sites, then create
  an Extruct company table with research columns for blog, social media, news,
  key people, and business model tracking. Re-run columns to refresh monitoring data.
  Triggers on: "competitor monitoring", "track competitors", "competitive intelligence",
  "monitor competitors", "competitor analysis", "competitive landscape",
  "who are my competitors", "competitor tracking".
---

# Competitor Monitoring

Discover competitors, build a tracked company table in Extruct, and run recurring research columns to monitor their content, social presence, news, and product moves.

## Related Skills

```
market-research → competitor-monitoring → list-building (for targeting competitor customers)
                                        → competitor-post-engagers (for targeting their audience)
```

This skill sets up the competitive intelligence foundation. Its outputs feed into prospecting workflows (target competitor customers or engaged audiences).

## Extruct API Operations

This skill delegates all Extruct API calls to the `extruct-api` skill.

For all Extruct API operations, read and follow the instructions in `skills/extruct-api/SKILL.md`.

Table creation, row uploads, column creation, enrichment runs, and data fetching are handled by the extruct-api skill. This skill focuses on **which competitors to track** and **what monitoring columns to add**.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Client company domain | User provides | yes |
| Known competitors | User provides (optional — can be discovered) | no |
| Monitoring focus areas | User choice (default: all) | no |
| Existing monitoring table ID | Extruct table to reuse | no |

## Workflow

### Step 1: Collect competitors

Start by asking the user: "Which competitors do you want to track?" They may already have a list. Then augment with discovery methods as needed.

**Direct input (always start here)**

Ask the user for their known competitors. Most users know their top 3-5. This is the primary input — discovery methods below are supplementary.

**Augment with lookalike search**

Use the extruct-api skill to find similar companies:

```
companies similar --company-identifier {client_domain} --limit 20
```

Present results to the user — not all lookalikes are direct competitors. Let the user pick which ones to add.

**Augment with web search**

Search for competitor lists and comparison pages:
- `"{client_company} vs"` — head-to-head comparisons
- `"{client_company} alternatives"` — competitor roundups
- G2/Capterra category pages for the client's product category

**Augment with G2 / review site discovery**

If the client is listed on G2, Capterra, or TrustRadius:
- Find the client's category page
- Extract other vendors in the same category

**Combining methods:** Use direct input as the base, then run lookalike + web search to surface competitors the user may have missed. Deduplicate by domain. Present the merged list for final confirmation.

**Output:** Confirmed list of 3-10 competitor domains.

### Step 2: Create the competitor monitoring table

Delegate to the extruct-api skill to create a company table (or reuse an existing one):

```json
{
  "name": "{client_name} — Competitor Monitoring",
  "kind": "company"
}
```

Upload competitor domains as rows (batch of 50 via extruct-api skill). The table auto-generates `company_profile`, `company_name`, and `company_website` columns.

Include the client's own domain as the first row — useful for side-by-side comparison.

### Step 3: Add monitoring columns

Add research columns based on the user's monitoring focus. Present the menu below and let them choose which to enable.

#### Core columns (recommended for all setups)

| Column | Key | Agent | Format | Prompt summary |
|--------|-----|-------|--------|----------------|
| **Key People** | `key_people` | `research_pro` | `text` | List key people with roles, LinkedIn/X profiles. Search company website, Crunchbase/PitchBook, LinkedIn |
| **Business Model Analysis** | `business_model_analysis` | `research_pro` | `text` | Revenue streams, customer segments, value propositions, competitive advantages |
| **Competitors List** | `competitors_list` | `research_pro` | `text` | Who this competitor competes with (useful for discovering adjacent competitors) |
| **Funding History** | `funding_history` | `research_pro` | `text` | Funding rounds, investors, amounts, dates |

#### Content monitoring columns

| Column | Key | Agent | Format | Prompt summary |
|--------|-----|-------|--------|----------------|
| **Company Blog URL** | `company_blog_url` | `research_pro` | `url` | Find the company's blog or content hub URL |
| **Recent Blog Posts (6mo)** | `recent_blog_posts_6mo` | `research_pro` | `text` | List blog posts from the last 6 months with titles, dates, topics, and URLs |
| **People LinkedIn Updates** | `recent_company_updates` | `research_pro` | `text` | Recent LinkedIn posts and activity from key people at the company |

#### News monitoring columns

| Column | Key | Agent | Format | Prompt summary |
|--------|-----|-------|--------|----------------|
| **Recent Company News** | `recent_company_news` | `research_pro` | `text` | News articles, press releases, product announcements from the last 6 months |
| **Public News (6mo)** | `public_news_6mo` | `research_pro` | `text` | Broader public coverage — media mentions, analyst reports, event appearances |
| **News Summary** | `news_summary` | `llm` | `text` | Synthesize recent_company_news and public_news_6mo into a concise briefing. Dependencies: `recent_company_news`, `public_news_6mo` |

#### Column config examples

**Key People:**
```json
{
  "kind": "agent",
  "name": "Key People",
  "key": "key_people",
  "value": {
    "agent_type": "research_pro",
    "prompt": "List the key people in the company along with their roles. To find key people, leverage company website, crunchbase/pitchbook or other company profiles, search linkedin and broader web.\n\nFor each person, provide their LinkedIn and/or X profile links if available. Format the response as a bulleted list with names, roles, and links.",
    "output_format": "text",
    "extra_dependencies": ["company_name", "company_website"]
  }
}
```

**Recent Blog Posts:**
```json
{
  "kind": "agent",
  "name": "Recent Blog Posts 6mo",
  "key": "recent_blog_posts_6mo",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Find and list blog posts published by this company in the last 6 months. For each post include: title, publication date, main topic/theme, and URL. Focus on the company's official blog or content hub. If no blog is found, check for articles on Medium, Substack, or LinkedIn articles by the company page.",
    "output_format": "text",
    "extra_dependencies": ["company_name", "company_website", "company_blog_url"]
  }
}
```

**People LinkedIn Updates:**
```json
{
  "kind": "agent",
  "name": "People LinkedIn Updates",
  "key": "recent_company_updates",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Find recent LinkedIn posts and updates from key people at this company (founders, executives, and other visible team members). Summarize the main themes, announcements, and engagement patterns. Include links to notable posts.",
    "output_format": "text",
    "extra_dependencies": ["company_name", "company_website", "key_people"]
  }
}
```

**News Summary (LLM synthesis, depends on other columns):**
```json
{
  "kind": "agent",
  "name": "News Summary",
  "key": "news_summary",
  "value": {
    "agent_type": "llm",
    "prompt": "Synthesize the recent company news and public news into a concise executive briefing. Highlight: 1) Major product or strategy shifts, 2) Funding or M&A activity, 3) Key hires or departures, 4) Market positioning changes. Keep it to 3-5 bullet points.",
    "output_format": "text",
    "extra_dependencies": ["recent_company_news", "public_news_6mo"]
  }
}
```

### Step 4: Run enrichment

Delegate to the extruct-api skill to trigger enrichment on all newly added columns. Scope the run to only the new columns.

Monitor progress — these are `research_pro` columns, so they take longer than `llm` columns (expect 1-3 minutes per row per column).

### Step 5: Review baseline results

Once enrichment completes, fetch data and present a competitor overview:

```
Competitor Monitoring Baseline — {client_name}
================================================

| Company | Key People | Blog Posts (6mo) | Recent News | Funding |
|---------|-----------|------------------|-------------|---------|
| Competitor A | 5 found | 12 posts | 3 articles | Series B |
| Competitor B | 3 found | 0 posts | 1 article | Seed |
| ...     | ...       | ...              | ...         | ...     |

Notable Findings:
- [Competitor A] published 12 blog posts in 6mo — active content strategy
- [Competitor B] raised Series B last month — expect product expansion
- [Competitor C] has no blog — rely on social monitoring instead
```

Ask the user:
- "Does the competitor list look complete? Want to add any?"
- "Any columns returning thin results that we should drop?"
- "Ready to move to next steps (target their customers, scrape their audience)?"

### Step 6: Re-running for fresh data

Extruct does not have built-in scheduling. To refresh monitoring data, re-run enrichment on the table's columns. Each re-run overwrites the previous column values with fresh research results.

**How to re-run:** Use the extruct-api skill to trigger enrichment on specific columns:

```
tables run {table_id} --mode all --columns recent_blog_posts_6mo,recent_company_updates,recent_company_news
```

**What to re-run and when:**

| Columns | When to re-run | Why |
|---------|---------------|-----|
| `recent_blog_posts_6mo`, `recent_company_updates` | When the user wants a content update | Blog and social data goes stale fastest |
| `recent_company_news`, `public_news_6mo`, `news_summary` | When the user wants a news update | Catches new announcements, funding, launches |
| `key_people` | After hearing about exec changes | Detects new hires, departures |
| `funding_history` | After hearing about a raise | Updates funding rounds |
| `business_model_analysis`, `competitors_list` | Periodically or after market shifts | These change slowly — quarterly at most |

**Re-running all columns at once:**

```
tables run {table_id} --mode all
```

This refreshes everything but costs more research credits and takes longer. Prefer scoped re-runs for routine updates.

After each re-run, review the updated data (Step 5) and flag significant changes to the user — new blog posts, funding rounds, people moves, or messaging shifts.

## Output

| Output | Format | Location |
|--------|--------|----------|
| Competitor monitoring table | Extruct company table | `https://app.extruct.ai/tables/{table_id}` |

## Next Steps After Setup

- **Target competitor customers** → use `list-building` with competitor domains as seeds for lookalike search
- **Target competitor audience** → use `competitor-post-engagers` to scrape people engaging with competitor LinkedIn posts
- **Deep dive on a competitor** → use `market-research` for in-depth analysis of a specific competitor's market positioning
- **Enrich with custom data points** → use `list-enrichment` to add custom research columns (pricing, tech stack, etc.)
