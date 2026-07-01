---
name: account-research-extruct
description: Extruct-harness variant of account-research. Same goal and SAME output contract (a buyer-map dashboard at accounts/{slug}.js + findings), but the execution ENGINE is Extruct Deep Research — the async deep_research_tasks API that returns ONE deep, cited research report mining every layer (overview, numbers, GTM motion + tech stack, launches, segmentation, open/closed roles, leadership/named people, buying committee + honest verdict) in a single xhigh-capable pass, instead of per-layer research_pro columns or a PredictLeads + Apollo pull. Use this skill ONLY when the user explicitly asks for the Extruct-native / Extruct Deep Research version of an account run, or to benchmark the engines. For normal account research, use `account-research`.
---

# Account Research — Extruct Deep Research engine

This is the `account-research` skill with the execution engine set to the **Extruct Deep Research
feature** (`POST /v1/deep_research_tasks`). One async task with 10/25/50 research agents returns a
single fully-cited report covering every layer; you then **assemble that report into the dashboard**.
It replaces the older per-layer `research_pro` columns engine (kept as a benchmark alternate).

- **Same as the original:** the goal (a decision-ready account dossier), the conceptual model
  (RESEARCH → LINK → doors/strategies → tasks), and the **output contract** — the dashboard data file
  `accounts/{slug}.js` and the findings markdown. Output-shape and door-authoring rules are unchanged
  and shared.
- **Different from the original:** the **engine**. Instead of pulling PredictLeads + Apollo, or mining
  one `research_pro` column per layer, this variant issues **one Deep Research brief** and parses the
  returned cited report into the dashboard globals.

```
account-research          (original): PredictLeads + Apollo + Extruct      -> accounts/{slug}.js
account-research-extruct  (this one): Extruct Deep Research (one brief)     -> accounts/{slug}.js
                                       ^ same output, different engine — that is the benchmark
```

## Engine: Extruct Deep Research

The full API workflow, depth levels, brief template, and gotchas:
**[references/deep-research-engine.md](references/deep-research-engine.md)** — read it first. The shape
of the dashboard you must produce is unchanged: **[references/output-shape.md](references/output-shape.md)**.

> The bundled `extruct-api` CLI has **no `deep-research` command** (only `deep-search`). Drive Deep
> Research with the REST API via `curl` using the repo `.env` token, or the Extruct MCP
> (`create_deep_research_task` / `get_deep_research_task`) if it is connected. See the engine doc.

### 0. Confirm access and account
- `~/.ext auth user` BEFORE anything. Use the project's account (`danny@extruct.ai` for
  extruct-research). Never spend credits on the wrong org. Note `available_credits` (Deep Research bills
  1 credit per executed agent — up to 50 at `xhigh`).
- Confirm scope + slug (kebab-case, e.g. `owner`). Capture the **seller**, the **decision to support**,
  and the **region focus** — they go into the brief.

### 1. COMPOSE the brief (the whole skill is the brief)
One `brief` string (<=20,000 chars) carries the seller context, the target, the decision, and a
numbered list of every layer the dashboard needs. Write it so the report contains everything required
to populate the globals. Cover, asking for a **source URL per claim** and to **flag low-confidence /
gaps**:

1. Company overview (→ `ACCOUNT`): what they do, HQ, founded, headcount, mission.
2. Business numbers (→ `SIGNALS`/`TLDR`): funding rounds + dates + investors, valuation, ARR/revenue +
   growth, customers/locations, retention if disclosed. Reconcile disputed figures; label estimates.
3. How they sell + internal GTM tech stack (→ `TECH`,`SIGNALS`): motion, org size/structure, leaders,
   pricing, cycle; CRM / sales-engagement / dialer / conversation-intelligence / data-enrichment /
   warehouse — with evidence; and whether they build GTM data/AI in-house.
