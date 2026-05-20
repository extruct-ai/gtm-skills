---
name: email-generation
description: >
  Render a cold-outreach email sequence from a fixed template set and a
  contact CSV whose input fields are already filled. Deterministic — variant
  routing + placeholder substitution, no per-row LLM call. The render contract
  (newline model, per-target escaping, operation order) is the core of this
  skill. Triggers on: "generate emails", "email generation", "run emails",
  "render emails", "create emails", "email pipeline", "generate outreach".
---

# Email Generation (Renderer)

Render a sequence from a **fixed template set** (`sequence.md` from `email-prompt-building`) and a contact CSV whose `{{input_fields}}` are already populated. This skill is **mechanical**: route variants, substitute placeholders, render to the target format, write the output CSV.

There is **no LLM call here.** All strategic reasoning happened at design time (`email-prompt-building`); all per-row intelligence happened upstream in normalization + enrichment, which filled the input fields. If an email is wrong, the template or the input data is wrong — fix the source, re-render.

## Architectural Principle

**This skill is a renderer, not a reasoner and not a runner.**

```
template set (sequence.md) ─┐
                            ├──▶ route variant ─▶ substitute ─▶ render to target ──▶ emails CSV
contact CSV (fields filled) ┘
```

## Inputs Required

| Input | Source | Required |
|-------|--------|----------|
| Template set | The campaign's sequence file from `email-prompt-building` | yes |
| Contact CSV | Input fields already filled by normalization + enrichment | yes |

The contact CSV must carry **every field in the template's Input Fields contract**, plus the routing key(s). If a declared field is missing for a row, apply that field's declared fallback; if the row can't be salvaged, drop it and report.

## The Render Contract

Rendering is where this pipeline actually breaks. "Substitute the placeholders" hand-waves the hard part — newlines and escaping. This contract is mandatory.

### Newline model

The template uses two break types and the renderer MUST preserve the distinction:
- **`\n\n` (blank line)** = paragraph break
- **`\n` (single)** = soft line break inside a paragraph (used deliberately)

### Render targets — one body, three outputs

| Target | Newline handling | Escaping |
|--------|------------------|----------|
| `review` (`emails.md` / CSV `body` column) | keep `\n\n` and `\n` literal | none — but the CSV writer MUST quote the multiline cell |
| `html` (Instantly / sequencer) | `\n` → `<br />` (so `\n\n` → `<br /><br />`) | HTML-escape `& < >` in the content |
| `plain` (plain-text channels) | keep literal | none |

### Order of operations — non-negotiable

1. **Route variant** — pick the touch variant using the routing key (e.g. `customer_segment`).
2. **Substitute `{{fields}}`** into the plain-text body.
3. **Escape + newline-convert LAST**, on the fully-assembled string.

Why this order: if you HTML-escape the template *before* substitution, a field value like `Johnson & Johnson` slips in unescaped and breaks the HTML. Escaping the final assembled string covers both template copy and substituted values.

### Reference renderer

```python
import html

def render(body: str, target: str) -> str:
    """body: assembled plain-text (variant chosen, {{fields}} substituted).
    target: 'review' | 'html' | 'plain'."""
    if target in ("review", "plain"):
        return body
    if target == "html":
        # escape content per line, THEN join with <br /> — never escape the tags
        return "<br />".join(html.escape(line) for line in body.split("\n"))
    raise ValueError(target)
```

### Failure modes the renderer must guard against

- **#1 bug — forgetting `\n` → `<br>`**: the email arrives as one wall of text. Every HTML sequencer needs the conversion.
- **Escaping before substitution** — field values with `& < >` break the HTML.
- **Double-escaping** — `&amp;amp;`. Escape exactly once, as the last step.
- **Unquoted multiline CSV cell** — embedded newlines in the `body` column shift rows/columns. Use a real CSV writer.
- **Unsubstituted placeholders** — the renderer MUST assert zero `{{` remain in any output before writing. A leftover `{{company_name}}` means the field wasn't passed (e.g. Touch 3 not receiving `company_name`).

## Workflow

### Step 1: Validate inputs

- Read the template set; collect every `{{field}}` and every routing key.
- Read the contact CSV headers; confirm every declared input field + routing key is present.
- Report any mismatch and stop before rendering.

### Step 2: Render per row

For each contact, for each touch:
1. Route the variant (if the touch has variants).
2. Substitute input fields into the plain-text body; apply per-field fallback when a value is empty.
3. Render to each required target (`review`, `html`).
4. Assert no `{{` remains.

Subject lines: first touch only; follow-ups carry an empty subject (thread continuation).

### Step 3: Write outputs

- An emails CSV — one row per (contact × touch): `email, first_name, company_name, touch, variant, subject, body, body_html, gaps`. The `gaps` column records which fields fell back (e.g. `industry=fallback`).
- A human-readable review file — one email per section.

Write both into the GTM project's campaign-assets location. See [references/render_emails.py](references/render_emails.py) for the reference renderer.

### Step 4: Quality checks

- [ ] Zero unsubstituted `{{` across all rows
- [ ] Variant routing correct — spot-check one row per variant
- [ ] `\n\n` and `\n` both survive into the HTML target as `<br /><br />` / `<br />`
- [ ] A field value containing `&` / `<` renders escaped (not raw, not double-escaped)
- [ ] Row count = contacts × touches; `gaps` populated where fallbacks fired
- [ ] Follow-up touches have empty subject

## Feedback Loop

When the user flags a bad email:
1. Identify whether it's a **copy** problem (→ fix the template via `email-prompt-building`) or a **data** problem (→ fix normalization/enrichment so the input field is correct).
2. Re-render. Never hand-edit an individual email — the fix is always in the template or the input data.

## Suppression

Before writing the output CSV, drop any contact whose email is on the GTM project's suppression list (unsubscribes, bounces, retired addresses). The project owns where that list lives; this skill only honors it.

## No template yet?

If no `sequence.md` exists for the campaign, use the `email-prompt-building` skill to design one. Do not improvise copy in this skill — this skill only renders.
