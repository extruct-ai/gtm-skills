# Column Guide

Use this guide whenever you need to create, update, or debug Extruct columns. It blends the public column-management guidance with a comprehensive template library so the agent can both choose the right column behavior and copy good configs.

## Contents

1. Design order
2. Before you run
3. Pick the right column kind
4. Agent types
5. Purpose-built column kinds
6. Output formats
7. Dependencies and prompt writing
8. Troubleshooting
9. Recommended defaults
10. Template library
11. Common chains

## Design Order

When creating a column, make decisions in this order:

1. pick the table kind
2. pick the column kind
3. if needed, pick the agent type
4. pick the output format
5. decide what the column should depend on
6. write the prompt

Many column mistakes come from doing this in reverse.

## Before You Run

Before you add or run columns:

- confirm the table kind, row count, and existing columns
- prefer built-in column kinds before designing custom prompts
- add only the columns you actually need
- run only the new column ids when iterating
- review a small sample of completed rows before scaling out

For full workflows, read:

- `researching-companies.md`
- `finding-people-at-companies.md`
- `researching-people.md`

## Pick The Right Column Kind

Use the simplest column kind that matches the data you want Extruct to return.

### Use `input` When You Already Have The Value

Use `input` for values that already exist in your own system, such as:

- company website
- raw company name
- manual notes
- local scoring metadata

If you already have the value, store it as `input` instead of spending credits asking Extruct to rediscover it.

### Use `agent` When Extruct Needs To Research, Reason, Or Transform

Use a custom `agent` column when you want Extruct to return:

- a new fact it needs to research
- a summary or normalization of upstream row data
- a classification into a fixed set of options
- structured output such as `select`, `money`, `grade`, or `json`

### Prefer Purpose-Built Column Kinds When They Already Match The Job

Use purpose-built kinds for jobs Extruct already knows how to do:

- `company_people_finder`
- `email_finder`
- `phone_finder`
- `reverse_email_lookup`
- `linkedin`

## Agent Types

Extruct agent types are not interchangeable.

| Agent type | Use this when you want Extruct to return... | Notes |
|---|---|---|
| `research_pro` | a company answer grounded in the right company context | default for ordinary company enrichment |
| `research_reasoning` | a judgment-heavy or ambiguous answer that needs careful reasoning | best when the hard part is reasoning, scoring, or disambiguation |
| `llm` | a transformation of data already present in the row | no web research |
| `linkedin` | data from a known LinkedIn company or person URL | use after you already have the right LinkedIn URL |

### `research_pro`

Use `research_pro` when you want Extruct to return a company answer such as:

- pricing and packaging information
- funding or valuation
- target segments
- recent news
- product or use-case research
- closest competitors
- canonical company URLs such as LinkedIn or careers pages

Why it is usually the default on company tables:

- it gathers or confirms company context before answering
- `company` tables automatically inject `company_name` and `company_website`

### `research_reasoning`

Use `research_reasoning` when the hard part is judgment rather than fact collection, for example:

- choosing the official site from messy candidates
- assigning a custom score
- deciding whether the company is SMB, mid-market, or enterprise
- ranking or reasoning across evidence

### `llm`

Use `llm` when you want Extruct to transform data already present in the row.

Use it for:

- `select` values derived from upstream notes
- summaries of several upstream columns
- normalized versions of messy evidence
- structured `json` derived from row context

### `linkedin`

Use `linkedin` when the row already has a known LinkedIn URL and you want LinkedIn-derived data.

Typical pattern:

1. use `research_pro` to find the right LinkedIn URL
2. use `linkedin` to fetch LinkedIn data
3. use `llm` to summarize or classify that data

Important people-table rule:

- on `people` tables, custom `agent` columns can use `llm`, `research_reasoning`, and `linkedin`
- `research_pro` is not allowed on `people`-table custom `agent` columns

## Purpose-Built Column Kinds

### Built-In Company Intelligence

`company` tables automatically create and fill:

- `company_profile`
- `company_name`
- `company_website`

You usually should not create those manually.

### `company_people_finder`

Use this when you want Extruct to return people at a company by role.

It:

- starts from company context
- expands role intent into realistic title variants and searches
- creates or updates a related `people` table

Both exact titles and broader role families are supported.