4. Recent launches + dated news + leadership changes (→ `SIGNALS`,`FLAGS`).
5. Segmentation + the honest fit/wedge (→ `TLDR`,`DOORS`): who they sell to; the upmarket question;
   how well-mapped the target universe already is by incumbents; where the defensible wedge is (or that
   there isn't one). Be objective even if the verdict is "weak fit".
6. Hiring signals — OPEN and recently FILLED roles in the target functions (→ `JOBS`), and what the
   filled roles imply (e.g. an in-house build = headwind).
7. Named leadership + decision-makers with LinkedIn URLs (→ `PEOPLE`,`TEAM_MEMBERS`).
8. Recommended buying committee + entry angle + concrete first move + honest verdict (→ `DOORS`,
   `TASKS`,`TLDR`).

Bake the SELLER CONTEXT + REGION FOCUS into the brief text (the engine has no per-column context).

### 2. CREATE the Deep Research task
`POST https://api.extruct.ai/v1/deep_research_tasks` with `{ "brief": "...", "depth": "<level>" }`.
- **depth**: `medium` (10 agents) for a quick pass · `high` (25, the default) for a normal run ·
  **`xhigh` (50)** when the user asks for max effort or it is a priority account.
- Optional `output_schema` (JSON Schema) for a structured spine — see the engine doc. Default is the
  markdown cited report.
Capture the returned task `id`.

### 3. POLL to completion
`GET …/deep_research_tasks/{id}` every ~15-25s until `status` is `done` or `failed` (progress shows in
`agents`/`sources`/`iterations`). **Gotcha:** the GET echoes the brief with literal newlines, so a
strict JSON parse throws "Invalid control character" — parse with `json.loads(..., strict=False)`.
A 50-agent `xhigh` run can take 10-20+ min; poll in the background.

### 4. SAVE the findings
Write the cited report to `research/{slug}-deep-research/` (or `sales-prep/{slug}/findings/`):
`report.md` (the `report.markdown`, with a provenance header: task id, depth, agents/sources/iterations),
`sources.md` (numbered `report.sources` `{id,url}`), and `task.json` (raw record). Check
`report.degradation_reasons` and record any coverage gaps honestly.

### 5. ASSEMBLE the dashboard (same contract)
Read the report and map its sections to the `window.*` globals in
[references/output-shape.md](references/output-shape.md). Resolve each `[n]` citation to its
`report.sources[n].url` for the `sourceUrl` fields. Populate `JOBS` + `JOBS_META` from the open/closed
roles section. Do NOT invent globals — the dashboard only renders the documented ones. Then
`node scripts/build_accounts_index.js`.

### 6. LINK + doors + tasks
Identical to the original: tag signals to buyers (Tier model), cluster into <=4 doors (thesis / wedge /
calendar-bound why-now / primary buyer / >=2 backing signals / first move), generate tasks. See
[references/strategy-plans.md](references/strategy-plans.md). The report's "buying committee / verdict"
section is the raw material; keep its honest verdict — do not re-inflate a weak-fit into a slam-dunk.

### 7. Verify (same as original)
- Curl every external `sourceUrl` (2xx, or 999 LinkedIn). Render 403 anti-bot sources as `derived`.
- `node --check` + data-integrity (unique ids, no dangling PERSON_SIGNAL/refId/task refs, valid
  playbooks/strategies, complete DOOR_PLANS) + `helpers.js` builds.
- Serve and load `?account={slug}`; confirm the Jobs/People/Signals tabs populate.

## Engine character (this is the point of the benchmark)
Deep Research is **strong where the columns engine was weak**: one pass returns a fuller leadership
roster, reconciled/disputed numbers, named incumbents, dated launches, and an honest fit verdict, all
cited (a real run on Owner.com: 42 agents, 142 sources, 9 iterations). Its trade-offs vs structured
columns: it returns **prose, not typed cells**, so the assembly step (5) does the structuring; it will
**not enumerate a full job board** (expect the GTM/data-relevant roles, not 1,000+ rows); and
single-source claims (e.g. "uses vendor X" from one article) carry that confidence — surface it, do not
upgrade it. Capture what the report actually delivered; that delta IS the benchmark result.

## Hard rules (unchanged from the original)
- No vendor/tool names in user-facing dashboard output. No em dashes. Calendar-bound why-now only.
  <=4 doors.
- Never fabricate to fill the dashboard. A smaller, fully-sourced result beats a padded one. Keep
  single-source / low-confidence items labelled as such.
- If a required Extruct stage is wedged (task stuck in `in_progress` with no agent progress, or
  `failed`), STOP and say so; do not backfill with web search.

## Reference files
- [references/deep-research-engine.md](references/deep-research-engine.md) — the Deep Research API workflow, depth levels, brief template, gotchas (the engine).
- [references/output-shape.md](references/output-shape.md) — the dashboard data contract (shared, unchanged).
- [references/strategy-plans.md](references/strategy-plans.md) — door/strategy authoring (shared).
- [references/extruct-harness.md](references/extruct-harness.md) — the LEGACY `research_pro` columns engine, kept as the benchmark alternate.
- [references/methodology.md](references/methodology.md) / [references/enrich.md](references/enrich.md) — the original provider-based engine, kept as background for comparison.
