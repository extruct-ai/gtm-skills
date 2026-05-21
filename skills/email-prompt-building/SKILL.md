---
name: email-prompt-building
description: >
  Design a cold-outreach email sequence as a FIXED TEMPLATE SET — real,
  human-approved copy with {{input_field}} placeholders and variant-routing
  rules. Reads the company context file and campaign research, explores
  angles, and commits to copy at design time. The output is rendered later by
  the email-generation skill via deterministic substitution — no per-row LLM.
  Triggers on: "cold email", "outreach prompt", "email campaign", "new
  vertical email", "draft email prompt", "email sequence", "email template".
---

# Cold Email Template Builder

Design a cold-outreach sequence and commit it to a **fixed template set**: the actual approved copy for every touch, with `{{input_field}}` placeholders and variant-routing rules. This skill does the thinking — explore angles, form pain hypotheses, decide the sequence arc, pick proof points — and bakes the result into final copy.

The template is rendered later by `email-generation` via plain deterministic substitution. There is **no runtime LLM** writing emails per row.

## Architectural Principle

**This skill is design-time. It commits to copy; it does not defer decisions to a runtime model.**

Older versions of this skill emitted an *LLM instruction prompt* and let a per-row model write each email. That is retired. Per-row variance is now expressed two ways only: (1) `{{input_fields}}` filled upstream, (2) discrete variant templates selected by a routing key. Everything else is identical across the batch.

```
                       DESIGN TIME (this skill)
                       ┌─────────────────────────────────────┐
context file ─────────▶│  explore angles, pick hypotheses,    │
research / hypotheses ▶│  decide sequence arc, choose proof   │──▶ template set (sequence.md)
enrichment field list ▶│  → commit to FINAL COPY              │     • real copy per touch
                       └─────────────────────────────────────┘     • {{input_field}} placeholders
                                                                    • variant-routing rules
                                                                    • Input Fields contract

                       FILL TIME (normalization + enrichment skills)
                         contacts ─▶ populate every declared input field

                       RENDER TIME (email-generation skill)
                         template + filled CSV ─▶ deterministic render ─▶ emails CSV
```

## What This Skill Reads (inputs)

All inputs live in the GTM project this skill is invoked on (paths are
project-relative; the exact layout is the project's, not this skill's).

| Input | What to extract |
|-------|-----------------|
| Company context file | Voice, sender, value prop, proof library, key numbers, banned words |
| Campaign research | Verified data points, statistics, tool comparisons |
| Hypothesis set | Numbered hypotheses with mechanisms and evidence |
| Enrichment field list | Which `{{input_fields}}` will be available, and from which enrichment/normalization step |
| Campaign brief | Target vertical, role types, sequence length |

## What This Skill Produces (output)

A **template set** — one sequence file per campaign — containing:

1. **Sequence overview** — touches, send cadence, the variable list
2. **Per-touch copy** — the FINAL approved text of each email, verbatim, with `{{input_field}}` placeholders inline. Not rules for writing it — the actual words.
3. **Variant-routing rules** — when a touch has variants, the routing key and the condition for each (e.g. `Touch 3: segment == "enterprise" → variant A, else → variant B`)
4. **Input Fields contract** (see below) — every `{{field}}`, its source, and its fallback
5. **Subject lines** — first touch only; follow-ups use empty subject to thread
6. **Notes** — why each angle was chosen, voice rules applied, what was deliberately excluded

See [references/example-sequence.md](references/example-sequence.md) for the worked output shape.

### The Input Fields contract

Every `{{placeholder}}` in the template MUST be declared in a table — this is the handshake with the fill + render steps. A render fails loudly if a declared field is missing; an *undeclared* placeholder is a bug. Describe each source by its **role** (a normalization step, a classification enrichment column), not by a file path in any specific project.

| Field | Source (by role) | Fallback if missing |
|-------|------------------|---------------------|
| `{{first_name}}` | name-normalization step | skip the contact |
| `{{company_name}}` | name-normalization step | skip the contact |
| `{{industry}}` | industry-classification enrichment column | drop the clause that uses it (provide a no-`{{industry}}` variant) |
| `{{segment}}` (routing key) | segment-classification enrichment column | route to the default variant |

If a field needs genuine per-row writing (e.g. a bespoke one-line opener), it is still an input field — produced by an **LLM enrichment column** upstream, not by this skill and not at render time.

## Building a Campaign Template Set

### Step 1: Read upstream data

