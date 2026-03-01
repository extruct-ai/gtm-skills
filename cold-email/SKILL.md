---
name: cold-email
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
| Enrichment columns | CSV headers from table-enrichment output | Field names and what they contain |
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

**P2 → from context file → What We Do:**
- Read the product description, email-safe value prop, and key numbers.
- Reason about which value angle matters for THIS audience and THIS hypothesis.
- Write 2-3 hypothesis-matched value angles with the reasoning embedded.
- Use the email-safe value prop, not the raw version (avoid banned words).
- Include example queries built from the audience's verticals.

**P4 → from context file → Proof Library:**
- Select 2-3 proof points that match this campaign's audience.
- For each, write the condition: when to use it, which hypothesis it validates, which role type it resonates with, and WHY.
- Do NOT include proof points from unrelated audiences.

**Banned phrasing → from context file + campaign-specific:**
- Start with banned words from context file → Voice.
- Add any campaign-specific banned phrases discovered during generation or copy-feedback.

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

## Structure (strict)
[Word limits, paragraph rules]

P1 — [Rules referencing hypotheses and enrichment fields]
P2 — [Synthesized value angles per hypothesis. Key numbers from context.
      Example queries per sub-vertical.]
P3 — [CTA rules with campaign-specific examples]
P4 — [2-3 proof points from Proof Library with conditions and reasoning]

## Output format
[JSON keys]

## Banned phrasing
[From context → Voice + campaign additions]
```

### Step 4: Self-containment check

Before saving, verify:
- [ ] Voice rules come from context file, not hardcoded in this skill
- [ ] P2 uses product description and numbers from context file
- [ ] P4 uses proof points from the Proof Library, matched to this campaign's audience
- [ ] Research data is embedded with actual numbers, not "use the research data"
- [ ] No references to external files — the email-generation skill only needs this prompt + CSV
- [ ] Banned words from context file are included in the banned phrasing section

### Step 5: Save

```
claude-code-gtm/prompts/{vertical-slug}/en_first_email.md
claude-code-gtm/prompts/{vertical-slug}/en_follow_up_email.md  (if follow-up needed)
```

## Email Structure (defaults)

These are sensible defaults. Override from context file or user input.

### First Email
- 4 paragraphs, ≤120 words total
- Greeting on its own line
- P1: sector-specific opener (≤16 words for key line)
- P2: product value + example query (1-2 sentences)
- P3: soft CTA — concrete sample, not a meeting (1 sentence)
- P4: proof/PS — case study from a peer (1 sentence)

### Follow-up Email
- 2 paragraphs, ≤60 words total
- P1: case study + capability + example
- P2: sector-shaped CTA (different angle from first email)

## Reference

See [references/prompt-patterns.md](references/prompt-patterns.md) for patterns distilled from past campaigns.