Use broader role families for coverage:

- `sales leadership`
- `engineering leadership`
- `recruiting`
- `product leadership`

Use precise titles for a narrower search:

- `CEO`
- `VP Sales`
- `Head of Engineering`
- `Revenue Operations`

### `email_finder` And `phone_finder`

These are provider-backed contact lookups, not research agents.

They require:

- `full_name`
- `profile_url`
- `company_website`

`company_website` can come from:

- a parent company row, or
- a local people-table input column keyed exactly `company_website`

### `reverse_email_lookup`

Use this when you already have an email and want Extruct to resolve person or profile data from that email.

It uses a top-level `email_column_key` field and does not use a `value` block.

## Output Formats

Choose the output format that best matches the data you want Extruct to return later.

| Output format | Use this when you want Extruct to return... | Example |
|---|---|---|
| `text` | prose, notes, or short bullet summaries | company description |
| `url` | one canonical URL | careers page |
| `email` | one email address | normalized email from row context |
| `select` | exactly one allowed option | pricing model |
| `multiselect` | zero or more allowed options | markets served |
| `numeric` | a count or measured value | employee count |
| `money` | structured financial data | annual revenue |
| `date` | an exact or partial date | founded date |
| `phone` | one international-format phone number | direct phone |
| `grade` | a 1-5 score with explanation | ICP fit |
| `json` | nested structured output | competitor list |

Guidance:

- use the simplest output format that preserves the business value of the answer
- use `text` for short prose meant to be read directly
- use `select` or `multiselect` when the answer should be constrained to labels
- use `numeric`, `money`, `date`, `url`, `email`, or `phone` when the answer is a single typed value
- use `money` for revenue, ARR, valuation, or funding
- use `grade` for bounded scoring rubrics
- prefer separate columns when fields will be filtered, sorted, exported, or automated independently
- Extruct already returns sources and explanation outside the answer; do not duplicate that wrapper metadata inside `output_schema`
- do not add provenance-only fields such as `sources`, `source_url`, `evidence_url`, `reasoning`, `why`, or `notes` unless those fields are themselves durable business outputs the user wants to keep in the table
- prefer `select` for bounded classifications even when you also want justification; Extruct's response metadata already carries the supporting explanation
- use `json` when the user wants one structured answer with multiple fields that naturally belong together in one cell, such as status plus supporting URL, a competitors array, structured social profiles, launches list, or a product catalog slice

Anti-pattern:

- do not model a bounded decision as `json` just to carry evidence alongside it
- bad fit: remote hiring as `{status, evidence_url, notes}`
- better fit: `remote_hiring_status` as `select` with labels such as `yes`, `no`, `mixed`, `unclear`
- if the user wants one compact structured answer, a small `json` object is fine
- if downstream workflows need each field to be independently filterable, sortable, exportable, or automatable, split them into separate columns

Good fit for `json`:

- `remote_hiring_status` plus `careers_page_url` in one structured answer
- a competitors array with per-competitor fields such as `name`, `domain`, and `short_reason`
- structured social profiles that naturally belong together in one answer
- a product catalog slice or launch list with repeated items

Rule of thumb:

- one bounded label -> `select`
- one typed scalar -> typed non-`json` format
- a few fields that the user wants as one cohesive answer -> `json`
- several independently reusable fields -> separate columns
- one nested object or repeating list -> `json`

If you set `output_format` to `json`, `output_schema` is required.

## Dependencies And Prompt Writing

### Dependencies

For custom `agent` columns, dependencies come from:

- prompt references such as `{pricing_notes}`
- `extra_dependencies`

### Auto-Injected Baseline Context

On `company` and `people` tables, Extruct automatically injects baseline context for custom agent columns.

For `company` tables:

- `company_name`
- `company_website`

For `people` tables:

- `full_name`
- `profile_url`
- `role`

What this means:

- on `company` and `people` tables, most prompts should be plain natural-language instructions with no variables
- add explicit prompt references only when a column must read another custom column
- on `generic` tables, explicit references are often the clearest choice

### Prompt Writing Rules

Each column should ask Extruct for one job.

Good prompts are:

- specific
- narrow
- explicit about what should come back
- grounded in the current row or explicit upstream inputs

Prompt-design rule:

