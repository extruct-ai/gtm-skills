# Enrichment provider playbook

Per-provider operational notes for the ENRICH step of account research. Cheaper, broader first; expensive, narrower last. Never trust one provider.

## Order of preference (default)

1. **Apollo** for the broad roster pull (`apollo_mixed_people_api_search`)
2. **Apollo** for organization enrichment and tech detection (`apollo_organizations_enrich`)
3. **PredictLeads** for job-change events and open positions
4. **Anysite/Webparser** for individual LinkedIn profile depth
5. **WebFetch** for primary sources (press releases, sustainability statements) when others fail

> Providers in this list have been exercised on at least one real account run. If you reach for a tool that isn't here, exercise it once and document the concrete job it did before adding it. Listed-but-unused is exactly the trap this playbook is supposed to prevent.

## Apollo (the workhorse)

**What it's good for**:
- Broad roster pull (600–1000 people from a 100K+ employer in DACH)
- Title corroboration and seniority bucketing
- Organization enrichment (industry, employee count, funding)
- Job postings (`apollo_organizations_job_postings`) — the fallback when PredictLeads is down

**Quirks**:
- `apollo_mixed_people_api_search` with `q_organization_domains` is the standard incantation for "everyone at a company"
- Locations filter: `person_locations[]` works but is loosely matched (use "Germany" not "DE")
- Page size 25 is typical; 100 sometimes works for high-quota accounts
- Email reveals cost extra; toggle `person_email_verification_status` carefully

**Cost**: ~$0.05–0.10 per page on retail; effectively free under most subscriptions.

## PredictLeads

**What it's good for**:
- Hire / leave / promote / retire events with verified dates
- Job openings filtered by category
- Financing events
- Tech detection

**Quirks**:
- Date parameter is `found_at_from`, not `created_at`
- Categories accept an array; the doc says comma-string but that doesn't work
- Company identifier accepts domain (`basf.com`) directly — no lookup needed for well-known entities

**Failure mode**:
- **Every endpoint returns `MCP error -32603` when the server is wedged.** Including `api_subscription`. This happened on the BASF run 2026-05-28 even after a token top-up. Don't loop. Pivot to Apollo's equivalents.
- Cached JSON dumps at `sales-prep/{slug}/data/{slug}_jobs_raw.json` and `{slug}_news_raw.json` survive between runs and are often only 3–7 days stale, which is usually fine.

**Press-release backfill** (when PredictLeads is dark):
1. WebFetch the company's news-releases landing page
2. Scan for personnel/board changes (search for "appoints", "promotes", "successor", "joins", "retires")
3. Follow each press-release URL
4. Extract: date, type (hire/leave/promote/retire), name, role, source URL
5. ~30 minutes for a 12-month sweep, produces 10–15 verified events on a large group

## Extruct (MCP + CLI)

**What it's good for**:
- Company database queries
- AI Tables for repeatable enrichment workflows
- Lookalike search

**Quirks**:
- MCP auth flow is fragile. When MCP writes fail, pivot to the `extruct-api` CLI (bundled with the `extruct-skills` plugin).
- CLI needs `.env` token + `SSL_CERT_FILE` env-var fix on some macOS setups
- Two distinct Extruct accounts often exist for the same user (e.g., `danny@extruct.ai` vs `danny.kewazo@extruct.ai`). Check which one owns the table.
- **Never trigger `/run` (full-column or full-table) without explicit per-run authorization.** Empty `{}` request body equals full-table run.
- Free credits for the operator (don't optimize cost; optimize correctness).

## Anysite / Webparser

**What it's good for**:
- LinkedIn profile scrapes (recent posts, activities, speaking events)
- Careers page scrapes
- News article extraction

**Quirks**:
- Two-step: `mcp__claude_ai_Anysite__discover(source, category)` → `mcp__claude_ai_Anysite__execute(source, category, endpoint, params)`. Always discover first; endpoint names are not guessable.
- LinkedIn-scraping returns 999 to bots, but real profiles render fine for humans. **The 999 from curl is anti-bot, not a broken URL.**
- For LinkedIn profile URLs in the dashboard, link them through and let the human resolve — don't try to render scraped content inline.

## WebFetch (primary sources)

When all enrichment providers fail, fall back to authoritative primary sources:

- Company sustainability reports (often confirm L&D / DEI / AI commitments)
- Press releases (`/global/en/media/news-releases/` is the standard path for European multinationals)
- Annual reports / 10-Ks
- LinkedIn URN URLs for individual posts (`linkedin.com/feed/update/urn:li:activity:NNNNNN`)
- News aggregators (G2 customer pages, Databricks customer stories, etc.)

**WebFetch via Claude tool is free**; it's the cheapest fallback once you know what to look for.

## BigQuery (`bq-readonly`)

Read-only access to `fresh-electron-418200` via the bq-readonly service account. For one-off data analysis that doesn't fit any MCP. Use sparingly — for joining enrichment data with internal CRM-derived tables when needed.

## Decision tree

```
Need broad roster?       → Apollo apollo_mixed_people_api_search
Need leadership events?  → PredictLeads company_news_events
                            ↳ if down → Apollo apollo_contacts_search + press-release backfill
Need job postings?       → PredictLeads company_job_openings
                            ↳ if down → Apollo apollo_organizations_job_postings
Need profile depth?      → Anysite discover + execute
Need email?              → Apollo person enrichment (free at subscription tier)
Need primary source?     → WebFetch
```

## Anti-patterns

- Pulling 1000+ people from Apollo without segmenting first; you'll get noise. But segment for volume, not to decide who the buyers are: bias to inclusion. Don't hard-exclude by region, by blank Apollo department metadata, or by an exact current-title match; match on the function a person owns and their recent trajectory (last one or two roles), and let scoring rank the marginal ones down. Excluding upstream hides the miss; one extra row doesn't.
- Hitting LinkedIn directly from curl and concluding the URL is broken because you got 999.
- Looping on a wedged PredictLeads MCP. After 2 retries, pivot. Document the failure in the methodology doc so the next person knows.
- Burning email-lookup credits across the full roster instead of just the 10–15 curated buyers.
- Trusting a single provider for confirmation. A tech detection from Apollo title-cluster alone is `inferred`, not `confirmed`. Get a second source (signal or URL) before marking it `confirmed`.
- Listing a tool here that you haven't actually used. If it doesn't have a "what we proved on a real run" line, it doesn't go in the playbook — see the methodology doc's "Untested providers — graveyard" section.
