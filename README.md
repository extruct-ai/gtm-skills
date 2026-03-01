# Skills

Claude Code skills for the Extruct GTM repo. Each skill is a directory with a `SKILL.md` and optional `references/`.

## GTM Pipeline Skills (end-to-end workflow)

These 10 skills form a connected pipeline. Run them in order for a full campaign.

```
0. company-context-builder  →  Foundation (ICP, win cases, DNC)
1. list-building             →  Find companies (Search, Discovery, Lookalike)
2. market-problems-deep-research → Research vertical pain points (Perplexity)
3. data-points-builder       →  Design enrichment columns
4. table-enrichment          →  Run enrichment on Extruct table
   (5. Re-run list-building with enrichment insights — optional)
6. segment-and-tier          →  Tier companies by hypothesis fit
6b. linkedin-finder          →  Find LinkedIn profiles (Extruct, zero credits)
6c. email-finder             →  Get verified emails + phones (Prospeo / Fullenrich)
7. email-generation          →  Generate emails (tier-aware)
8. copy-feedback             →  Persona review for Tier 1 (Perplexity)
9. run-instantly             →  Upload to Instantly + send
   (10. Feedback loop → company-context-builder)
```

| Step | Skill | Trigger | Description |
|------|-------|---------|-------------|
| 0 | **company-context-builder** | "company context", "ICP", "win cases" | Build/maintain global context file for all skills |
| 1 | **list-building** | "find companies", "build a list", "lookalike" | Build company lists with decision tree + lookalike mode |
| 2 | **market-problems-deep-research** | "deep research", "hypothesis set", "market research" | Research vertical pain points via Perplexity |
| 3 | **data-points-builder** | "data points", "enrichment columns", "column design" | Design enrichment columns (segmentation + personalization) |
| 4 | **table-enrichment** | "enrich", "add column", "run enrichment" | Add columns to Extruct table with progress monitoring |
| 6 | **segment-and-tier** | "segment", "tier", "prioritize list" | Tier companies by hypothesis fit + data richness |
| 6b | **linkedin-finder** | "find linkedin", "find people", "find contacts" | Find LinkedIn profiles via Extruct (zero credits) |
| 6c | **email-finder** | "find emails", "enrich contacts", "email finder" | Get verified emails + phones via Prospeo / Fullenrich |
| 7 | **email-generation** | "generate emails", "email pipeline" | Generate emails from CSV + prompt (tier-aware) |
| 8 | **copy-feedback** | "review email", "copy feedback", "persona review" | Persona-based review for Tier 1 accounts |
| 9 | **run-instantly** | "upload to instantly", "send emails" | Upload leads to Instantly + pre-send checklist |

## Other Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| **create-table** | "create table", "upload companies" | Create Extruct table, upload rows, add columns |
| **cold-email** | "cold email", "outreach prompt" | Email prompt template builder |
| **company-edit** | "format companies", "company list" | Format company data for blog articles |

## Structure

```
.claude/skills/
├── README.md                          ← this file
│
│   # Pipeline skills (new)
├── company-context-builder/
│   ├── SKILL.md
│   └── references/
│       └── context-schema.md
├── list-building/
│   ├── SKILL.md
│   └── references/
│       ├── search-filters.md
│       └── discovery-api.md
├── market-problems-deep-research/
│   ├── SKILL.md
│   └── references/
│       └── pe-rollup-example.md
├── data-points-builder/
│   ├── SKILL.md
│   └── references/
│       └── data-point-library.md
├── table-enrichment/
│   ├── SKILL.md
│   └── references/
│       └── api_reference.md
├── segment-and-tier/
│   ├── SKILL.md
│   └── references/
│       └── tiering-framework.md
├── email-generation/
│   ├── SKILL.md
│   └── references/ (uses cold-email references)
├── copy-feedback/
│   ├── SKILL.md
│   └── references/
│       └── persona-review-template.md
├── linkedin-finder/
│   ├── SKILL.md
│   └── references/
│       └── api_reference.md
├── email-finder/
│   ├── SKILL.md
│   └── references/
│       ├── prospeo-api.md
│       └── fullenrich-api.md
├── find-people/                       ← legacy (monolithic version)
│   ├── SKILL.md
│   └── references/
│       ├── prospeo-api.md
│       └── fullenrich-api.md
├── run-instantly/
│   ├── SKILL.md
│   └── references/
│       └── instantly-api.md
│
│   # Other skills
├── cold-email/
│   ├── SKILL.md
│   └── references/
│       └── prompt-patterns.md
├── create-table/
│   └── SKILL.md
└── company-edit/
    └── SKILL.md
```

## External Tools & Environment Variables

Skills depend on external APIs. All keys are loaded from a `.env` file via `python-dotenv`.

| Variable | Service | Base URL | Used by |
|----------|---------|----------|---------|
| `EXTRUCT_API_TOKEN` | Extruct API | `https://api.extruct.ai/v1` | list-building, table-enrichment, create-table |
| `PERPLEXITY_API_KEY` | Perplexity (Sonar Pro) | `https://api.perplexity.ai/chat/completions` | market-problems-deep-research, copy-feedback |
| `PROSPEO_API_KEY` | Prospeo | `https://api.prospeo.io` | email-finder |
| `FULLENRICH_API_KEY` | Fullenrich | `https://api.fullenrich.com/api/v1` | email-finder |
| `INSTANTLY_API_KEY` | Instantly | `https://api.instantly.ai/api/v2` | run-instantly |

### `.env` setup

If no `.env` file exists in the project root, create one:

```bash
cp .env.example .env
# then fill in your keys
```

`.env.example`:

```
# Extruct — company search, tables, enrichment
EXTRUCT_API_TOKEN=

# Perplexity — deep research, persona building
PERPLEXITY_API_KEY=

# Prospeo — people search
PROSPEO_API_KEY=

# Fullenrich — email/phone waterfall enrichment
FULLENRICH_API_KEY=

# Instantly — email sequencing and sending
INSTANTLY_API_KEY=

```

Not all keys are required. Only add keys for the skills you plan to use.

## Context File

All pipeline skills read from one global context file:

```
claude-code-gtm/context/extruct_context.md
```

Build it with `company-context-builder`. It stores ICP, win cases, campaign history, hypotheses, and DNC list.

## Contributing

These skills are templates. They reflect one team's GTM workflow — yours will be different. We encourage you to fork, adapt, and experiment.

**PRs are welcome.** If you've built a skill that others could use, open a PR. A few rules:

1. **Declare your dependencies.** Every skill that calls an external API must list the vendor and the env variable in its `SKILL.md` (Auth section). If your skill adds a new API, update `.env.example` and the env table in this README.
2. **One skill, one job.** A skill should do one thing well. If it's doing two things, split it.
3. **Include a `SKILL.md`.** Follow the existing format: frontmatter (`name`, `description` with triggers), workflow steps, code examples.
4. **Add references if needed.** API specs, example outputs, and schemas go in a `references/` subdirectory.

### Skill structure

```
your-skill/
├── SKILL.md              ← required
└── references/           ← optional
    └── api-docs.md
```

### What makes a good PR

- Solves a real workflow problem you've hit
- Works end-to-end (not a stub)
- Documents the external tools and API keys it needs
- Doesn't duplicate an existing skill — extend or replace instead

## Community

The community is being shaped. Join our Discord to share workflows, get help, and suggest new skills:

https://discord.gg/extruct