- ask Extruct for the business answer, not for duplicated provenance
- do not ask the model to return URLs, notes, source lists, or reasoning inside the answer just to justify the answer; Extruct already returns sources and explanation outside the answer
- if explanatory text is itself the business output, it is fine to store it explicitly
- if the user wants one compact structured answer, a small `json` object is fine; split into separate columns only when the fields need to be used independently downstream
- prefer one bounded output per column unless the user explicitly wants one cohesive multi-field answer

Research prompt pattern:

```text
Find the company's official careers page URL. Return the single best URL only.
```

Chained `llm` prompt pattern:

```text
Classify the company's pricing approach into exactly one option based on:

Pricing Notes
---
{pricing_notes}
---
```

Bounded classification pattern:

```text
Classify the company's remote hiring status into exactly one option:
yes, no, mixed, unclear.
Return the label only.
```

Split-column pattern:

```text
Classify the company's remote hiring status into exactly one option:
yes, no, mixed, unclear.
Return the label only.
```

If the user also wants the careers page URL in the same answer, returning a small `json` object is fine. Split it into separate columns only when the status and URL need to be used independently downstream.

Competitor discovery pattern:

```text
Find the company's closest competitors and alternatives.
Prefer companies that solve the same core problem for a similar buyer.
Return one object with a competitors array.
Each competitor should include name, domain, and short_reason.
If you are not confident a company is a real competitor, leave it out.
```

Bad JSON vs better typed-columns example:

Bad fit:

```json
{
  "status": "mixed",
  "evidence_url": "https://company.example/careers",
  "notes": "Some roles are remote-friendly."
}
```

Better split when the fields need to be used independently:

```text
remote_hiring_status -> select
careers_page_url -> url
```

Compact JSON example for one combined answer:

```json
{
  "remote_hiring_status": "mixed",
  "careers_page_url": "https://company.example/careers"
}
```

Good JSON example:

```json
{
  "competitors": [
    {
      "name": "Ramp",
      "domain": "ramp.com",
      "short_reason": "Targets the same finance automation buyer."
    }
  ]
}
```

## Troubleshooting

### Unresolved Column References

Cause:

- the prompt references a missing column key

Fix:

- create the source column first
- or change the prompt to reference an existing key

### Column Is Not Compatible With Table Kind

Common examples:

- `company_people_finder` on a `people` table
- `research_pro` custom `agent` column on a `people` table

### Cells Never Start Running

Cause:

- upstream dependency cells are not done

Fix:

- inspect the source columns first
- keep dependency chains short

### Results Are Hard To Use Downstream

Cause:

- too many `text` outputs
- bounded answers were packed into `json` with evidence or commentary fields

Fix:

- move repeated decisions into `select`, `multiselect`, `numeric`, `money`, `date`, `phone`, `grade`, or `json`
- keep provenance in Extruct's wrapper metadata unless the user explicitly needs it as table data

### A Column Feels Expensive

Cause:

- you used web research for a transformation problem

Fix:

- research the source fact once
- derive downstream fields with `llm`

## Recommended Defaults

If you are unsure:

- default to `company` tables
- default to built-in column kinds when available
- default to `research_pro` for company facts
- default to `llm` for downstream transformations
- default to the simplest output format that preserves downstream value
- default to `select` for bounded classifications
- default to separate columns over one `json` blob when the fields have different jobs
- default to `json` only when the answer is naturally multi-field domain data
- do not model Extruct wrapper metadata such as sources or explanation inside `output_schema` unless the user explicitly wants those fields in the table
- default to natural-language prompts with no variables on `company` and `people` tables
- add explicit references only for intentional chaining or on `generic` tables

## Template Library

Copy one or more of these objects into `column_configs`, then adjust `name`, `key`, allowed options, and prompt wording as needed.

Wrapper example:

```json
{
  "column_configs": [
    {
      "kind": "agent",
      "name": "Description",
      "key": "company_description",
      "value": {
        "agent_type": "research_pro",
        "prompt": "Describe what the company does in under 25 words.",
        "output_format": "text"
      }
    }
  ]
}
```

Notes before you copy:

- on `company` and `people` tables, required columns are created automatically
- on those tables, custom agent columns get baseline context injected automatically
- most prompts on `company` and `people` tables should not mention `company_name`, `company_website`, `full_name`, `profile_url`, or `role` explicitly
- if a template below references another column, that dependency is intentional

