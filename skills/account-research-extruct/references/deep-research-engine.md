# Extruct Deep Research — the engine for account-research-extruct

How to run an entire account research as ONE Extruct Deep Research task and parse the cited report into
the dashboard. Deep Research is the async `deep_research_tasks` feature: it fans out 10/25/50 agents
over the web + Extruct's index and returns a single cited report. Docs:
`docs.extruct.ai/api-guides/research/deep-research`.

> The bundled `extruct-api` CLI does **not** implement Deep Research (only `deep-search`/discovery). So
> drive it with `curl` + the repo `.env` token, or the Extruct MCP if connected. Both hit the same API.

## 0. Access + account (do this FIRST)
```
~/.ext auth user        # MUST be the project account (danny@extruct.ai). Note available_credits.
```
Deep Research bills **1 credit per executed agent** (max 50 at `xhigh`); failed tasks are refunded. The
token the curl calls use lives in the repo `.env` as `EXTRUCT_API_TOKEN` (the `~/.ext` wrapper reads it
but only execs the CLI, so for raw curl read it yourself).

## 1. Endpoints, auth, params
- **Create:** `POST https://api.extruct.ai/v1/deep_research_tasks`
- **Poll/Get:** `GET https://api.extruct.ai/v1/deep_research_tasks/{id}`
- **List:** `GET https://api.extruct.ai/v1/deep_research_tasks`
- **Auth:** `Authorization: Bearer $EXTRUCT_API_TOKEN`

Request body:

| Field | Req | Notes |
|---|---|---|
| `brief` | yes | 1–20,000 chars. Name the target(s), give seller context + the decision to support + the numbered layer asks (see template). Specific briefs yield better reports. |
| `depth` | no | `medium` (10 agents) · `high` (25, default) · `xhigh` (50). Full budget must be available; only executed agents are billed. |
| `output_schema` | no | JSON Schema (`type:"object"`) for structured output instead of markdown. <=5 nesting levels, <=50 properties. Use "Evidenced" wrappers (`{value, sources[], reasoning}`) for sourced fields. |

Response (create): `{ id, status:"created", brief, depth, iterations:0, agents:0, sources:0, report:null, owner:{email} }`.
Lifecycle: `created` → `in_progress` → `done` | `failed`.

## 2. The brief template (fill the {braces})
Keep it one string. This is the entire research spec — make it map to the dashboard globals.

```
Seller context: We are {SELLER} ({seller_domain}) — {one line on what the seller sells and how it is
positioned}. We are preparing to sell {seller product} to {TARGET}.

Target: {TARGET} ({target_domain}) — {one line identity}. Region focus: {REGION}.

Decision to support: a first sales conversation — how to position {SELLER} to {TARGET}, exactly who to
sell to, and an honest, evidence-based assessment of whether and where {SELLER} adds value.

Produce a decision-ready, fully cited report. Cite a source URL for every factual claim, label
estimates, and flag coverage gaps / low-confidence items:
1. Company overview: what {TARGET} does, HQ, founding year, headcount, mission.
2. Business numbers: funding rounds (amount, date, lead investors), valuation, ARR/revenue + growth,
   customers/locations, retention/unit economics. Reconcile disputed figures.
3. How {TARGET} sells: motion (inbound/outbound, sales-led/self-serve), sales/SDR/AE org size +
   structure + leaders, pricing/packaging, sales cycle; and the INTERNAL GTM tech stack with evidence
   (CRM, sales engagement, dialer, conversation intelligence, data/enrichment/prospecting, warehouse/BI);
   and whether they build GTM data/AI in-house.
4. Recent product launches + dated company news + leadership changes (last 18-24 months).
5. Customer segmentation + the upmarket question: who they sell to today; the upmarket opportunity; how
   well-mapped that universe already is by existing/vertical data vendors; and an objective EASY-vs-HARD
   verdict per segment. State plainly if a segment is well-served (a weak fit for {SELLER}).
6. Hiring signals: current OPEN and recently FILLED roles in {target functions}, and what the filled
   roles imply (in-house build = headwind).
7. Leadership + decision-makers relevant to {SELLER}: names + exact titles + LinkedIn URLs.
8. Recommended buying committee + entry angle + concrete first move + an explicit honest verdict on
   whether {TARGET} is a strong fit and, if so, the narrow defensible wedge.
```

