---
name: email-prompt-building
description: >
  Generate self-contained email prompt templates for cold outreach campaigns.
  Reads from the company context file (voice, value prop, proof points) and
  campaign research (hypotheses, data points) to produce a prompt that the
  email-generation skill runs per-row against a contact CSV. One prompt per
  campaign. Triggers on: "cold email", "outreach prompt", "email campaign",
  "new vertical email", "draft email prompt", "email sequence".
---

# Cold Email Prompt Builder

Generate self-contained prompt templates for cold outreach campaigns. Each prompt encodes everything the email generator needs: voice, research data, value prop, proof points, and personalization rules. No external file references at runtime.

## Architectural Principle

**This skill is a generator, not a template.** It reads the company context file and campaign research, reasons about what fits this specific audience, and produces a self-contained prompt. Each campaign gets its own prompt. Each company gets its own context file. Nothing is hardcoded in this skill.

```
                          BUILD TIME (this skill)
                          ┌─────────────────────────────────────┐
context file ────────────▶│                                     │
research / hypothesis ───▶│  Synthesize into self-contained     │──▶ prompt template (.md)
enrichment column list ──▶│  prompt with reasoning baked in     │
                          └─────────────────────────────────────┘

                          RUN TIME (email-generation skill)
                          ┌─────────────────────────────────────┐
prompt template (.md) ───▶│                                     │
contact CSV ─────────────▶│  Generate emails per row            │──▶ emails CSV
                          └─────────────────────────────────────┘
```

## What This Skill Reads (inputs)

| Input | Source | What to extract |
|-------|--------|-----------------|
| Context file | `claude-code-gtm/context/{company}_context.md` | Voice, sender, value prop, proof library, key numbers, banned words |
| Research | `claude-code-gtm/context/{vertical-slug}/sourcing_research.md` | Verified data points, statistics, tool comparisons |
| Hypothesis set | `claude-code-gtm/context/{vertical-slug}/hypothesis_set.md` | Numbered hypotheses with mechanisms and evidence |
| Enrichment columns | CSV headers from list-enrichment output | Field names and what they contain |
| Campaign brief | User describes audience, roles, goals | Target vertical, role types, campaign angle |

## What This Skill Produces (output)

A single `.md` file at `claude-code-gtm/prompts/{vertical-slug}/en_first_email.md` containing:

1. **Role line** — who the LLM acts as (from context file → Voice → Sender)
2. **Core pain** — why this audience has this problem (from research, not generic)
3. **Voice rules** — tone, constraints, banned words (from context file → Voice)
4. **Research context** — verified data points embedded directly (from sourcing_research.md)
5. **Enrichment data fields** — table mapping each CSV column to how to use it
6. **Hypothesis-based P1 rules** — rich descriptions with research data, mechanisms, evidence
7. **P2 value angle** — synthesized from context file → What We Do, adapted per hypothesis
8. **P3 CTA rules** — campaign-specific examples
9. **P4 proof points** — selected from context file → Proof Library, with conditions for when to use each
10. **Output format** — JSON keys, word limits
11. **Banned phrasing** — from context file → Voice → Banned words + campaign-specific additions

## Building a Campaign Prompt

### Step 1: Read upstream data

Read these files before writing anything:

```
claude-code-gtm/context/{company}_context.md
claude-code-gtm/context/{vertical-slug}/sourcing_research.md
claude-code-gtm/context/{vertical-slug}/hypothesis_set.md
```

**Also read the contact CSV headers.** Before writing any prompt rules, check which enrichment fields actually exist in the CSV. Only reference fields that are present. If the prompt needs a field that isn't there, either ask the user to add it via enrichment or drop that rule.

**Check persona spread.** If the contact list spans multiple personas (e.g., executives + ICs + ops), recommend splitting into separate prompts per role cluster. One prompt trying to handle all roles produces generic output. Flag this to the user before proceeding.

### Step 2: Synthesize (the reasoning step)

This is where the skill does real work. For each section of the prompt:

**Voice → from context file:**
- Read `## Voice` section. Copy sender name, tone, constraints, banned words into the prompt.
- Do NOT invent voice rules. If the context file doesn't have them, ask the user.

