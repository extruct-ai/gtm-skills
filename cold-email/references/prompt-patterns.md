# Prompt Patterns

Distilled patterns for building email prompt templates. These are structural patterns — fill in your own company, product, audience, and proof points from the context file.

## Pattern 1: Pain-Theme Segmentation

Map 3-5 pain themes from your hypothesis set, then branch P1 based on which theme fits each recipient.

**Structure:**
- Define pain themes (A, B, C...) from `market-problems-deep-research` output
- Map role types to themes (analysts → theme A, executives → theme B)
- P1 references the specific pain theme matched to the recipient
- P2 explains how your product addresses that theme

**When to use:** You have a hypothesis set with distinct pain points and enrichment data to match companies to themes.

---

## Pattern 2: Role-Based Emphasis

Vary the angle based on the recipient's seniority and function.

**Structure:**
- Analysts/researchers: emphasize precision, coverage, manual work reduction
- Directors/VPs: emphasize speed, cost discipline, cross-team visibility
- C-suite: emphasize strategic advantage, competitive edge, scale

**When to use:** Your list spans multiple seniority levels within the same vertical.

---

## Pattern 3: Post-Event Outreach

Use a shared event as the opener.

**Structure:**
- P1: Event reference + observation about a trend discussed at the event
- P2: Simple question about how they currently handle [relevant process]
- P3: Product explanation with concrete outcome
- P4: Soft CTA (no hard meeting ask)

**When to use:** After a conference, webinar, or industry event where your audience was present.

---

## Pattern 4: Multi-Email Sequence

First email + follow-up with different angles.

**Structure:**
- Email 1: Hypothesis-driven opener → product value → CTA → proof point
- Email 2 (follow-up): Different case study → different capability angle → sector-shaped CTA

**Rules:**
- Follow-up must use a different value angle than email 1
- Never say "quick follow-up" or "circling back"
- Follow-up is shorter (≤60 words vs ≤120)

---

## Cross-Campaign Defaults

These are starting points. Override per campaign as needed.

| Rule | Default |
|------|---------|
| Max words (first email) | 120 |
| Max words (follow-up) | 60 |
| Paragraphs (first email) | 4 |
| Paragraphs (follow-up) | 2 |
| Greeting format | "Hey {FirstName}," |
| Firm mentions | at most once |
| Sector naming | always explicit, never "sectors like yours" |
| Output format | JSON (keys: recipient_name, recipient_company, subject, greeting, first_paragraph...fourth_paragraph) |
| Input | CSV row passed as JSON |
| Prompt location | `claude-code-gtm/prompts/{vertical-slug}/` |

## Building Your Own Patterns

After running 2-3 campaigns, distill what worked:

1. Export campaign results from Instantly
2. Identify which P1 angles got replies
3. Note which proof points resonated
4. Add the pattern here with the audience, structure, and key phrases that worked

Keep this file as a living reference. Delete patterns that stop working.
