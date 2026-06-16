---
name: atomic-message
description: >
  Draft ONE cold-outreach message from a signal + persona + channel: a single
  cold email, a LinkedIn note, or a follow-up. Generates one primary draft plus
  1-2 variants, then runs a self-check lint. Reads voice, sender identity,
  positioning, proof, and banned words from the company context file. This is
  the single-message craft engine; it does NOT build sequences, cadences, or
  multi-touch arcs (email-prompt-building owns sequencing). Triggers on: "write
  a message", "draft a message", "atomic message", "write a single email",
  "one-off email", "write a linkedin message", "linkedin note", "linkedin dm",
  "write a follow-up", "follow-up message", "draft outreach", "rewrite this
  message", "write a cold email" (one message, not a sequence).
---

# Atomic Message

Draft one outreach message at a time: a cold email, a LinkedIn note, or a follow-up. Generate a primary draft plus 1-2 variants, then lint against the craft rules before emitting.

This skill writes ONE message. It does NOT design multi-touch sequences, cadences, or step arcs, and it does not decide send timing. That is `email-prompt-building`'s job. When a sequence needs each touch written, that skill calls this one per touch.

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| Signal | yes | the reason to reach out now: job change, hiring JD, event, post engagement, funding, or a specific observation. From upstream enrichment, the user, or research. |
| Persona | yes | the recipient's role cluster (e.g. founder, revops, sales leadership, IC). Shapes which pain and proof to lead with. |
| Channel | yes | one of: `cold email`, `linkedin`, `follow-up`. Sets length, format, casing, and CTA style. |
| Recipient context | no | name, company, role facts. Used to make the message relevant, never recited back. |
| Company context file | yes | voice, sender identity, what-we-do, positioning, proof library, CTA options, banned words. Read at runtime. |

## Workflow

### Step 1: Read the context file

Read the company context file's Voice, What We Do, Proof, CTA, and banned-words sections. The skill supplies the craft (how to make an atomic message good); the context file supplies the company's voice and facts. **If the context file's Voice section defines a per-channel spec, it overrides the generic channel defaults** in `references/craft.md`.

### Step 2: Pick the angle

From the signal + persona, choose exactly one of each:

- the ONE thing to open on: the signal, or a sharp problem line that does not repeat the solution
- the ONE capability framing relevant to that persona (from What We Do)
- the ONE proof point relevant to that persona (from Proof; never stack more than one)
- the ONE CTA (from the context file's CTA options; one per message, never stacked)

One signal, one framing, one proof, one ask. If you have three angles, that is three candidate messages, not one crammed message.

### Step 3: Draft for the channel

Follow the channel's structure and length in `references/craft.md`, applying the context file's voice. Produce:

- 1 primary draft
- 1-2 variants that change the ANGLE (a different signal framing or a different proof), not just reworded synonyms

### Step 4: Self-check (lint)

Run every draft through the self-check in `references/craft.md` before emitting. Read each line aloud in your head first. Fix anything it flags.

### Step 5: Emit

Output the primary draft and variants as plain text (no markdown blockquotes). For cold email, include subject-line options. Label what each variant changes so the user can choose.

## Reference

See [references/craft.md](references/craft.md) for the universal copy mechanics, the per-channel structure (cold email / linkedin / follow-up), and the self-check lint.