**P1 → from research + hypotheses:**
- For each hypothesis in the campaign, write a rich description using data points from the research.
- Explain the MECHANISM (why this pain exists), not just the symptom.
- Include specific numbers from the research (coverage percentages, decay rates, time costs).
- Write P1 rules that reference enrichment fields by name.
- NEVER use generic framing like "scores suppliers" or "manages vendors." Use the `platform_type` enrichment field or derive the actual description from the company profile. If the enrichment data doesn't include `platform_type`, instruct the generator to describe what the company actually does based on its description.

**Competitive awareness rules (embed in P1/P2):**
- If enrichment data or research reveals the prospect company has an existing capability that overlaps with your product:
  1. NEVER pitch as a replacement. Position as a data layer underneath.
  2. Acknowledge their existing tool by name in P1.
  3. Shift P2 from "here's what we do" to "here's what we add to what you already do."
  4. If the prospect FOUNDED a competing product (career history), either:
     a. Use Variant D (peer founder) and reference shared context, OR
     b. Deprioritize. Flag to user as "risky send, needs manual review."

**P2 → from context file → What We Do:**
- Read the product description, email-safe value prop, and key numbers.
- Reason about which value angle matters for THIS audience and THIS hypothesis.
- Write 2-3 hypothesis-matched value angles with the reasoning embedded.
- Use the email-safe value prop, not the raw version (avoid banned words).
- **P2 simplicity check — enforce before saving:**
  - One idea per sentence. No compound lists.
  - No architecture descriptions. No implementation jargon (see Anti-patterns #3).
  - If a sentence has more than two commas, split it into separate sentences.
  - Read P2 aloud. If any sentence requires a second read, rewrite it shorter.
  - Bad: "We aggregate 100M+ records from trade registries, customs filings, and corporate databases, enabling teams to run queries like 'packaging suppliers in DACH under €50M' and get matched results in seconds."
  - Good: "We track 100M+ companies across trade registries and customs filings. Your team can search something like 'packaging suppliers in DACH under €50M' and get results in seconds."
- Example query rules:
  - The example query MUST reference a vertical or category the prospect's platform actually serves. Use enrichment data or company description.
  - NEVER reuse the same example query across different prospects.
  - Format: "{category} in {geography} under {size constraint}"

**P4 → from context file → Proof Library:**

Select proof points based on THREE dimensions:

| Dimension | Logic |
|-----------|-------|
| **Peer relevance** | Proof company should be same size or larger than prospect. Never cite a smaller company as proof to a bigger one. |
| **Hypothesis alignment** | Proof point should validate the same hypothesis used in P1. |
| **Non-redundancy** | If a stat appears in P2, do NOT repeat it in P4. |

If no proof point meets all three criteria, drop P4 entirely (use a shorter structural variant instead).

**Banned phrasing → from context file + campaign-specific:**
- Start with banned words from context file → Voice.
- Add any campaign-specific banned phrases discovered during generation or email-response-simulation.

### Step 3: Assemble the prompt

Write the `.md` file following this skeleton:

```markdown
[Role line from context → Voice → Sender]

[Core pain — 2-3 sentences from research. Not generic.]

## Hard constraints
[From context → Voice. Copied verbatim.]

## Research context
[Verified data points from sourcing_research.md. Actual numbers, tool names,
coverage gaps. This is the foundation for P1.]

## Enrichment data fields
[Table: field name → what it tells you → how to use it in the email]

## Hypothesis-based P1
[Per hypothesis: mechanism, evidence, usage rules.
All grounded in research data.]

## Role-based emphasis
[Map role keywords → emphasis. Use specific data points.]

## Structural variants
[Select variant per recipient based on role + seniority from enrichment data.
See "Structural Variants" section below for definitions.]

## Competitive awareness
[Rules for handling prospects with overlapping capabilities.]

## Proof point selection
[Three-dimensional selection: peer relevance, hypothesis alignment, non-redundancy.]

## Example query rules
[Must reference prospect's actual vertical. Never reuse across prospects.]

P1 — [Rules referencing hypotheses and enrichment fields. Use actual platform description, not generic framing.]
P2 — [Synthesized value angles per hypothesis. Key numbers from context. Vertical-specific example queries.]
P3 — [CTA rules with campaign-specific examples]
P4 — [Proof points with conditions. Drop entirely if no proof meets all three criteria.]

## Subject line rules
[Subject references the prospect's problem, not your product. Never sound like
you're selling data or leads. No "boost your pipeline" or "better lead lists."
Frame around THEIR challenge: coverage gap, manual process, missed deals.]

## Output format
[JSON keys]

## Banned phrasing
[From context → Voice + campaign additions]

## Example emails
[Include 2-3 full example emails as demonstrations. Models follow examples
better than instructions. Each example should show a different structural
variant or hypothesis. Annotate each with which variant, hypothesis, and
enrichment fields it uses.]
```

### Anti-patterns — what NOT to do

Every generated prompt must include these rules verbatim. These are the most common ways cold emails fail:

1. **Never repeat the prospect's own info back to them.** Don't paraphrase their LinkedIn headline, restate their company description, or echo what their product does. They already know. It signals you scraped them and have nothing to say.
2. **Never explain their business to them.** Don't tell a CTO how three-tier architectures work. Don't tell a data vendor that data decays. If they live it daily, skip it.
3. **Never use architecture jargon in P2.** No "three-tier," "waterfall," "entity resolution," "microservices," "data mesh," or implementation-level terms. P2 is about outcomes, not internals. If a term wouldn't appear in a board deck, cut it.
4. **Never stack multiple questions.** One email, one question — max. Two questions compete for attention and neither gets answered. If you have a question in P1, P3's CTA must be a statement or offer, not another question.
5. **P2 must be readable on first pass.** If you have to read a sentence twice to understand it, rewrite it. No nested clauses, no stacked qualifiers, no "which enables X that drives Y resulting in Z" chains.

### Step 4: Self-containment check

Before saving, verify:
- [ ] Voice rules come from context file, not hardcoded in this skill
- [ ] Structural variants are defined with role-based selection logic
- [ ] P1 uses actual platform description, not generic framing
- [ ] P2 example queries reference the prospect's actual vertical, not a generic category
- [ ] P4 proof points pass all three selection criteria (peer relevance, hypothesis alignment, non-redundancy)
- [ ] Competitive awareness rules are included for prospects with overlapping capabilities
- [ ] Research data is embedded with actual numbers, not "use the research data"
- [ ] No references to external files — the email-generation skill only needs this prompt + CSV
- [ ] Banned words from context file are included in the banned phrasing section
- [ ] Every enrichment field referenced in the prompt actually exists in the CSV headers
- [ ] Subject line rules reference the prospect's problem, not your product
- [ ] At least 2 full example emails are included as demonstrations
- [ ] If contact list spans multiple personas, separate prompts were recommended

### Step 5: Save

```
claude-code-gtm/prompts/{vertical-slug}/en_first_email.md
claude-code-gtm/prompts/{vertical-slug}/en_follow_up_email.md  (if follow-up needed)
```

## Structural Variants

Select structure based on role + seniority from enrichment data. These are defaults. Override from context file or user input.

### Variant A: Technical Evaluator (CTO, VP Eng, Head of Data)
4 paragraphs, ≤120 words.
- P1: pain with concrete data point
- P2: product specs (API-first, pricing model, integration)
- P3: low-effort CTA (sample search, not a meeting)
- P4: peer proof point (PS)

### Variant B: Founder / CEO (small company, <50 people)
3 paragraphs, ≤90 words. No PS.
- P1: pain tied to their specific stage or market move
- P2: value + proof in one paragraph (merge P2+P4)
- P3: CTA

### Variant C: Executive / Chairman / Board (delegates decisions)
2-3 paragraphs, ≤70 words. Forwardable.
- P1: one sharp observation about their platform
- P2: one sentence value + CTA combined
- Optional P3: proof point only if it's a name they'd recognize

### Variant D: Peer Founder (built something adjacent or competing)
2 paragraphs, ≤60 words. Peer-to-peer tone.
- P1: acknowledge shared context, state the angle without explaining basics
- P2: specific offer, no product pitch

### Follow-up Email
- 2 paragraphs, ≤60 words total
- P1: case study + capability + example
- P2: sector-shaped CTA (different angle from first email)

## Reference

See [references/prompt-patterns.md](references/prompt-patterns.md) for patterns distilled from past campaigns.
