---
name: account-research
description: >
  Deep-research a single target account into a decision-ready dossier: resolve its
  parent-subsidiary entity tree, map the buying units and decision-makers, mine live
  signals (open roles, leadership moves, news, tech stack), and link signals to buyers
  with an entry angle. Extruct-powered; delegates people discovery to people-search.
  Use to prep for a sales conversation, build a buyer map, find who to sell to at a
  company, or surface why-now signals for ONE account (not a list).
  Triggers on: "research this account", "account research", "buyer map",
  "who do we sell to at", "prep for the meeting with", "deep dive on", "map the org at",
  "find decision makers at", "why now at", "research [company] before the call".
---

# Account Research

Turn one target company domain into a decision-ready dossier: the resolved entity tree, the buyers across every buying unit, the live signals, and the angle to enter on. Breadth lists come from `list-building`; this skill goes deep on a single account.

## Related Skills

```
list-segmentation → account-research → people-search → email-search → campaign-sending
                                     → list-enrichment (custom data points on the tree)
```

Reads the company context file for ICP and target roles. Hands a buyer map plus signals to the outreach skills.

## Extruct API Operations

This skill delegates all Extruct API calls to the `extruct-api` skill. People discovery is delegated to the `people-search` skill, and email/phone enrichment to `email-search`.

Read and follow `extruct-api` for table creation, column creation, enrichment runs, and data fetching. This skill decides **what to resolve, what to mine, and how to assemble the dossier**.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Target account domain | User provides | yes |
| Company context file | `claude-code-gtm/context/{company}_context.md` (ICP, target roles, proof) | no (sharpens targeting) |
| Region / segment focus | User choice | no |

## Workflow

### Step 1: Anchor the account

Delegate to `extruct-api`: create a company table, add the target domain as one row, and let it resolve `company_profile` / `company_name` / `company_website`. Warm the profile before adding research columns — profile resolution is the slow step and the research columns depend on it.

For a large group, anchor on the parent domain; the entity tree in Step 2 expands it.

### Step 2: Resolve the entity tree (the differentiator)

Standard databases return one flat record. The real account is often a tree of many legal entities. Add a `research_pro` column that resolves the **parent-subsidiary / org-chart structure**: the holding entity, its divisions or networks, the operating units beneath them, and a verified count of legal entities and countries.

Output: the resolved hierarchy (parent → children, counts, source per node). This is what no flat database gives you, and it defines the real buying surface. See the `entity_structure` config in [references/column-library.md](references/column-library.md).

### Step 3: Mine the account signals

Add atomic, single-job `research_pro` columns — one per signal layer, never one mega-prompt. Bake the ICP / target roles (from the context file) and the region focus into each prompt. The standard set:

| Column | Mines |
|--------|-------|
| `open_roles` | current open positions in-region and what they reveal about where budget is moving |
| `closed_roles` | recently filled or closed positions — where headcount actually grew, and the team's hiring throughput |
| `leadership_changes` | recent hires, departures, promotions in the target functions (the buying-window signal) |
| `recent_news` | dated events: M&A, rebrands, launches, partnerships, funding |
| `tech_stack` | the CRM and the incumbent tooling the offer sits beside |
| `division_focus` | what each division / operating unit is currently prioritizing |

Add ICP-specific columns designed with `enrichment-design` if the context file calls for them. Run only the new columns via `extruct-api`, then poll to completion and read. Configs in [references/column-library.md](references/column-library.md).

### Step 4: Find the buyers

Delegate to the `people-search` skill to find decision-makers in the target functions (from the context file) **across the resolved entities**, not just the parent — each buying unit has its own owner. Search the operating-unit domains surfaced in Step 2.

Drop anyone whose current employer resolves off-target. Optionally enrich emails and phones via `email-search`.

### Step 5: Link signals to buyers, then form the entry angle

Tag each signal to the people who own that decision using the tier model in [references/methodology.md](references/methodology.md). Then cluster the linked signals into a small number of **entry angles** — each a one-line thesis, a named owner, two or more backing signals, and a first move. Cap at about four; a fifth pattern is usually a time-bound flag, not a durable angle.

### Step 6: Assemble the dossier

Write findings to `claude-code-gtm/accounts/{slug}/`:

- `overview.md` — what they do, the resolved entity tree, the footprint
- `buyer-map.md` — decision-makers by buying unit, with the angle per person
- `signals.md` — dated, sourced events and what each implies
- `account-brief.md` — the distilled brief: the angle, the people, the why-now

Emit a CRM-syncable account map (companies + people + signals) to hand to `campaign-sending` or the CRM. A visual dashboard is **out of scope** for this skill; the dossier is the deliverable.

## Ground Rules

- **Extruct is the engine.** Company facts, entity resolution, and every signal come from Extruct `research_pro` columns. Job changes, open positions, tech, and news are all covered by Extruct — don't reach for a separate signal vendor.
- **Source every claim.** Each figure carries its source; confidence-gate over guessing. Never fabricate to fill the dossier — a smaller, fully-sourced result beats a padded one.
- **Verify before claiming.** Read the actual cells; don't report from memory. If a required Extruct stage is wedged, stop and say so rather than backfilling with web search.
- **Stay vertical-agnostic.** Read who and what to target from the context file; don't assume an industry.

## Reference

- [references/column-library.md](references/column-library.md) — `research_pro` column configs for the entity tree and each signal layer.
- [references/methodology.md](references/methodology.md) — entity-resolution approach, the tier model for linking signals to buyers, and the dossier shape.
