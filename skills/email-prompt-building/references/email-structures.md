# Email Structure Library

Pre-built email structures for the email-prompt-building skill. Pick one, customize it, or build your own from scratch. Each structure defines what goes in each paragraph, word limits, and when it works best.

## How to Use

1. Browse the structures below
2. Pick the one closest to your campaign goals
3. Customize paragraph definitions, word limits, or add/remove paragraphs
4. The email-prompt-building skill will synthesize content (voice, research, proof points) into the chosen structure

If none of these fit, define your own structure or paste an example email that worked in the past — the skill will reverse-engineer the structure from it.

---

## Structure: 4P-short

The default cold outreach structure. Proven on multiple campaigns.

```
Paragraphs: 4
Word limit: ≤120 total
Greeting: "Hey {FirstName}," on its own line

P1 — Sector-specific opener (≤16 words for key line)
     One crisp observation showing you understand THEIR work.
     Uses enrichment data and hypothesis to personalize.
     Natural opener: "Noticed...", "Saw...", "Heard from..."
     Names their sector explicitly.

P2 — Product value (1-2 sentences)
     Brief tool description + one concrete example query in quotes.
     Value angle matched to the hypothesis.
     Includes key number from context file.

P3 — Soft CTA (1 sentence)
     Concrete sample offer, not a meeting request.
     Uses their buyer type and region.
     Example: "Want me to run a sample list of [buyer] in [region]?"

P4 — Proof / PS (1 sentence)
     Case study from a peer company.
     Format: "PS. [Profile] used us to [concrete result]."
     Matched to hypothesis and audience.
```

**Best for:** First cold outreach to mid-level and senior prospects. Works well for product-led motions where you can show a concrete sample.

**Tested on:** PE roll-up sourcing, industrial tech CRM hygiene, market research firms.

---

## Structure: 3P-question

Shorter, question-led. Opens with a question that the recipient can answer from their own experience.

```
Paragraphs: 3
Word limit: ≤90 total
Greeting: "Hey {FirstName}," on its own line

P1 — Question opener (1-2 sentences)
     A specific question about their workflow or pain.
     Must be answerable — not rhetorical.
     Grounded in research data (not generic).
     Example: "How does your team currently find [buyer type] in [region]?
     Most tools cover about 15-25% of that market."

P2 — Value + CTA (2-3 sentences)
     Product description tied to the question.
     Concrete example.
     CTA embedded: "Happy to show you what comes back for [query]."

P3 — Proof / PS (1 sentence)
     Same as 4P-short.
```

**Best for:** Senior prospects (VP+) who delete long emails. When the CTA is lightweight (sample, not meeting).

**Not tested yet.** Add campaign results here when used.

---

## Structure: 2P-followup

For follow-up emails when the first email got no reply.

```
Paragraphs: 2
Word limit: ≤60 total
Greeting: "Hey {FirstName}," on its own line

P1 — Case study + capability (1-2 sentences)
     Different angle from the first email.
     "We recently helped a [profile] [capability]."
     One concrete example in quotes.

P2 — Sector-shaped CTA (1 sentence)
     Different CTA from first email.
     Tied to their sector/use case.
     Never "quick follow-up" or "circling back."
```

**Best for:** Second touch 3-5 days after first email. Use a different value angle and CTA.

**Tested on:** PE roll-up sourcing (follow-up), market research firms.

---

## Structure: 4P-story

Narrative structure. Tells a short story of a similar company's problem and resolution.

```
Paragraphs: 4
Word limit: ≤130 total
Greeting: "Hey {FirstName}," on its own line

P1 — Hook (1 sentence)
     Specific event, news, or observation about their company.
     Creates curiosity without flattery.

P2 — Peer story (2-3 sentences)
     "A [similar profile] was dealing with [same pain].
     They were [doing workaround]. [Specific cost/time of workaround]."
     Uses research data to make it credible.

P3 — Resolution + value (1-2 sentences)
     What the peer company did differently.
     Product mention embedded naturally, not pitched.

P4 — CTA (1 sentence)
     Soft ask connected to the story.
     "Want to see if the same approach works for [their vertical]?"
```

**Best for:** C-suite and founders who respond to stories more than feature descriptions. When you have a strong case study close to the recipient's profile.

**Not tested yet.** Add campaign results here when used.

---

## Structure: 3P-event

Post-event outreach. Uses a shared event as the opening context.

```
Paragraphs: 3
Word limit: ≤100 total
Greeting: "Hey {FirstName}," on its own line

P1 — Event reference + observation (1-2 sentences)
     Reference the specific event.
     Tie to a trend or pain discussed there.
     Not: "Great seeing you at X" (unless you actually met).

P2 — Value + example (1-2 sentences)
     Product explanation with concrete outcome.
     Example query tied to the event's audience.

P3 — CTA (1 sentence)
     Concrete offer, not a meeting.
     "Want me to run [specific deliverable] on your [event contacts/target list]?"
```

**Best for:** 1-2 weeks after a conference or trade show. When the recipient was an exhibitor or attendee. Works well with H#1 (trade show contact rot).

**Not tested yet.** Add campaign results here when used.

---

## Adding Your Own Structure

After a campaign, if you discover a structure that works, add it here:

```markdown
## Structure: [name]

[1-sentence description]

\```
Paragraphs: [N]
Word limit: ≤[N] total
Greeting: [format]

P1 — [role and rules]
P2 — [role and rules]
...
\```

**Best for:** [audience, motion type, seniority]
**Tested on:** [campaign name, reply rate, date]
```

## Extracting Structure from Past Emails

If you have an email that worked well but no formal structure, paste it and the email-prompt-building skill will:
1. Identify how many paragraphs and their roles
2. Count the word limit
3. Extract the CTA style and proof point placement
4. Create a new structure entry based on the pattern
