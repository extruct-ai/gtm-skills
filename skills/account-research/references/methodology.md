# Account Research — methodology

How to turn Extruct cells into a decision-ready dossier. The step-by-step workflow lives in SKILL.md; this is the reasoning behind it.

## Entity resolution (why it leads)

The hard, defensible step. A flat database returns one record per company; an account that is a holding group, a franchise network, or a multi-region entity is really a tree of many legal entities. Resolving it — parent → divisions → operating units, deduped, with a verified count of legal entities and countries — defines the real buying surface. Every operating unit beneath the parent is a separate buyer; one logo can be dozens of conversations.

Use the `entity_structure` column to resolve the tree, then carry the operating-unit domains into people discovery so you find the owner in each unit, not just at the parent.

## Linking signals to buyers — the tier model

A signal alone is dead weight; a signal tagged to the person who owns the decision is a wedge.

| Tier | Method | Confidence |
|------|--------|------------|
| Tier 1 — named in source | the person is the author, quoted, or referenced in the signal source | high |
| Tier 2 — aligned by function | same function, operating unit, and seniority as the signal | medium |
| Tier 3 — inferred | reasoned over the people pool; ranked candidates with a rationale | medium-low |

Record each link as `{person, signal, tier, rationale}`. Multiple tiers co-tagging the same person-signal pair is the strongest case.

## Entry angles (doors)

Cluster the linked signals into a few entry narratives. Each angle must have:

- a one-line functional thesis (not "we sell X to Y")
- at least one named owner in that buying unit
- two or more backing signals (not one anecdote)
- a first move

Cap at about four. A fifth pattern is usually a time-bound flag (a deadline), not a durable angle.

## Dossier shape

Write to `claude-code-gtm/accounts/{slug}/`:

- `overview.md` — what they do; the resolved entity tree; the footprint
- `buyer-map.md` — decision-makers by buying unit; the angle per person
- `signals.md` — dated, sourced events and what each implies
- `account-brief.md` — the distilled brief: the angle, the people, the why-now

Also emit a CRM-syncable map (companies + people + signals) for `campaign-sending` or the CRM. A visual dashboard is optional and out of scope for this skill.

## Quality bar

- Every figure carries its source. Confidence-gate over guessing.
- Read the actual cells; never report from memory.
- If a required Extruct stage is wedged, stop and say so; don't backfill with web search or fabricate.
- A smaller, fully-sourced dossier beats a padded one.
