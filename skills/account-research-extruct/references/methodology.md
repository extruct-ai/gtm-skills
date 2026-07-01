# Account research instructions

Internal runbook for researching a target account, enriching its buying signals, and presenting findings in the Extruct dashboard shell. Draft; not yet a published skill.

## Workflow at a glance

```
DISCOVER → ENRICH → LINK → PRESENT
   ↓         ↓        ↓        ↓
subsidiaries  people  person→signal  full-page detail views
teams         job-change tier 1/2/3   tiered "Related people"
signals       URL-truth                URL-driven filters
```

Each step has a primary data source and a fallback. Never trust one provider.

## DISCOVER: surface the account's structure

The goal is a defensible answer to "what does this company look like, where are the buyers, and what's happening this quarter?"

- **Subsidiaries / legal entities**: BASF taught us that "BASF" is a holding (`BASF SE`) with ~38 DACH GmbHs underneath, several of which are the real buying entities (`BASF Business Services GmbH` for GBS, `BASF Coatings GmbH` for the carve-out, etc.). For any large group, the *legal entity* is more useful than the brand. Sources: SEC filings, German Handelsregister, the company's own "Organization" page.
- **Teams / academies**: surface internal program names ("Human Capability Future Unit", "Global Technical Academy", "AI Innovation Center"). These come from sustainability reports, LinkedIn `_about` sections, and Apollo title-cluster analysis. Each team gets a heading and a door tag.
- **Doors**: organize teams into 3–5 "doors" (outreach paths). Each door has a strategic thesis ("AI Enablement + FOX", "GBS Workforce Enablement"). Doors are how reps decide what to lead with.
- **Signals**: time-stamped, sourced events. Each signal has a confidence (H/M/L), a bucket (AI/L&D/Workforce/Tech stack/etc.), a source URL, and a "why it matters" line.
- **Flags**: time-bounded windows (carve-out closes, spinout effective date). Different from signals because they have a deadline.

## ENRICH: get the people

Order matters. Cheaper, broader first; expensive, narrower last.

| Layer | Source | What you get | Cost / brittleness |
|---|---|---|---|
| Roster (~600-1000) | Apollo `apollo_mixed_people_api_search` filtered by company + DACH | Names, titles, locations, LinkedIn URLs, emails | Cheap, broad |
| Title corroboration | Apollo title text + tech detection | "Senior Specialist BizX" implies SuccessFactors HCM | Cheap |
| Curated buyers | Hand-pick from the roster based on title pattern + door alignment | The 12 named buyers in `window.PEOPLE` | Manual, judgment |
| Profile depth | Anysite (webparser) on individual LinkedIn URLs | Recent posts, activities, speaking | Brittle, anti-bot |
| Job-change events | PredictLeads `company_news_events` with `categories: hires, leaves, promotes, retires_from` | Verified leadership churn with dates | Provider-dependent |
| Open positions | PredictLeads `company_job_openings` or Apollo `apollo_organizations_job_postings` | What the company is hiring for (proxy for org change) | Provider-dependent |

**Never expose source vendor names in customer-facing copy.** No "Apollo enrichment" in a `sourceLabel`. No "PredictLeads detected" in a dashboard. Strip these on the way in. The user-facing label is "Internal people graph" or "Internal directory" if there's no public URL to point at.

## LINK: connect signals to people (the Tier model)

This is the most non-obvious piece. A signal alone is dead weight. A signal tagged to *people who own the decision* is a wedge. We use a three-tier model.

| Tier | Method | When to use | Confidence |
|---|---|---|---|
| **Tier 1 — Mentioned in source** | NER over the source document, role-of-mention (author / quoted / referenced) | Sustainability report names a person; LinkedIn post is authored by them; press release quotes them | 0.85–1.0 |
| **Tier 2 — Aligned by function** | Deterministic rules: bucket alignment, team membership, seniority proximity, geo overlap | "AI signal → all AI Enablement people"; "Ludwigshafen signal → all Ludwigshafen people" | 0.4–0.7 |
| **Tier 3 — Researcher agent** | Per-signal LLM agent reasons over signal text + the people pool, returns ranked candidates with rationale, plus a role category (`owner` / `accountable` / `affected` / `champion`) | "BizX rollout → who owns HRIS, not just who has 'HR' in their title?" | 0.5–0.8 |