### Company Research

#### Description

```json
{
  "kind": "agent",
  "name": "Description",
  "key": "company_description",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Describe what the company does in under 25 words.",
    "output_format": "text"
  }
}
```

#### ICP Summary

```json
{
  "kind": "agent",
  "name": "ICP Summary",
  "key": "icp_summary",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Identify the company's ideal customer profile. Summarize the primary buyer, company type, and likely use case in 2-3 short bullet points.",
    "output_format": "text"
  }
}
```

#### Employee Count

```json
{
  "kind": "agent",
  "name": "Employee Count",
  "key": "employee_count",
  "value": {
    "agent_type": "research_pro",
    "prompt": "How many employees does the company currently have?",
    "output_format": "numeric"
  }
}
```

#### Annual Revenue

```json
{
  "kind": "agent",
  "name": "Annual Revenue",
  "key": "annual_revenue",
  "value": {
    "agent_type": "research_pro",
    "prompt": "What is the company's latest annual revenue or ARR? Prefer the most recent reliable figure and use revenue, not total funding.",
    "output_format": "money"
  }
}
```

#### Founded Date

```json
{
  "kind": "agent",
  "name": "Founded Date",
  "key": "founded_date",
  "value": {
    "agent_type": "research_pro",
    "prompt": "When was the company founded?",
    "output_format": "date"
  }
}
```

#### Pricing Notes

```json
{
  "kind": "agent",
  "name": "Pricing Notes",
  "key": "pricing_notes",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Summarize the company's pricing model and publicly visible price points as a short bulleted list. Include plan names and prices when available.",
    "output_format": "text"
  }
}
```

#### Recent News

