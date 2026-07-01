# Extruct harness — the engine for account-research-extruct

How to run an account research entirely inside Extruct AI Tables. Drive via the bundled
`extruct-skills:extruct-api` CLI (preferred; `~/.ext` wrapper handles token + macOS SSL) or the Extruct
MCP. This doc is the concrete command workflow plus the failure modes proven on the Nestlé run.

## 0. Account + access (do this FIRST)
```
~/.ext auth user                      # MUST be the project account (danny@extruct.ai). NOT another org.
~/.ext healthcheck                    # if auth ok but cells never process, it is a processing wedge, not creds
```
The CLI reads the repo `.env` token; the MCP uses whatever account it is OAuthed to — they can differ.
If the MCP is on the wrong org, either reconnect it (`/mcp`) or use the CLI.

## 1. Create the table + row, WARM the profile
```
~/.ext tables create --payload '{"name":"<Company> — account-research-extruct","kind":"company"}'
~/.ext rows create <table_id> --payload '{"rows":[{"data":{"input":"<region-domain>"}}],"run":false}'
~/.ext ... lookup_company_profile <region-domain>   # WARM the cache — critical
```
**Profile-resolution is the fragile step.** The auto `company_profile` / `company_name` / `company_website`
cells can sit in `requested` for a long time (seen: ~30 min, 0 cells, healthcheck ok). The research
columns depend on `company_name`+`company_website`, so a wedged profile blocks everything.
Mitigations, in order:
1. Call `lookup_company_profile <domain>` right after creating the row (warms the cache; on one account
   the row resolved in seconds after this; on another it stayed wedged).
2. If still `requested` after ~5-10 min, **repoint the row to the parent/global domain** (e.g.
   `nestle.com.br` -> `nestle.com`) and re-run — the global entity usually resolves faster. The column
   prompts stay region-scoped, so the output is still in-region.
3. If a whole-table run stays 0/N across re-runs, the account's enrichment is wedged server-side. STOP
   and tell the user (nudge it in the UI, retry later, or rebuild a fresh table). Do not fake it.

## 2. Atomic columns (one narrow job each)
Add via `columns add <table_id> --payload-file cols.json`. Use `research_pro` (company tables), one
column per layer. Bake the SELLER CONTEXT + REGION FOCUS into every prompt. Example column config:
```json
{ "kind":"agent", "name":"Open roles (Brazil)", "key":"open_roles",
  "value":{ "agent_type":"research_pro", "output_format":"text",
    "prompt":"Atomic task. List current OPEN positions <company> is hiring in <region>... and whether each requires English/another language, with a rough share. Cite the careers source." } }
```
Run only the new columns, then poll:
```
~/.ext tables run <table_id> --payload '{"mode":"new","columns":["<id1>","<id2>",...]}'
~/.ext tables poll <table_id>          # blocks until done/failed (may be backgrounded; re-read after)
~/.ext tables data <table_id> --limit 1 --columns <key1>,<key2>,...
```
Read the cell `answer` (and `sources`, `explanation`) per column.

## 3. People + email
```
# people finder column on the company table:
{ "kind":"company_people_finder", "name":"<region> buyers", "key":"buyers",
  "value":{ "roles":["Head of HR <region>","HRBP <region>","L&D lead <region>", ...], "max_results":8 } }
# run it, poll, then find the child people table:
~/.ext tables get <table_id>           # child_relationships -> child people table_id
# on the child: add email_finder, run, read
```
Drop people whose email resolves to a non-target domain — the finder returns role-matches who have
moved; the email is the current-employer gate. (Seen: 4 of 8 "Nestlé" matches were at other companies.)

## 4. Assemble the dashboard
Map cells -> the `accounts/{slug}.js` globals in [output-shape.md](output-shape.md). In particular:
- open/closed roles -> `window.JOBS` (each `{id,title,category,market,status,firstSeen,lastSeen,url,
  english?,desc?}`) + `window.JOBS_META` (`active`, `closed`, `csByMarket` flat `{MKT:n}`, `subtitle`,
  `note`). The Jobs tab (src/JobsTab.jsx) renders these and only appears when `window.JOBS` is non-empty;
  it shows `j.desc` + an `EN/lang` badge when `j.english`.
- tech -> `window.TECH`; news/leadership/lang-requirement -> `window.SIGNALS`; buyers -> `window.PEOPLE`
  + `window.TEAM_MEMBERS`.
Then `node scripts/build_accounts_index.js` and verify (node --check, integrity, helpers build, serve).

## Benchmark expectation (vs the original account-research)
The Extruct harness is strong on narrative synthesis (e.g. AI-adoption summaries) but weak on the
structured spine. Proven deltas on Nestlé (research_pro columns vs PredictLeads+Apollo baseline):
- open positions: ~1 role found vs 1,086 enumerated
- closed positions: none vs ~9,968
- tech / L&D stack: "not found" vs 882 detections (incl. Articulate Storyline)
- news/leadership: "not found" vs overhaul/layoffs/hiring/leadership reset
- named buyers: `[]` vs 8 found / 4 verified with emails
- language requirement: could not quantify (and self-contradicted 0% vs "preferred") vs ~43% measured
Record what each column actually returns; the gap IS the result. Do not pad to match the baseline.
