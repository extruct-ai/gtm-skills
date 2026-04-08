# Prompt Patterns

Distilled patterns for building email prompt templates. These are structural patterns — fill in your own company, product, audience, and proof points from the context file.

## Pattern 1: Pain-Theme Segmentation

Map 3-5 pain themes from your hypothesis set, then branch P1 based on which theme fits each recipient.

**Structure:**
- Define pain themes (A, B, C...) from `market-research` output
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

## Pattern 4: Genuine Curiosity (Question-First P1)

Open with a real question derived from enrichment data — not a statement with a question mark bolted on.

**Structure:**
- P1 is a single question. The question must be:
  - Genuinely answerable (you don't already know the answer)
  - Grounded in something specific you observed in their enrichment data (job change, company growth, product launch, coverage gap)
  - NOT a restatement of their pain dressed as a question
- P2 is a short value bridge: what made you curious + what you do, in plain language
- P3 is a concrete CTA (sample, not a meeting)

**Bad examples (statement-first disguised as questions):**
- "Are you struggling with data coverage in APAC?" (you're telling them their pain)
- "Did you know that 40% of trade show contacts decay within 90 days?" (rhetorical)
- "Wouldn't it be great if you could search 100M+ companies?" (leading)

**Good examples (genuine curiosity):**
- "Your team added three APAC markets last year — are you sourcing those suppliers locally or from a central database?"
- "I saw you just launched a materials procurement vertical — how are you building the supplier directory for that?"
- "Noticed your platform covers DACH but not Nordics yet — is that a data availability issue or a demand priority call?"

**Key rule:** If you could answer your own question from the enrichment data, it's not genuine curiosity — it's a statement with a question mark. The question must ask about something you genuinely cannot see from the outside.

**When to use:** Best for senior prospects (VP+) and founders who ignore statement-first pitches. Works especially well when enrichment data reveals a recent move (expansion, product launch, hire) that creates a natural opening. Prefer this pattern over Pain-Theme for audiences that are self-aware about their pain and don't need it named.

---

## Pattern 5: Multi-Email Sequence

First email + follow-up with different angles.

**Structure:**
- Email 1: Hypothesis-driven opener → product value → CTA → proof point
- Email 2 (follow-up): Different case study → different capability angle → sector-shaped CTA

**Rules:**
- Follow-up must use a different value angle than email 1
- Never say "quick follow-up" or "circling back"
- Follow-up is shorter (≤60 words vs ≤120)

---

## Pattern 6: Structural Variants

Select email structure based on the recipient's role and seniority from enrichment data. Different personas need different formats.

**Variants:**

| Variant | Who | Paragraphs | Max words | Notes |
|---------|-----|------------|-----------|-------|
| A: Technical Evaluator | CTO, VP Eng, Head of Data | 4 (P1-P4) | 120 | Full structure with proof point PS |
| B: Founder / CEO | Small company (<50 people) | 3 (P1-P3) | 90 | Merge P2+P4, no separate PS |
| C: Executive / Board | Chairman, board member, delegates decisions | 2-3 | 70 | Forwardable, one sharp observation |
| D: Peer Founder | Built something adjacent or competing | 2 | 60 | Peer-to-peer tone, no product pitch |

**Selection logic:**
- Match on `job_title` or `seniority` from enrichment data
- If role is ambiguous, default to Variant A
- Follow-up emails are always 2 paragraphs, ≤60 words regardless of variant

**When to use:** Your list spans multiple seniority levels or includes both operators and executives. Especially important when the same campaign targets both technical evaluators and C-suite.

---

## Cross-Campaign Defaults

These are starting points. Override per campaign as needed.

| Rule | Default |
|------|---------|
| Max words (first email) | Varies by structural variant (60-120) |
| Max words (follow-up) | 60 |
| Paragraphs (first email) | Varies by structural variant (2-4) |
| Paragraphs (follow-up) | 2 |
| Greeting format | "Hey {FirstName}," |
| Firm mentions | at most once |
| Sector naming | always explicit, never "sectors like yours" |
| Output format | JSON (keys: recipient_name, recipient_company, subject, greeting, paragraphs per variant) |
| Input | CSV row passed as JSON |
| Prompt location | `claude-code-gtm/prompts/{vertical-slug}/` |

## Building Your Own Patterns

After running 2-3 campaigns, distill what worked:

1. Export campaign results from your email sequencer
2. Identify which P1 angles got replies
3. Note which proof points resonated
4. Add the pattern here with the audience, structure, and key phrases that worked

Keep this file as a living reference. Delete patterns that stop working.
