"""Reference renderer for the email-generation skill.

Deterministic — no LLM. Reads a fixed template set + a contact CSV whose
input fields are already filled, routes variants, substitutes placeholders,
renders to the target format, writes the per-row output CSV.

This is a REFERENCE implementation. Adapt the template constants and the
routing rule to the campaign's own sequence.md. The render contract — newline
model, escaping, operation order — must not change.

Usage:
    python3 render_emails.py contacts.csv emails_generated.csv
"""
import csv
import html
import sys


# ── Templates ─────────────────────────────────────────────────────────────────
# In a real campaign these come from the campaign's sequence.md. Each is plain
# text: "\n\n" = paragraph break, "\n" = soft line break inside a paragraph.

TOUCH_1 = """Hey {{first_name}},

Congrats on the new role at {{company_name}}.

[core pain]

Want to compare notes on {{industry}}?"""

TOUCH_1_NO_INDUSTRY = """Hey {{first_name}},

Congrats on the new role at {{company_name}}.

[core pain]

Want to compare notes?"""

TOUCH_2 = """Hey {{first_name}},

[benchmark angle]

[give-a-doc CTA]"""

TOUCH_3_ENTERPRISE = """Hey {{first_name}},

[enterprise angle]

[CTA]"""

TOUCH_3_DEFAULT = """Hey {{first_name}},

[default angle]

[CTA]"""

TOUCH_1_SUBJECTS = ["{subject A}", "{subject B}", "{subject C}"]


# ── Render contract ───────────────────────────────────────────────────────────

def fill(template: str, **fields) -> str:
    """Substitute {{key}} placeholders. Step 2 of the contract."""
    out = template
    for k, v in fields.items():
        out = out.replace("{{" + k + "}}", v or "")
    return out


def render(body: str, target: str) -> str:
    """Render the assembled plain-text body to a target format.

    Step 3 of the contract — runs LAST, after variant routing + substitution,
    so substituted field values are escaped too.

    target: 'review' | 'plain' keep newlines literal; 'html' converts
    '\\n' -> '<br />' and HTML-escapes content (escape per line, never the tags).
    """
    if target in ("review", "plain"):
        return body
    if target == "html":
        return "<br />".join(html.escape(line) for line in body.split("\n"))
    raise ValueError(f"unknown render target: {target}")


def assert_rendered(body: str, who: str):
    """No placeholder may survive into output."""
    if "{{" in body:
        raise AssertionError(f"unsubstituted placeholder for {who}: {body[:120]}")


# ── Pipeline ──────────────────────────────────────────────────────────────────

def main(contacts_csv: str, out_csv: str):
    with open(contacts_csv) as f:
        contacts = list(csv.DictReader(f))

    rows = []
    for i, c in enumerate(contacts):
        first = c["first_name"]
        company = c["company_name"]
        industry = c.get("industry", "")
        segment = c.get("segment", "")

        # Touch 1 — field-driven variant (industry present or fallback)
        if industry:
            body1 = fill(TOUCH_1, first_name=first, company_name=company, industry=industry)
            gaps1 = ""
        else:
            body1 = fill(TOUCH_1_NO_INDUSTRY, first_name=first, company_name=company)
            gaps1 = "industry=fallback"
        subject1 = TOUCH_1_SUBJECTS[i % len(TOUCH_1_SUBJECTS)]  # deterministic rotation

        # Touch 2 — universal, empty subject (thread continuation)
        body2 = fill(TOUCH_2, first_name=first)

        # Touch 3 — routed variant on the segment key
        if segment == "enterprise":
            body3 = fill(TOUCH_3_ENTERPRISE, first_name=first)
            variant3 = "enterprise"
        else:
            body3 = fill(TOUCH_3_DEFAULT, first_name=first)
            variant3 = "default"

        for touch, body, subject, variant, gaps in [
            (1, body1, subject1, "universal", gaps1),
            (2, body2, "", "universal", ""),
            (3, body3, "", variant3, ""),
        ]:
            assert_rendered(body, f"{c['email']} touch {touch}")
            rows.append({
                "email": c["email"],
                "first_name": first,
                "company_name": company,
                "touch": touch,
                "variant": variant,
                "subject": subject,
                "body": render(body, "review"),       # review CSV keeps \n literal
                "body_html": render(body, "html"),    # sequencer-ready
                "gaps": gaps,
            })

    # csv.DictWriter quotes multiline cells correctly — required for the body column
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} emails ({len(contacts)} contacts x 3 touches) -> {out_csv}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
