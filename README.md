![Extruct](docs/images/cover.png)

# GTM Skills by Extruct

Run outbound campaigns end-to-end with [Extruct](https://www.extruct.ai) and [Claude Code](https://docs.anthropic.com/en/docs/claude-code/skills). Research, list building, enrichment, segmentation, email generation, and sending. Use one [skill](https://docs.anthropic.com/en/docs/claude-code/skills) or combine several. Each works independently.

For updates, follow [Danny Chepenko on LinkedIn](https://br.linkedin.com/in/danielchepenko).

## Getting Started

### 1. Install skills

Via [skills.sh](https://skills.sh) CLI ([repo](https://github.com/vercel-labs/skills)):

```
npx skills add extruct-ai/gtm-skills
```

Or via [Claude Code](https://docs.anthropic.com/en/docs/claude-code/skills) plugin manager:

```
/plugin marketplace add extruct-ai/gtm-skills
/plugin install gtm-skills
```

Skills are stored in `~/.claude/skills/`. Install once, use everywhere across all your projects.

**Updating:** re-run `npx skills add extruct-ai/gtm-skills` to pull the latest version, or `npx skills update` to update all installed skills at once. For the plugin manager, run `/plugin marketplace update` to refresh and get the latest versions.

### 2. Get your Extruct API token

Sign up at [extruct.ai](https://www.extruct.ai) (free trial with 100 credits) and grab your API token from the dashboard.

The token is needed for company search, table creation, enrichment, and people search. Skills that don't call the Extruct API (context-building, hypothesis-building, email-prompt-building, email-generation) work without it.

Set the token in your terminal:

```
export EXTRUCT_API_TOKEN=<your-token>
```

If you skip this step, skills will ask for the token in chat when they need it.

### 3. Run your first workflow

Describe what you need in Claude Code:

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

Use one, combine a few, or run them all. No required sequence, each skill works independently.

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
| **email-verification** | Validate emails via verification provider before sending |
| **email-response-simulation** | Simulate prospect reading your email (Tier 1 review) |
| **campaign-sending** | Upload leads for sequencing and sending |
| **inbox-reply** | Manage and reply to lead responses in the email sequencing inbox |
| **competitor-monitoring** | Track competitors with enrichment-powered monitoring tables |
| **post-engagers** | Extract engagers from any LinkedIn post and load into Extruct |
| **extruct-api** | Bundled Extruct API reference — used by other skills for all API operations |

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

| Variable | Service | Used by |
|----------|---------|---------|
| `EXTRUCT_API_TOKEN` | [Extruct API](https://www.extruct.ai/docs) | list-building, list-enrichment, table-creation, people-search, list-segmentation, email-search |

Other providers' credentials (email enrichment, sequencing, deep research) are requested in chat when the corresponding skill runs.
