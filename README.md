![Extruct](docs/images/cover.png)

# GTM Skills

[Skills](https://docs.anthropic.com/en/docs/claude-code/skills) are reusable prompt templates for Claude Code, Anthropic's agentic coding tool. This pack covers outbound campaigns: research, list building, enrichment, segmentation, email generation, and sending. Use one skill or combine several. Each works independently.

Maintained by [Extruct AI](https://www.extruct.ai).

> **These skills are templates.** They show one way to run GTM workflows using Extruct and Claude Code. Fork them, adapt to your workflow, swap out the tools you don't use. The skill patterns are the value, the specific vendor integrations are up to you.

## Install

```
npx skills add extruct-ai/gtm-skills
```

**Where skills live:** Once installed, skills are stored in `~/.claude/skills/`. They become globally available across all your projects. Install once, use everywhere.

## Quick Start

After installing, just describe what you need:

**Start from your website:**

```
I'm building www.example.com.
Read my website, figure out my ICP,
and draft a plan for an outbound campaign.
```

**Start from a win case:**

```
I'm building www.example.com.
One of my customers is www.customer.com,
they use us to score suppliers.
Find similar companies and plan a campaign.
```

**Start from a list of won deals:**

```
I'm building www.example.com.
Here's a list of my won deals [attach CSV].
Analyze them and find similar companies to target.
```

Each prompt triggers plan mode. Claude will research, ask clarifying questions, and propose a step-by-step campaign plan before executing.

## Skills

Building blocks for outbound campaigns. Use one, combine a few, or run them all. No required sequence, each skill works independently.

| Skill | Description |
|-------|-------------|
| **context-building** | Build/maintain global context file (ICP, voice, proof points, DNC) |
| **hypothesis-building** | Generate pain hypotheses from context file + user knowledge (no API) |
| **list-building** | Find companies via Search, Discovery, or Lookalike |
| **market-research** | Research vertical pain points via deep research APIs |
| **enrichment-design** | Design enrichment columns (segmentation + personalization) |
| **list-enrichment** | Add research columns to Extruct tables |
| **table-creation** | Create Extruct table, upload rows, add columns |
| **list-segmentation** | Tier companies by hypothesis fit + data richness |
| **people-search** | Find LinkedIn profiles via Extruct |
| **email-search** | Get verified emails + phones via contact enrichment providers |
| **email-prompt-building** | Build self-contained prompt template for a campaign. **Edit this skill to change email structure** (paragraph count, word limits, format). |
| **email-generation** | Generate emails from prompt + CSV (tier-aware) |
| **email-response-simulation** | Simulate prospect reading your email (Tier 1 review) |
| **campaign-sending** | Upload leads for sequencing and sending |

## About Extruct

[Extruct](https://www.extruct.ai): API-first company search and lookalikes engine.

**Core capabilities:**
- **Instant Search**: semantic company search (free, unlimited)
- **Lookalike Search**: find companies similar to your best accounts (free, unlimited)
- **Deep Search**: AI-powered discovery with criteria scoring (1 credit/match)
- **AI Tables**: research any data point per company with AI agents (1 credit/cell)
- **People Finder**: find decision makers with LinkedIn profiles (2 credits/cell)

**Pricing:** from $59/mo for 1K credits. Free trial with 100 credits. See [extruct.ai/pricing](https://www.extruct.ai/pricing).

Built by [Danny Chepenko](https://www.linkedin.com/in/danielchepenko/) and [Dima Persiyanov](https://www.linkedin.com/in/persiyanov/)

---

## Reference

### Campaign Artifacts

Skills automatically create a `claude-code-gtm/` directory with all intermediate files:

```
claude-code-gtm/
├── context/
│   ├── {company}_context.md          ← ICP, voice, proof points
│   └── {vertical-slug}/             ← per-vertical research + hypotheses
├── prompts/
│   └── {vertical-slug}/             ← email prompt templates
└── csv/
    ├── input/{campaign-slug}/       ← segmented lists, people, contacts
    └── output/{campaign-slug}/      ← generated emails
```

### Environment Variables

Only the Extruct API token needs to be set upfront. Other providers' credentials are requested in-chat when the corresponding skill runs.

| Variable | Service | Used by |
|----------|---------|---------|
| `EXTRUCT_API_TOKEN` | [Extruct API](https://www.extruct.ai/docs) | list-building, list-enrichment, table-creation, people-search, list-segmentation, email-search |