**Tier 3 runs on every signal** (cost is bounded: per-account signals are O(10–50), not thousands). Results land in a `person_signal` join: `(person_id, signal_id, tier, confidence, role_category, rationale, user_verdict)`. Multiple tiers can co-tag the same pair; that's the strongest signal.

UI surfaces the three tiers as labeled sections within "Related people":
1. "Mentioned in source" (Tier 1)
2. "Likely owners" (Tier 3)
3. "Aligned by function" (Tier 2)

## PRESENT: the dashboard rules

- **Each entity gets a full-page detail view**: PersonPage, SignalPage, SubsidiaryPage. Tabs, breadcrumb, 2-column overview (left rail with facts, main with narrative + related entities). No right-side drawers.
- **URLs encode state**: `#person/:id`, `#signal/:id`, `#subsidiary/:id`, `#people?view=team&door=Door+1&flag=flag-1`. The hash is the share-link.
- **Filter state lives in the URL**, not in component state. Backend reads/writes only.
- **Sources must be verifiable**: every signal's "Read source" button must be a real `<a href>` that returns 200. URLs that 404 break trust harder than no link at all. Curl every URL before committing it to data. For derived-from-internal-data signals, render a "Derived" pill instead of a broken link.
- **Abbreviations get tooltips**: `<abbr title>` on GBS, BizX, HCM, HRIS, LMS, L&D, OpEx, EHS, AgSol, BASD, FTE, DACH, FOX, HRBP. Otherwise the user has to translate every paragraph.
- **Entity references are linkified**: "Door 2" in a why-it-matters paragraph is a clickable span that routes to `#people?door=Door+2`. Person names are clickable to `#person/:id`. Team names get the same treatment when worth it.
- **Counts must be real**: "View N people in this door" must reflect the broader pool count (from `getAllPeople()`), not the curated 12. Hardcoded 3-per-door breaks trust on first inspection.
- **No vendor names visible**: see ENRICH section. Apollo, PredictLeads stay backstage.
- **No side-stripe borders, no gradient text, no glassmorphism, no hero-metric template, no identical-card grids**. Cards are the lazy answer — use them only when truly the best affordance.

## MCP / provider gotchas

This section captures what to do when the data layer fights back.

### PredictLeads

- Used for: hire/leave/promote events, job openings, financing events, technology detection.
- **Use the FULL source catalog (we under-used it on early runs).** Endpoints worth pulling per account:
  - `company_news_events` — leadership churn (hires/leaves/promotes/retires), cost-cutting (decreases_headcount_by, closes_offices_in), partnerships, launches, awards, spin-offs. Article URLs live in `included`; extract + curl-verify them.
  - `company_job_openings` — active AND closed, with first_seen/last_seen + categories + status. Recency-sorted, so for a 24-month trend you must date-window (`first_seen_at_from`/`_until`) or paginate; one 1000-row call only reaches back ~12 months. Bucket by theme + market: opened-vs-closed mix is an automation-pressure signal; the top customer-service-hiring market is the delivery hub to target.
  - `company_technology_detections` — the real stack (resolve technology names via `included`). Trust multi-source/high-score detections; single-source score 0.25 are weak.
  - `company_connections` — partner/vendor/integration/customer graph (find the incumbent vendor + integration surface). Caveat: often dominated by the company's own brand/subsidiary graph and generic links; resolve the OTHER side carefully.
  - `company_products` — the product lines the company SELLS (distinguish sell-side products from internal stack, e.g. a telco selling "Contact Center Solutions" ≠ what it runs internally).
  - Also available: `company_financing_events`, `company_website_evolution`, `company_similar_companies`, `company_github_repositories`, plus `discover_*` endpoints.
