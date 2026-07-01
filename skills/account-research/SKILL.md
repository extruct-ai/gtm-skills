---
name: account-research
description: >
  Deep-research a single target account into a decision-ready dossier: the entity tree,
  the buying units and decision-makers, live signals (open/closed roles, leadership moves,
  news, tech stack), and the entry angle. Powered by Extruct Deep Research — ONE cited
  report per account, no table/column setup. Optionally enrich buyer emails via email-search.
  Use to prep for a sales conversation, build a buyer map, find who to sell to at a company,
  or surface why-now signals for ONE account (not a list).
  Triggers on: "research this account", "account research", "buyer map",
  "who do we sell to at", "prep for the meeting with", "deep dive on", "map the org at",
  "find decision makers at", "why now at", "research [company] before the call".
---

# Account Research

Turn one target company domain into a decision-ready dossier: the resolved entity tree, the buyers across every buying unit, the live signals, and the angle to enter on. Breadth lists come from `list-building`; this skill goes deep on a single account.

The engine is **Extruct Deep Research**: you write one brief describing the account and the decision it supports, Extruct runs 10/25/50 research agents over the web and its index, and returns a single fully-cited report. You assemble that report into the dossier. There is no table or column setup — one brief, one report.

## Related Skills

```
list-segmentation → account-research → email-search → campaign-sending
```

Reads the company context file for ICP and target roles. Hands a buyer map plus signals to the outreach skills. Optional email/phone enrichment is delegated to `email-search`.

## Engine

Extruct Deep Research API: `POST /v1/deep_research_tasks`. The endpoints, auth, depth levels, the poll gotcha, and the report shape are in **[references/deep-research-engine.md](references/deep-research-engine.md)** — read it first.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Target account domain | User provides | yes |
| Company context file | `claude-code-gtm/context/{company}_context.md` (ICP, target roles, proof) | no (sharpens targeting) |
| Region / segment focus | User choice | no |
| Depth (`medium` / `high` / `xhigh`) | User / account priority | no (default `high`) |

## Workflow

### Step 1: Confirm access
`~/.ext auth user` — must be the project account (`danny@extruct.ai` for extruct-research). Note `available_credits` (Deep Research bills 1 credit per executed agent, up to 50 at `xhigh`). Capture the slug (kebab-case), the seller, the region focus, and the decision the dossier must support — they all go into the brief.

### Step 2: Compose the brief
One `brief` string (<=20,000 chars) carries the seller context, the target, the decision, the region, and a numbered list of every layer the dossier needs. Bake in the ICP / target roles from the context file. Ask for a **source URL per claim** and to **flag low-confidence items and gaps**. Cover:

1. **Overview** — what they do, HQ, founding year, headcount, mission.
2. **Entity tree (the differentiator)** — parent → divisions / subsidiaries / operating units, deduped, with a verified count of legal entities and countries. A flat database shows one record; the real account is a tree, and every operating unit is a separate buyer.
3. **Numbers** — funding rounds (amount, date, investors), valuation, revenue/ARR + growth, customers/locations, retention. Reconcile disputed figures; label estimates.
4. **Signals** — current OPEN and recently FILLED roles in the target functions; leadership changes; dated news (M&A, launches, partnerships, funding, expansion); the tech stack (CRM + the incumbent tooling the offer sits beside); what each division is prioritizing.
5. **Decision-makers** — named buyers **across the entity tree, not just the parent**, in the target functions, with exact titles and LinkedIn URLs.
6. **Entry angle + honest verdict** — the buying committee, the wedge, a concrete first move, and an objective read on whether this is a strong fit (say so plainly even if it is weak).

### Step 3: Run it
Create the task at the chosen `depth`, then poll to `done` (in the background; mind the `strict=False` JSON gotcha). See the engine doc.

### Step 4: Assemble the dossier
Read `report.markdown` + `report.sources`. Tag each signal to the buyer who owns it with the tier model, then cluster the linked signals into <=4 entry angles — see [references/methodology.md](references/methodology.md). Write findings to `claude-code-gtm/accounts/{slug}/`:

- `overview.md` — what they do, the resolved entity tree, the footprint
- `buyer-map.md` — decision-makers by buying unit, with the angle per person
- `signals.md` — dated, sourced events and what each implies
- `account-brief.md` — the distilled brief: the angle, the people, the why-now

Save the raw cited report (`report.md` + `sources.md`) alongside as provenance. Emit a CRM-syncable account map (companies + people + signals) for `campaign-sending` or the CRM. **Keep the report's honest verdict** — do not inflate a weak-fit into a slam-dunk. A visual dashboard is out of scope; the dossier is the deliverable.

### Step 5: (Optional) enrich buyer emails
Delegate the named buyers to `email-search` for verified emails and phones. Drop anyone whose current employer resolves off-target.

## Ground Rules

- **Extruct is the engine.** The whole account — entity tree, signals, people, verdict — comes from one Deep Research report. Don't reach for a separate signal vendor.
- **Source every claim.** The report cites `[n]`; carry the source URL through to the dossier. Confidence-gate over guessing; keep single-source / low-confidence items labelled as such. Never fabricate to fill the dossier — a smaller, fully-sourced result beats a padded one.
- **Verify before claiming.** Read the actual report, not memory. If the task `failed`, or sits in `in_progress` with agent/source counts that never advance, STOP and say so rather than backfilling with web search.
- **Stay vertical-agnostic.** Read who and what to target from the context file; don't assume an industry.

## Reference

- [references/deep-research-engine.md](references/deep-research-engine.md) — the Extruct Deep Research API workflow (endpoints, depth levels, brief template, poll gotcha, report shape).
- [references/methodology.md](references/methodology.md) — the tier model for linking signals to buyers, entry-angle rules, and the dossier shape.
