# Context File Schema

Template for `claude-code-gtm/context/{company}_context.md`. Copy and fill in.

```markdown
# Company Context

## What We Do

**Product:** [One-liner description]

**Value prop:** [Core value proposition in 1-2 sentences]

**Email-safe value prop:** [Same value prop rewritten without any banned words from voice rules. This version gets baked into prompt templates.]

**Key lingo:**
- [Term 1]: [definition — how we use it internally]
- [Term 2]: [definition]

**Key numbers:** [quantifiable claims about the product — e.g., database size, speed benchmarks, coverage stats. These get used in P2 of emails.]

---

## Voice

**Sender:** [Name and company — who the emails come from]

**Tone:** [e.g., "Calm, analytical, builder-to-builder." Keep to 1 sentence.]

**Language level:** [e.g., "B2 English: simple, clear sentences. Polite but not over-polite."]

**Hard constraints:**
- [Rule 1 — e.g., "No dashes, no exclamation marks, no emojis."]
- [Rule 2 — e.g., "No buzzwords, no flattery, no hype."]
- [Rule 3 — e.g., "Sentence case only."]
- [Add as many as needed]

**Banned words:** [Words that must never appear in outreach — e.g., "agents", "try"]

**Scope boundaries:** [What the product IS and ISN'T — e.g., "Company-level intelligence, not people/panel data."]

---

## ICP

### Primary profiles

| Profile | Company size | Roles | Geographies | Why they buy |
|---------|-------------|-------|-------------|--------------|
| [Profile 1] | [range] | [titles] | [regions] | [reason] |
| [Profile 2] | [range] | [titles] | [regions] | [reason] |

### Anti-patterns (who is NOT a fit)

- [Description of companies that look like ICP but aren't]

---

## Win Cases

| Customer | Profile | What worked | Result | Date |
|----------|---------|------------|--------|------|
| [Name/anon] | [profile type] | [what resonated] | [concrete outcome] | [YYYY-MM] |

### Quotes / signals from wins

- "[Direct quote or paraphrase from customer]" — [context]

---

## Proof Library

Pre-written proof point sentences for use in P4 of emails. Each entry has the sentence, the audience it works for, and the hypothesis it validates.

| Proof point | Best for audience | Best for hypothesis | Source win case |
|-------------|-------------------|--------------------|----|
| "[Full PS sentence ready to paste into an email]" | [audience type] | [hypothesis name or "general"] | [win case reference] |
| "[Another proof point]" | [audience type] | [hypothesis name] | [win case reference] |

Rules:
- Every proof point must trace back to a real win case above.
- Write the full sentence as it would appear in the email (including "PS.").
- When building a campaign prompt, pick 2-3 proof points that match the campaign audience and bake them into the prompt template with conditions for when to use each one.

---

## Campaign History

| Campaign | Vertical | List size | Reply rate | Top hypothesis | Key learning | Date |
|----------|----------|-----------|------------|---------------|--------------|------|
| [name] | [vertical] | [N] | [X%] | [#N name] | [1-sentence takeaway] | [YYYY-MM] |

---

## Active Hypotheses

### Validated (reply rate > X%)

1. **[Name]** — [2-3 sentence description with data points]. Best fit: [company type]

### Testing

1. **[Name]** — [description]. Best fit: [company type]

### Retired

1. **[Name]** — retired because [reason]. Last tested: [date]

---

## Do Not Contact

| Domain | Reason | Added |
|--------|--------|-------|
| [domain.com] | [competitor/partner/requested/other] | [YYYY-MM-DD] |
```

## Section Rules

- **What We Do**: Keep under 100 words. Update when positioning changes. Include email-safe version and key numbers.
- **Voice**: Defines the sender identity and tone for all outreach. Skills read this section to set the voice in prompt templates.
- **ICP**: Max 5 primary profiles. Anti-patterns prevent wasted outreach.
- **Win Cases**: Add every closed deal. Anonymous is fine ("a mid-market company in [industry]").
- **Proof Library**: Derived from win cases. Every proof point must map to a real win. Skills read this section when building P4 of prompt templates.
- **Campaign History**: One row per campaign. Update reply rate when final numbers are in.
- **Active Hypotheses**: Move between Validated/Testing/Retired based on campaign results. Target 5-7 active.
- **Do Not Contact**: Check before every list build and Instantly upload.