- Responses are large; they get saved to a tool-results file. Parse with python (`body` is a JSON string under `{status_code, body}`; data is JSON:API `data[]` + `included[]`).
- **Failure mode**: every endpoint returns `MCP error -32603: Internal error` when the MCP server is wedged. Including `api_subscription` (status check). Don't loop. Pivot to Apollo's analogous endpoints (`apollo_organizations_job_postings`, person events via `apollo_contacts_search`).
- **Confirmed offline 2026-05-28** (BASF run). Token top-up did not resolve. Worth pinging support before relying on it again. Cached JSON dumps at `data/{account}_jobs_raw.json` and `data/{account}_news_raw.json` (≥3 days old) plus press-release backfill were sufficient for a 12-month leadership-churn pass.
- Date parameter is `found_at_from` not `created_at`. Categories are an array (not comma-string despite what the doc says).
- Company identifier accepts domain (`basf.com`) directly. No lookup needed for well-known entities.
- **Press-release backfill workflow** (when PredictLeads is dark): WebFetch the BASF news-releases landing, scan for personnel/board changes, follow each `p-YY-NNN` URL. Extract: date, type (hire/leave/promote/retire), name, role, source URL. 12-month sweep takes ~30 min and produces 10–15 verified events on a large group.

### Extruct (MCP + CLI)