Read the project's company context file, campaign research, and hypothesis set.

Also confirm the **enrichment field list** — which `{{input_fields}}` will actually be available, and from which enrichment/normalization step. Only use fields you can guarantee will be filled.

**Check persona spread.** If the contact list spans multiple personas (executives + ICs + ops), build a separate template set per role cluster. One template trying to serve all roles produces mush.

### Step 2: Explore angles, then commit to copy

This is the real work. There is no runtime model to "figure it out per row" — this skill must commit.

- For each hypothesis, work out the sharpest way to land the pain. Explore several angles.
- **Map angles onto the sequence**: each strong angle becomes a *touch* (Touch 1 = angle A, Touch 2 = angle B, …) or a *variant* of a touch. Multi-touch sequences let you take the problem from several angles without cramming.
- Write the FINAL copy for each touch. Actual sentences, not "write a P1 about X."
- Apply voice rules from the context file (tone, constraints, banned words). Do not invent voice.
- Place `{{input_field}}` placeholders only where per-row substitution is genuinely needed. Everything else is fixed copy.

### Step 3: Define variants and routing

When a touch should differ by segment/persona, write each variant as **separate, complete copy** — never one template with "if enterprise, say X" conditionals. Declare the routing key and the condition per variant. Keep variants few (2-3); each is a full email.

### Step 4: Write the Input Fields contract

Declare every `{{field}}` per the table above — source and fallback. A field with no reliable source is not allowed in the template; either add an enrichment step that produces it, or cut the clause.

### Step 5: Assemble the sequence file

```markdown
# Sequence — {campaign}

[overview: touches, cadence, variables]

## Touch 1 — {angle}
[FINAL copy with {{placeholders}}]
**Subject options:** [first touch only]

## Touch 2 — {angle}
[FINAL copy]  **Subject:** empty (threads as Re:)

## Touch 3 — conditional on {{routing_key}}
### Variant A — {condition}
[FINAL copy]
### Variant B — {condition}
[FINAL copy]

## Input Fields contract
[the declared-fields table]

## Notes
[angle rationale, voice rules, what was excluded]
```

### Step 6: Quality check

- [ ] Every touch is final copy, not instructions
- [ ] Every `{{placeholder}}` is declared in the Input Fields contract with a source + fallback
- [ ] No undeclared placeholders; no `{{field}}` whose source can't be guaranteed
- [ ] Variants are complete separate copy, not conditionals inside one template
- [ ] Follow-up touches have empty subject (thread continuation)
- [ ] Voice rules + banned words come from the context file
- [ ] Formatting rules respected: no signature, `--` not `–`/`—`, English only
- [ ] Framing rules respected: never "we help {{industry}} teams", never describe the prospect's company, never "We're {Company}"
- [ ] Anti-patterns below are not present in any touch

### Step 7: Save

Save the template set as the campaign's sequence file, in whatever location
the GTM project uses for campaign assets (one sequence file per campaign).

## Anti-patterns — what NOT to write into any touch

1. **Never repeat the prospect's own info back to them.** Don't paraphrase their headline or restate what their product does. They know. It signals a scrape with nothing to say.
2. **Never explain their business to them.** If they live it daily, skip it.
3. **No architecture jargon.** No "three-tier", "entity resolution", "data mesh". Copy is about outcomes, not internals.
4. **One question per email.** Two questions compete and neither gets answered.
5. **Readable on first pass.** No nested clauses, no stacked qualifiers. If a sentence needs a second read, rewrite it shorter.
6. **Openers must be legible at first glance.** No white-paper-title noun phrases ("the X gap").
7. **Don't paraphrase user-pasted copy.** If the user hands you a hook, use it verbatim.

## Sequence shape (defaults)

Touches take the problem from different angles, escalating from soft to direct:
- **Touch 1** — congrats / context hook + the core inherited pain + soft CTA
- **Touch 2** — a sharper proof or benchmark angle + give-a-doc CTA
- **Touch 3** — a segment-specific angle (route by `{{customer_segment}}`)
- **Touch 4** — short "goodbye" / breakup note

Cadence default: 2 days after Touch 1, 3 days between later touches. Override per campaign.

## References

- [references/example-sequence.md](references/example-sequence.md) — worked template set (the output shape)
- [references/prompt-patterns.md](references/prompt-patterns.md) — copy patterns distilled from past campaigns
- [references/email-structures.md](references/email-structures.md) — structural variants by role/seniority
