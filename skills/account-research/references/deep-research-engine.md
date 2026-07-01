# Extruct Deep Research — the engine

Run an entire account research as ONE Extruct Deep Research task and assemble the cited report into the
dossier. Deep Research is the async `deep_research_tasks` feature: it fans out 10/25/50 agents over the
web + Extruct's index and returns a single cited report. Docs:
`docs.extruct.ai/api-guides/research/deep-research`.

> The bundled `extruct-api` CLI does not implement Deep Research (only `deep-search`/discovery). Drive
> it with `curl` + the repo `.env` token, or the Extruct MCP (`create_deep_research_task` /
> `get_deep_research_task`) if connected. Both hit the same API.

## 0. Access + account (FIRST)
```
~/.ext auth user        # MUST be the project account (danny@extruct.ai). Note available_credits.
```
Deep Research bills **1 credit per executed agent** (max 50 at `xhigh`); failed tasks are refunded. The
token lives in the repo `.env` as `EXTRUCT_API_TOKEN` (the `~/.ext` wrapper reads it but only execs the
CLI, so for raw curl read it yourself).

## 1. Endpoints, auth, params
- **Create:** `POST https://api.extruct.ai/v1/deep_research_tasks`
- **Poll/Get:** `GET https://api.extruct.ai/v1/deep_research_tasks/{id}`
- **List:** `GET https://api.extruct.ai/v1/deep_research_tasks`
- **Auth:** `Authorization: Bearer $EXTRUCT_API_TOKEN`

Request body:

| Field | Req | Notes |
|---|---|---|
| `brief` | yes | 1–20,000 chars. Name the target, give seller context + the decision to support + the numbered layer asks (SKILL.md Step 2). Specific briefs yield better reports. |
| `depth` | no | `medium` (10 agents) · `high` (25, default) · `xhigh` (50). Full budget must be available; only executed agents are billed. |
| `output_schema` | no | JSON Schema (`type:"object"`) for structured output instead of markdown. <=5 nesting levels, <=50 properties. Use "Evidenced" wrappers (`{value, sources[], reasoning}`) for sourced fields. Default is the markdown cited report. |

Response (create): `{ id, status:"created", brief, depth, iterations:0, agents:0, sources:0, report:null, owner:{email} }`.
Lifecycle: `created` → `in_progress` → `done` | `failed`.

## 2. Create (curl)
Write the body to a file to avoid shell-escaping the multi-line brief.
```bash
cd <repo-root>
TOKEN="$(grep '^EXTRUCT_API_TOKEN=' .env | head -1 | cut -d= -f2- | tr -d '"'\''"')"
# payload.json = {"brief":"...","depth":"high"}
curl -s -X POST https://api.extruct.ai/v1/deep_research_tasks \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  --data @payload.json          # -> capture .id
```

## 3. Poll (background) — mind the JSON gotcha
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
Run with `run_in_background: true` — an `xhigh` run can take 10-20+ min. If `status` sticks in
`in_progress` with counts that never advance, treat it as wedged: STOP and tell the user.

## 4. Read the report
From the `done` task JSON (`strict=False`):
- `report.markdown` — the cited report; inline `[n]` resolve to `report.sources[n]` (`{id, url}`).
- `report.sources` — the numbered URL list.
- `report.degradation_reasons` — coverage gaps to surface honestly (often `null`).
- (schema mode) `report.fields` instead of `markdown`.

## 5. Assemble → dossier
Map the report to the dossier files (SKILL.md Step 4), resolving each `[n]` → `report.sources[n].url`:
overview + entity tree → `overview.md`; dated events/roles/news/tech/leadership → `signals.md`; named
buyers per unit + tier-tagged angle → `buyer-map.md`; the distilled angle/people/why-now →
`account-brief.md`. Save the raw `report.markdown` as `report.md` + a numbered `sources.md` for
provenance. Tier model + entry-angle rules: [methodology.md](methodology.md).

## Worked example (Owner.com, 2026-06-30)
Task `8a2dcbe9-0a12-45dc-a179-d57c302d7295`, `depth:"xhigh"` → 42 agents, 142 sources, 9 iterations,
`degradation_reasons:null`; ~42 credits. One brief returned a full leadership roster, reconciled
disputed ARR, a named incumbent (single-source — flagged), and an honest fit verdict — the entity +
people layer in one pass.

## Billing / etiquette
- 1 credit per executed agent (medium<=10, high<=25, xhigh<=50). Failed = refunded.
- Default `high`; reserve `xhigh` for priority or explicitly-max-effort runs.
- One brief per account.