- Used for: company database queries, AI Tables for repeatable enrichment.
- **Failure mode**: MCP auth flow is fragile. When MCP writes fail, pivot to the `claude-api` skill or the `extruct-api` CLI bundled with `extruct-skills` plugin.
- CLI needs `.env` token + `SSL_CERT_FILE` env-var fix on some macOS setups.
- `danny@extruct.ai` vs `danny.kewazo@extruct.ai` are two distinct Extruct accounts. Check which one owns the table.
- Never trigger `/run` (full-column or full-table) without explicit per-run authorization. Empty `{}` request body equals full-table run.
- Free credits for the operator (don't optimize cost; optimize correctness).

### Apollo

- Used for: people search (broad roster pull), company job postings, organization enrichment.
- Reliable, well-documented. Use this as the default fallback when PredictLeads is down.
- `apollo_organizations_job_postings` is the swap for `company_job_openings`.
- `apollo_mixed_people_api_search` with `q_organization_domains` is the way to pull a company's DACH roster.

### Anysite / Webparser

- Used for: scraping individual pages (LinkedIn profiles, careers pages, news articles).
- Two-step: `discover(source, category)` → `execute(source, category, endpoint, params)`. Always discover first; endpoint names are not guessable.
- LinkedIn-scraping returns 999 to bots but real profiles render fine for humans. The 999 status from `curl` is anti-bot, not a broken URL.

### BigQuery (`bq-readonly`)

- Read-only access to `fresh-electron-418200`. Service account at canonical path (see `reference_bigquery_readonly` memory).
- For one-off data analysis that doesn't fit any MCP.

### Untested providers — graveyard (do not add to the main playbook)

Providers go in this graveyard until they've been exercised on at least one real account run with a concrete outcome. Listing a tool here is the honest version of "we know it exists but we haven't proven it earns a spot." If you reach for one of these on a new run, move it up into the main playbook only after you've used it and can document the specific job it did.

- **Saber.** Signal subscriptions, scoring profiles, contact research, `findEmail`. Removed from the main playbook 2026-05-29 after the BASF audit (0 Saber tools invoked, 0 Saber files, 0 references in the BASF data). Saber's shape (push-based feeds + continuous scoring across many accounts) is the opposite of per-account deep research, so it doesn't naturally fit this skill. If we ever build a "warm watch" companion workflow over named buyers, Saber goes there.

## Verification habits (non-negotiable)

- **Curl every source URL before committing it to the dashboard data.** If `curl -sIL` returns 404, don't paste the URL. Use the closest working landing page and label it as such ("BASF news releases (landing)").
- **Browser-verify UI changes via puppeteer.** Headless Chrome, navigate to affected URL, assert specific DOM state (`activeChips`, `hash`, `banner.textContent`, row counts), not just "no console errors". A "page loaded" check misses prop-mismatch bugs.
- **Cache disabled** when verifying. Python `http.server` doesn't set cache-busting headers; Chrome holds onto stale JSX.
- **Don't claim a fix works until the browser has confirmed it.** "I think this should work" is not done.

## Account-research outputs (what to deliver)

For any new account, produce:

1. `sales-prep/{account-slug}/findings/` markdown files:
   - `01_company_overview.md` — legal entity tree, sites, headcount
   - `02_teams_academies.md` — L&D/AI/HR programs and their leads
   - `03_doors.md` — 3–5 outreach paths with thesis
   - `04_signals.md` — every sourced event with URL
   - `05_flags.md` — time-bounded windows
   - `06_named_buyers.md` — 10–15 curated people with angle per person
   - `07_account_brief_vN.md` — the AE-facing distilled brief
2. `sales-prep/{account-slug}/dashboard-mockup/` (if presenting visually):
   - `src/data.js` with `window.PEOPLE`, `window.SIGNALS`, `window.TEAMS`, `window.SUBSIDIARIES`, `window.PERSON_SIGNAL`, etc.
   - All the page components reused from the BASF mockup
3. `sales-prep/{account-slug}/data/` raw API dumps (Apollo CSVs, PredictLeads JSON), kept separate from human-readable deliverables.

## Anti-patterns to refuse

- **"We have X enriched from Apollo"** in any user-facing string.
- **Hardcoding per-door contact lists** when the broader pool exists.
- **Card grids of icon + heading + 2-line summary** repeated as the primary IA. The grid IS the visual cliché. Use accordions, tables, or 2-col detail layouts.
- **Right-side detail drawers** for entity detail. Use full-page views with breadcrumb back-navigation.
- **Em dashes anywhere.** Use commas, colons, semicolons, periods, or parentheses.
- **Side-stripe borders** as accent. Banned.
- **Score badges on every row.** The score is meaningful in the curated People list, not in every Related-people popout.
- **"Open source" buttons that toast instead of linking.** Either link to the real URL or render as a "Derived" pill.

## How doors are designed

Doors are how a rep enters the account. Each one is a single outreach narrative with a named champion, a defensible thesis, and a distinct buyer profile. The design rules:

1. **Cluster signals by functional bucket** — L&D corporate, divisional AI, transformation / cost, vocational, GBS / shared services, tech-stack. One signal can show up in two clusters; that's fine.
2. **Pick the smallest set of distinct narratives that cover every cluster.** A "narrative" is one sentence a rep can repeat without notes: "FOX deployed AI; the missing layer is measurement of who can actually use it."
3. **Each door must pass four tests:**
   - Clear functional thesis (not "we sell L&D to BASF" — that's an industry, not a thesis)
   - At least one named champion with score ≥ 80 (someone seniority-appropriate already saying something the wedge can ride on)
   - Signal density ≥ 2 (two or more sourced events, not one anecdote)
   - Distinct buyer profile (so two doors don't compete for the same person as their primary contact; cross-mapping as secondary is OK)
4. **Rank doors by signal density × seniority of named buyers.** Door 1 is the highest-leverage opener; Door 4 is the lowest-risk fallback if Door 1 doesn't land.
5. **Cap at 4 doors.** Five doors is analysis paralysis for an AE prepping a sequence. If a fifth pattern emerges, it almost always wants to be a *flag* (time-bounded event) instead of a door (durable narrative).
6. **Revisit doors every enrichment pass.** New buyers + new signals can promote a flag into a door (we promoted Door 4 from a flag to a door in BASF v4 once GBS people showed up) or strengthen an existing door without changing the door count.

### BASF: door design decisions and revisions

Original three doors (v1–v3 of the brief):

- **Door 1 — Human Capability Future / strategic L&D.** Built from signal s1 (the 2025 sustainability statement publicly disclosing AI-supported skills and competencies management) plus Uta Schulz as the named program owner. Operational L&D delivered through Christine Edinger (Global Technical Academy) and Janina Allbach. Highest-leverage door because the public commitment removes the "AI-skills is hypothetical" objection.
- **Door 2 — AI Enablement and FOX.** Built from signal s6 (FOX won the 2025 Databricks Digital Award) plus Alican Polat as Divisional AI Lead and Juergen Mueller heading the AI Innovation Center (a parallel program to FOX). Distinct from Door 1 because the buyers and the budget are divisional, not corporate. The pitch is reskilling AI users, the measurement layer FOX is missing.
- **Door 3 — CoreShift + Berufsausbildung.** Built from signal s2 (CoreShift cost mandate, 20% by 2029) intersecting signal s3 (Ludwigshafen no-redundancy pledge). Berufsausbildung (the apprenticeship-pipeline program) is BASF's largest L&D envelope by headcount, so Elmar Benne (VP Vocational Training) holds the biggest single budget signature. Door 3's narrative is reskilling-as-the-only-lever because layoffs are off the table.

Door added in v4 (the only one not present from the start):

- **Door 4 — GBS Workforce Enablement.** Surfaced when the v4 enrichment pass converged three things: (a) Apollo surfaced ~70 GBS DACH names that weren't in earlier pulls; (b) Joerg Schmuelling's title literally contains "Workforce Enablement"; (c) Ege Ozoktas's title confirmed SuccessFactors BizX as the HCM. Pre-v4 we had three doors and missed GBS as a distinct buying entity (a separate legal entity, BASF Business Services GmbH). Adding it took the door count to four. Standardization-at-scale = role-based training-at-scale, so the buyer logic for adaptive training-per-role is the same as the buyer logic for shared services. A single buyer (GBS L&D / Workforce Enablement) can deploy across all divisions instead of selling Coatings, Ag, Chemicals separately.

Reassessment after the 2026-05-28 job-change run (signals s11–s15):

- **No new doors.** Door count stays at 4. The Coatings carve-out (s15) doesn't become Door 5; it stays as flag-1 because Coatings is being divested. If Area9 wins it post-close it becomes its own account, not a BASF door.
- **Door 1 got significantly stronger.** s13 (Aucoin promoted to President of Global Engineering Services, April 2025) means a fresh decision maker now owns the Technical Academy budget envelope where Edinger and Allbach operate; he's ~13 months in, past freeze, into year-two budget planning. s11 (CEO Kamieth absorbs Corporate HR portfolio, May 2026) + s12 (Spandau exit, July 2025) confirm Uta Schulz now reports up a thinner chain with no CHRO buffer — a net escalation path, not a stalling pattern. s14 (Münster Global Talent Development Praktikum) is staffing inside her broader scope.
- **Doors 2, 3, 4 unchanged.** None of the new signals named new buyers in those buckets or shifted the functional thesis.

Net effect: the recommended outreach sequence shifts slightly. Pre-s11–s15 we'd lead with Uta Schulz; post-run she's still first but Aucoin is now a strong third (was previously not in the curated 12). Joerg Schmuelling stays second.

### Strategies = doors (UX naming)

In the dashboard UI, doors are displayed as "strategies" (Human Capability Future, AI Enablement + FOX, etc.) without the "Door 1 / Door 2" prefix. The "Door N" identifier is kept internally for URL routing, data joins, and the methodology language above. When a rep edits a strategy in the dashboard (planned for a later iteration), they're editing the displayed name and the thesis, not the internal ID.

### The data pipeline end-to-end

This is the concrete contract the dashboard runs on. Each arrow is a deterministic transformation; humans curate the inputs, the system computes the outputs.

```
Sources         →    Signals          →    Strategies          →    Tasks
(verified)           (sourced events)      (aggregated narratives)   (next actions)
```

1. **Sources** — press releases, sustainability statements, LinkedIn posts, primary documents, job postings, news scrapes. Each one has a URL that returns 200 (curl-verified) or is marked `derived` if it lives only in internal data. Tech-stack entries cite a source the same way: `signal` (links to the signal that proves it), `url` (external doc), `derived` (rules-based inference), `inferred` (industry baseline, no proof claimed), or `needed` (proof is missing and the dashboard says so).

2. **Signals** — every sourced event becomes one `window.SIGNALS[i]` record with: `id`, `title`, `date`, `confidence` (H / M / L), `sourceLabel`, `sourceUrl`, `sourceType` (`primary` / `social` / `profile` / `derived`), `quote`, `bucket`, `why`, optional `context` for jargon. Confidence is the trust signal; a derived source can be a valid signal but stays at M or L.

3. **Person–Signal linking (the Tier model)** — each signal is tagged to people via `window.PERSON_SIGNAL` rows shaped `{ person_id, signal_id, tier, confidence, role_category, rationale }`. Three tiers, in order of trustworthiness:
   - **Tier 1 — Mentioned in source.** NER on the source document, with role-of-mention (author / quoted / referenced). Confidence 0.85–1.0.
   - **Tier 2 — Aligned by function.** Deterministic rules: bucket alignment, team membership, seniority proximity, geo overlap. Confidence 0.4–0.7.
   - **Tier 3 — Researcher agent.** Per-signal LLM call that reasons over signal text + the full people pool, returns ranked candidates with rationale and a role category (`owner` / `accountable` / `affected` / `champion`). Confidence 0.5–0.8.
   Tier 3 runs on every signal on signal creation; cached in `person_signal` (a backend job in production, hand-mocked in the dashboard). Multiple tiers can co-tag the same `(person, signal)` pair — that's the strongest possible signal.

4. **Signals → Strategies (the aggregation rule)** — a signal "belongs to" a strategy if at least one tagged person's `door` field equals that strategy's `Door N` label. A signal can appear under multiple strategies when its tagged people span doors. Computed by `window.getSignalStrategies(signalId)` which intersects `PERSON_SIGNAL` with `PEOPLE.door`. The Signals tab uses this to render the strategy-grouped view; the StrategyPage uses it (reversed) to list a strategy's signals.

5. **Strategies → Tasks (the generation rule)** — a task is the join of one strategy + one primary person + a "why now" rationale that traces back to source signals. Each task carries:
   - `playbook` — the named pattern: `New decision maker`, `Multi-thread`, `Champion signal`, `Sourced commitment`, `Net new buyer layer`, `Time-sensitive`, `Tech-stack integration`, `Hiring pattern`, `Job switcher`, `New program signal`, `Frontline reality`, `Measurement gap`, `Top-down legitimizer`, `Bottom-up`, `Sustained urgency`, `Tech ROI`.
   - `title` — the action verb-led ("Introduce yourself to Aucoin", "Reach BASF Coatings before Carlyle close")
   - `whyNow` — a per-person rationale grounded in the strategy's signals
   - `whySources[]` — `signal` / `press` / `flag` / `url` references for traceability
   - `strategyId` — which door the task belongs to
   - `primaryPersonId` + `multithreadPersonIds[]` — who to contact
   - `timeSensitive` + `deadline` — flag-driven urgency
   - `priority` (1–3), `status` (`active` / `snoozed` / `actioned` / `dismissed`), `createdAt`
   In production, tasks are generated by an LLM agent that walks the strategy's signal/people graph and emits task candidates; humans approve, edit, or dismiss. In the current dashboard mock, tasks are hand-authored from real signals; the data shape is the contract a generator will need to populate.

6. **Tasks → Inbox (the surfacing rule)** — the Tasks tab is the AE's daily landing. Default filter is `status = active`. Time-sensitive tasks bubble up with an inline deadline pill. Each row expands to show the why-now block (with source chips), the action bar (`Assign · Snooze · Dismiss`), and a mini stakeholder table (avatar · name · role · status · `Open ›` to PersonPage + `LinkedIn`). The left rail of Tasks carries the account-level AI summary (thesis · why now · best wedge) so the "why this account" context is one glance away.

### Why doors / strategies / tasks all exist (the conceptual layering)

A rep doesn't want to read 15 signals every morning. They want a short list of things to do today, with the receipts ready when someone asks "why this person, why now". Strategies are the *narrative compression* layer between raw events and concrete actions: each strategy is a single sentence a rep can repeat. Tasks are the *time-bounded execution* layer on top of strategies: each task is one next-action with the rationale baked in. Signals are the proof layer underneath both.

If a strategy can't generate at least 3–5 tasks, it's not a strategy yet (the narrative isn't crisp enough). If a task can't trace back to ≥1 sourced signal, it's not a task yet (it's a hunch).

### Writing a strategy plan

Every strategy carries a structured `plan` object that the StrategyPage renders. The plan is what a senior AE would write up in a doc and pass to a teammate inheriting the account — concrete enough to execute against, abstract enough to survive a new buyer surfacing tomorrow.

```js
window.DOOR_PLANS["door-N"] = {
  thesis:         "Why this strategy exists as a distinct play. 3–4 sentences.",
  whyNow:         "Timing: what window is open right now and when it closes.",
  wedge:          "The specific positioning angle. What to lead with, what to avoid.",
  buyerSequence:  [
    {
      person_id:    "p-...",
      rank:         1,                              // sequence order
      rationale:    "Why this person at this position in the sequence.",
      openingMove:  "The exact first move to make with this person.",
    },
    // ... 2–5 buyers in priority order
  ],
  riskTriggers:   ["...", "...", "..."],            // 3–5 concrete failure modes
  proofPoints:    ["s1", "s11", "s13"],             // signal IDs that back the plan
};
```

#### How to author each section

**Thesis.** Why does this strategy exist as a distinct play *and not a slice of another*? Answer in 3–4 sentences. Lead with the structural fact (public commitment / awarded program / largest budget envelope / net-new buyer layer), then state the wedge in one line. Bad thesis: "L&D at BASF". Good thesis: "Corporate strategic L&D is the highest-leverage door because the public AI-skills commitment removes the standard objection in one sentence and the named owner is a senior buyer with a thinner reporting chain than the org chart suggests."

**Why now.** Name the dates. Specific weeks and quarters, not generic "recent activity". Identify the window: what triggered it (a signal), what closes it (an event or a calendar boundary), how long the window stays open. Without a calendar boundary, this isn't a why-now, it's a why-this.

**Wedge.** The wedge is *what to lead with* and *what to avoid leading with*. Two halves matter equally. Bad wedge: "we sell adaptive learning". Good wedge: "Lead with the operating-model question; do not pitch a tool. The wedge is architecture, not content." If the wedge doesn't tell the rep what NOT to say in the first meeting, it isn't a wedge.

**Buyer sequence.** Ordered list, 2–5 people. Each step carries three fields:
- `rank` — 1 = engage first, 2 = engage second, etc. Not seniority; not score. *Sequence order.*
- `rationale` — 1–2 sentences on why this person at this position. Why not first? Why not last? What does this position give us that the others don't?
- `openingMove` — the exact first move. Not "introduce ourselves"; the actual sentence to send or the actual question to ask. The opening move is what the rep will copy-paste.

**Risks & blockers.** Concrete failure modes, not vague concerns. Each item names what could go wrong AND how to mitigate it. Bad risk: "buyer may say no". Good risk: "Aucoin defaults to 'let the existing L&D team handle this' because he's new to L&D. Mitigate by leading on engineering-skills measurement which is GES-native, not learning-vendor-shaped." If the risk doesn't have a mitigation, it's not on the list — it's a "kill the strategy" question, not a risk.

**Proof points.** Signal IDs only. If a claim in the plan can't be traced to a signal, the claim doesn't go in the plan. Three to five is the right range; more than that means the plan is over-evidenced for a one-pager.

#### Anti-patterns to refuse when authoring a plan

- **The "ranked by score" buyer sequence.** Sequence is about *order of approach*, not seniority. The top-scored buyer is sometimes second or third in the sequence because they need a warm intro from a champion first. Don't sort by score; reason about access.
- **The "we can also do" wedge.** Adding "we can also help with X" weakens the wedge. The wedge is one positioning. Multiple positionings = no positioning.
- **The "ongoing" why-now.** A why-now without a calendar boundary is a why-this. Calendar boundary or drop the section.
- **The "trust us" risk list.** Every risk must have a concrete failure mode and a concrete mitigation. "Could go wrong" is not a risk.
- **The hand-wavy thesis.** If the thesis can fit on a sales-deck slide as-is, it's marketing copy, not a thesis. The thesis is for the rep, not the prospect.

#### Quality check before shipping a plan

A finished plan should pass these tests:

1. **Repeatability test.** Read the wedge aloud. Could a new rep on the team repeat it back without notes after one read? If no, compress.
2. **First-meeting test.** Pick step 1 of the buyer sequence. Could a rep walk into the meeting tomorrow with just the `openingMove` and run the conversation for 30 minutes? If no, the opening move is too abstract.
3. **Calendar test.** Read the why-now. Is there at least one specific date or quarter? If no, fix it.
4. **Signal trace test.** Pick any claim in the thesis or why-now. Can it be traced to a signal ID in `proofPoints`? If no, either source it or remove it.
5. **Generator test.** Could a Tier 3 LLM agent reading this plan produce 3–5 tasks that pass the existing task quality bar? If no, the plan doesn't have enough material for execution.

The dashboard's StrategyPage Plan tab is the surface this object renders to. Sections that read as "thin" on the rendered page are the sections where the underlying writing wasn't doing the work.

## Open questions / things we still don't have

- True join-date / tenure for the full enriched pool. Currently `isNew` on a PERSON record means "newly surfaced in our research". Job-change events are the source-of-truth, but coverage from leadership-events providers is biased toward C-suite + regional commercial; expect a single-digit hit-rate when cross-referencing leadership churn against an L&D-skewed pool. The Aucoin hit (BASF run, 2026-05-28) is the proof-of-concept — manually re-tagged from TEAM_MEMBERS into PEOPLE with `signals: ["s13"]`.
- Subsidiary→Signal join is hand-curated (`window.SUBSIDIARY_SIGNALS`). Belongs in the same backend join the Tier-3 agent populates.
- Cost basis for the Tier-3 agent in production: O(per-account signals × people pool size) per re-run. Cache aggressively; invalidate on new-person-added or signal-edited.

## Cross-reference workflow (job-change events → pool)

Pattern, proven on BASF 2026-05-28:

1. Pull leadership events for the company domain (PredictLeads cache or Apollo or press-release WebFetch).
2. For each event with a named person, fuzzy-match against `window.PEOPLE` + the names inside `window.TEAM_MEMBERS` and `window.SUBSIDIARY_MEMBERS`. Match on full name + (LinkedIn URL or email if available).
3. **Direct hits**: add a `refId` to the TEAM_MEMBERS record (if missing), promote into `window.PEOPLE` with door/bucket/seniority/score/`signals: [sN]`, add Tier 1 PERSON_SIGNAL row linking person → the job-change signal.
4. **Indirect hits** (the event is *about* someone whose role change affects an existing pool member): add Tier 3 PERSON_SIGNAL rows linking the affected pool members to the signal with `role_category: "affected"` and rationale explaining the budget/reporting-chain impact.
5. Expect 4–5% direct hit rate on a leadership-event sweep against an L&D-skewed pool. The indirect hits (reporting-chain effects) are usually higher value than the direct hit anyway.