```json
{
  "kind": "agent",
  "name": "Recent News",
  "key": "recent_news",
  "value": {
    "agent_type": "research_pro",
    "prompt": "List the company's most important news from the last 12 months, newest first. Include date, headline, and URL.",
    "output_format": "json",
    "output_schema": {
      "type": "object",
      "properties": {
        "articles": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "date": {"type": "string"},
              "headline": {"type": "string"},
              "url": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

#### Product Launches Last 12 Months

```json
{
  "kind": "agent",
  "name": "Product Launches",
  "key": "product_launches",
  "value": {
    "agent_type": "research_pro",
    "prompt": "List the company's notable product launches from the last 12 months, newest first. Return one object with a launches array. Each launch should include date, name, summary, and url when available. Leave out vague marketing updates that are not real launches.",
    "output_format": "json",
    "output_schema": {
      "type": "object",
      "properties": {
        "launches": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "date": {"type": "string"},
              "name": {"type": "string"},
              "summary": {"type": "string"},
              "url": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

#### Competitors

```json
{
  "kind": "agent",
  "name": "Competitors",
  "key": "competitors",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Find the company's closest competitors and alternatives. Prefer companies that solve the same core problem for a similar buyer. Return one object with a competitors array. Each competitor should include name, domain, and short_reason. If you are not confident a company is a real competitor, leave it out.",
    "output_format": "json",
    "output_schema": {
      "type": "object",
      "properties": {
        "competitors": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "domain": {"type": "string"},
              "short_reason": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

#### Expansion Signals

```json
{
  "kind": "agent",
  "name": "Expansion Signals",
  "key": "expansion_signals",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Identify and summarize the company's expansion signals using job postings, press releases, new office mentions, executive hires, and product launches. Focus on geographic, product, or market expansion. Return a short evidence-dense summary with dates when available.",
    "output_format": "text"
  }
}
```

### URLs And LinkedIn

#### LinkedIn Company URL

```json
{
  "kind": "agent",
  "name": "LinkedIn URL",
  "key": "linkedin_company_url",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Find the company's official LinkedIn company page URL.",
    "output_format": "url"
  }
}
```

#### LinkedIn Company Data

Requires:

- `linkedin_company_url`

```json
{
  "kind": "agent",
  "name": "LinkedIn Data",
  "key": "linkedin_company_data",
  "value": {
    "agent_type": "linkedin",
    "prompt": "{linkedin_company_url}",
    "output_format": "text"
  }
}
```

#### LinkedIn Activity Summary

Requires:

- `linkedin_company_data`

```json
{
  "kind": "agent",
  "name": "LinkedIn Activity",
  "key": "linkedin_activity_summary",
  "value": {
    "agent_type": "llm",
    "prompt": "Summarize the recent LinkedIn activity as a bulleted list with names, dates, and links.\n\nLinkedIn Company Data\n---\n{linkedin_company_data}\n---",
    "output_format": "text"
  }
}
```

#### Careers Page URL

```json
{
  "kind": "agent",
  "name": "Careers URL",
  "key": "careers_page_url",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Find the company's official careers or jobs page URL.",
    "output_format": "url"
  }
}
```

#### Crunchbase URL

```json
{
  "kind": "agent",
  "name": "Crunchbase URL",
  "key": "crunchbase_url",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Find the company's Crunchbase profile URL.",
    "output_format": "url"
  }
}
```

### Derived `llm`

#### Pricing Model

Requires:

- `pricing_notes`

```json
{
  "kind": "agent",
  "name": "Pricing Model",
  "key": "pricing_model",
  "value": {
    "agent_type": "llm",
    "prompt": "Select the company's primary pricing model.\n\nPricing Notes\n---\n{pricing_notes}\n---",
    "output_format": "select",
    "labels": [
      "Free",
      "Freemium",
      "Subscription",
      "Usage-Based",
      "Custom Quote",
      "One-Time Purchase",
      "Marketplace Take Rate"
    ]
  }
}
```

#### HQ Country From Company Profile

Requires:

- `company_profile`

```json
{
  "kind": "agent",
  "name": "HQ Country",
  "key": "hq_country",
  "value": {
    "agent_type": "llm",
    "prompt": "Extract the company's headquarters country from this company profile.\n\nCompany Profile\n---\n{company_profile}\n---",
    "output_format": "text"
  }
}
```

#### Revenue Band

Requires:

- `annual_revenue`

```json
{
  "kind": "agent",
  "name": "Revenue Band",
  "key": "revenue_band",
  "value": {
    "agent_type": "llm",
    "prompt": "Classify the company's revenue into exactly one band based on this structured revenue data.\n\nAnnual Revenue\n---\n{annual_revenue}\n---",
    "output_format": "select",
    "labels": [
      "<$1M",
      "$1M-$10M",
      "$10M-$50M",
      "$50M-$100M",
      "$100M-$500M",
      "$500M+"
    ]
  }
}
```

#### Buyer Type

Requires:

- `company_description`

```json
{
  "kind": "agent",
  "name": "Buyer Type",
  "key": "buyer_type",
  "value": {
    "agent_type": "llm",
    "prompt": "Select the company's primary buyer type.\n\nDescription\n---\n{company_description}\n---",
    "output_format": "select",
    "labels": [
      "SMB",
      "Mid-Market",
      "Enterprise",
      "Consumer",
      "Developer",
      "Public Sector",
      "Healthcare Providers",
      "Financial Institutions"
    ]
  }
}
```

#### Prioritization JSON

Requires:

- `company_profile`
- `expansion_signals`
- `annual_revenue`
- `recent_news`

```json
{
  "kind": "agent",
  "name": "Prioritization",
  "key": "prioritization",
  "value": {
    "agent_type": "llm",
    "prompt": "You are a go-to-market analyst. Score ICP fit and buying intent. Return ONLY valid JSON with: icp_fit_score, buying_intent_score, positive_signals, negative_signals, recommended_action, outreach_hook.\n\nCompany Profile\n---\n{company_profile}\n---\n\nExpansion Signals\n---\n{expansion_signals}\n---\n\nAnnual Revenue\n---\n{annual_revenue}\n---\n\nRecent News\n---\n{recent_news}\n---",
    "output_format": "json",
    "output_schema": {
      "type": "object",
      "properties": {
        "icp_fit_score": {"type": "number"},
        "buying_intent_score": {"type": "number"},
        "positive_signals": {
          "type": "array",
          "items": {"type": "string"}
        },
        "negative_signals": {
          "type": "array",
          "items": {"type": "string"}
        },
        "recommended_action": {"type": "string"},
        "outreach_hook": {"type": "string"}
      }
    }
  }
}
```

If you want people-finder evidence in downstream scoring, first create a separate `llm` summary column from the people output, then reference that summary instead of the raw `company_people_finder` result.

### People And Contact

#### Leadership Finder

```json
{
  "kind": "company_people_finder",
  "name": "Leadership",
  "key": "leadership",
  "value": {
    "roles": [
      "CEO",
      "Founder",
      "operations leadership",
      "revenue leadership"
    ]
  }
}
```

#### Engineering Leadership Finder

```json
{
  "kind": "company_people_finder",
  "name": "Engineering Leaders",
  "key": "engineering_leaders",
  "value": {
    "roles": [
      "Head of Engineering",
      "VP Engineering",
      "platform leadership",
      "security leadership"
    ]
  }
}
```

#### Decision Makers

```json
{
  "kind": "company_people_finder",
  "name": "Decision Makers",
  "key": "decision_makers",
  "value": {
    "roles": [
      "VP Sales",
      "sales leadership",
      "revenue operations",
      "business development leadership"
    ]
  }
}
```

#### Work Email

Requires:

- `company_website`

Configured with `kind`, `name`, and `key` only. No `value` field is required.

```json
{
  "kind": "email_finder",
  "name": "Work Email",
  "key": "work_email"
}
```

#### Direct Phone

Requires:

- `company_website`

Configured with `kind`, `name`, and `key` only. No `value` field is required.

```json
{
  "kind": "phone_finder",
  "name": "Direct Phone",
  "key": "direct_phone"
}
```

#### Department

```json
{
  "kind": "agent",
  "name": "Department",
  "key": "department",
  "value": {
    "agent_type": "llm",
    "prompt": "Classify this person into the most likely department based on their current role.",
    "output_format": "select",
    "labels": [
      "Executive",
      "Engineering",
      "Product",
      "Design",
      "Sales",
      "Marketing",
      "Operations",
      "Finance",
      "HR",
      "Legal",
      "Customer Success",
      "Other"
    ]
  }
}
```

#### Seniority

```json
{
  "kind": "agent",
  "name": "Seniority",
  "key": "seniority",
  "value": {
    "agent_type": "llm",
    "prompt": "Classify this person's seniority level based on their current role.",
    "output_format": "select",
    "labels": [
      "C-Level",
      "VP",
      "Head",
      "Director",
      "Manager",
      "Individual Contributor",
      "Founder"
    ]
  }
}
```

#### Reverse Email Lookup

```json
{
  "kind": "reverse_email_lookup",
  "name": "Profile from Email",
  "key": "profile_from_email",
  "email_column_key": "work_email"
}
```

### Scoring

#### AI-Native Score

```json
{
  "kind": "agent",
  "name": "AI Native",
  "key": "is_ai_native",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Assess this statement about the company: The company is fundamentally AI-native rather than merely adding lightweight AI features. Use the default 1-5 grade scale. If there is not enough evidence to score confidently, return Not found.",
    "output_format": "grade"
  }
}
```

#### Enterprise Fit Score

```json
{
  "kind": "agent",
  "name": "Enterprise Fit",
  "key": "enterprise_fit",
  "value": {
    "agent_type": "research_pro",
    "prompt": "Assess this statement about the company: The company clearly sells to enterprise customers. Use the default 1-5 grade scale. If there is not enough evidence to score confidently, return Not found.",
    "output_format": "grade"
  }
}
```

#### Competitive Axis Score

```json
{
  "kind": "agent",
  "name": "SMB vs Enterprise",
  "key": "axis_smb_enterprise",
  "value": {
    "agent_type": "research_reasoning",
    "prompt": "Evaluate where this company sits on the spectrum from SMB to Enterprise. Consider pricing, sales model, product complexity, and customer size. Use this scale: 1 = pure SMB, 3 = mid-market, 5 = pure enterprise. If there is not enough evidence to score confidently, return Not found.",
    "output_format": "grade"
  }
}
```

## Common Chains

### URL -> LinkedIn Fetch -> Summary

1. `linkedin_company_url`
2. `linkedin_company_data`
3. `linkedin_activity_summary`

### Research -> Classification

1. `pricing_notes`
2. `pricing_model`

### Company -> People -> Contact Enrichment

Use:

- `finding-people-at-companies.md`
- `researching-people.md`
