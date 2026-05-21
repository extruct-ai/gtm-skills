# Example template set — worked reference

A generic illustration of the artifact `email-prompt-building` produces: a
fixed template set with `{{input_field}}` placeholders, a conditional touch
with variants, and an Input Fields contract. Copy is final approved text —
not instructions for a model to write it.

---

# Sequence — {campaign-slug}

3-touch cold sequence. Variables: `{{first_name}}`, `{{company_name}}`,
`{{industry}}`. Touch 3 is conditional on `{{segment}}`.

## Touch 1 — context hook + core pain

```
Hey {{first_name}},

Congrats on the new role at {{company_name}}.

[One specific inherited pain, 1-2 sentences — concrete, not generic.]

[One sentence on what we do, framed against what the prospect has felt.]

[Soft CTA — a question or a give.]
```

**Subject options (rotate):**
- "{subject A}"
- "{subject B}"
- "{subject C}"

## Touch 2 — proof / benchmark angle

```
Hey {{first_name}},

[A benchmark or proof point that sharpens the Touch 1 pain — sourced, not invented.]

[Give-a-doc CTA — something we send, no time-cost named for the recipient.]
```

**Subject:** empty — follow-up threads as `Re: <Touch 1 subject>`.

## Touch 3 — conditional on {{segment}}

TWO variants. The renderer routes per row on `{{segment}}`.

### Variant A — when segment == "enterprise"

```
Hey {{first_name}},

[Enterprise-specific angle.]

[CTA.]
```

### Variant B — when segment != "enterprise"

```
Hey {{first_name}},

[Mid-market / default angle.]

[CTA.]
```

**Subject:** empty (thread continuation).

---

## Input Fields contract

Every placeholder declared with its source and fallback. The renderer fails
loudly if a declared field is absent; an undeclared placeholder is a bug.

| Field | Source | Fallback if missing |
|-------|--------|---------------------|
| `{{first_name}}` | name-normalization step | skip the contact |
| `{{company_name}}` | name-normalization step | skip the contact |
| `{{industry}}` | industry-classification enrichment column | drop the clause; use the no-`{{industry}}` wording |
| `{{segment}}` (routing key) | segment-classification enrichment column | route to Variant B (default) |

## Notes

- Each touch takes a different angle on the same problem; angles were chosen
  at design time and committed to copy here.
- Follow-up touches use empty subjects so the sequencer threads them.
- Variants are complete separate copy — never one template with inline
  `if segment == ...` conditionals.