## 3. Create (curl)
```bash
cd <repo-root>
TOKEN="$(grep '^EXTRUCT_API_TOKEN=' .env | head -1 | cut -d= -f2- | tr -d '"'\''"')"
# write the body to a file to avoid shell-escaping the multi-line brief:
#   payload.json = {"brief":"...","depth":"xhigh"}
curl -s -X POST https://api.extruct.ai/v1/deep_research_tasks \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  --data @payload.json
# -> capture .id
```

## 4. Poll (background) — mind the JSON gotcha
The GET response echoes `brief` back **with literal newlines**, so a strict JSON parse fails with
"Invalid control character at …". Always parse with `strict=False`.
```bash
ID=<task_id>; OUT=scratch/dr.json
for i in $(seq 1 120); do
  curl -s -H "Authorization: Bearer $TOKEN" "https://api.extruct.ai/v1/deep_research_tasks/$ID" > "$OUT"
  read s rest < <(python3 -c "import json;d=json.load(open('$OUT'),strict=False);print(d.get('status'),'agents',d.get('agents'),'sources',d.get('sources'),'iters',d.get('iterations'))")
  echo "$(date +%H:%M:%S) status=$s $rest"
  [ "$s" = "done" ] || [ "$s" = "failed" ] && break
  sleep 25
done
```
Run this with `run_in_background: true` (an `xhigh` run can take 10-20+ min). If `status` sticks in
`in_progress` with agent/source counts that never advance, treat it as wedged: STOP and tell the user.

## 5. Read the report
From the `done` task JSON (`strict=False`):
- `report.markdown` — the cited report; inline `[n]` resolve to `report.sources[n]` (`{id, url}`).
- `report.sources` — the numbered URL list.
- `report.degradation_reasons` — coverage gaps to surface honestly (often `null`).
- (schema mode) `report.fields` instead of `markdown`.

## 6. Structured mode (optional) — output_schema
For a deterministic spine, pass an `output_schema` so the engine returns typed JSON. Keep it within
limits (<=5 nesting, <=50 props) — a full dashboard schema is too big, so request just the structured
arrays you most want machine-clean (e.g. `people`, `signals`, `doors`) with Evidenced wrappers, and
take the rest from a companion markdown run. Default to markdown → assemble unless you specifically need
the structured spine.

## 7. Assemble → dashboard
Map report sections to the globals in [output-shape.md](output-shape.md), resolving `[n]` → source URL:
- overview → `ACCOUNT`; numbers/news/leadership/launches → `SIGNALS` (+ `FLAGS` for calendar-bound);
  GTM stack → `TECH`/`TECH_CATEGORIES`; open/closed roles → `JOBS` + `JOBS_META`; named leaders/buyers →
  `PEOPLE` + `TEAM_MEMBERS`; segmentation + verdict + entry angle → `TLDR` + `DOORS` + `DOOR_PLANS`;
  first moves → `TASKS`. Tag `PERSON_SIGNAL` with the Tier model. Then
  `node scripts/build_accounts_index.js` and verify.

## Worked example (Owner.com, 2026-06-30)
Task `8a2dcbe9-0a12-45dc-a179-d57c302d7295`, `depth:"xhigh"` → 42 agents, 142 sources, 9 iterations,
`degradation_reasons:null`; ~42 credits. Output saved to `research/owner-deep-research/`. It returned a
fuller leadership roster, reconciled disputed ARR, named the actual restaurant-data incumbent (from a
single GTM article — flagged medium-confidence), and an honest "narrow wedge, discovery is a trap"
verdict — i.e. the entity layer the columns engine kept returning "not found" on.

## Billing / etiquette
- 1 credit per executed agent (medium<=10, high<=25, xhigh<=50). Failed = refunded.
- Default `high`; reserve `xhigh` for priority or explicitly-max-effort runs.
- One brief per account. Do not also run the columns engine on the same account unless benchmarking.
```
