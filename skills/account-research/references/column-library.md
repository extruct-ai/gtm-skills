# Account Research — column library

`research_pro` column configs for the account-research workflow. Each is atomic (one job). Bake the seller context and ICP from the company context file, plus any region focus, into the prompt where marked `[CONTEXT: ...]`. Anchor identity on the row's domain (`{input}`) so research doesn't drift to similarly named companies.

Add these via the `extruct-api` skill, run only the new columns scoped to their ids, then poll to completion before reading.

## Entity tree (the differentiator)

```json
{
  "kind": "agent",
  "name": "Entity structure",
  "key": "entity_structure",
  "value": {
    "agent_type": "research_pro",
    "output_format": "text",
    "prompt": "Atomic task. Anchor strictly on the company at {input}; ignore similarly named entities. Describe its parent-subsidiary / org-chart structure: the holding or parent entity, its divisions or networks, and the operating units beneath them. Large groups run as many separate legal entities across countries. Give the VERIFIED count of consolidated subsidiaries / legal entities and the number of countries if disclosed (annual report, registries). The point: standard databases show one flat record; the real account is a multi-layer tree. Cite source URLs."
  }
}
```

## Open roles

```json
{
  "kind": "agent",
  "name": "Open roles",
  "key": "open_roles",
  "value": {
    "agent_type": "research_pro",
    "output_format": "text",
    "prompt": "Atomic task. Anchor on {input}. List current OPEN job postings relevant to [CONTEXT: target functions and buying signals], with title, location/region, and the careers source URL. Note what the hiring reveals about where budget and headcount are moving. Verified postings only; cite each. If none, say 'not found'."
  }
}
```

## Closed roles

```json
{
  "kind": "agent",
  "name": "Closed roles",
  "key": "closed_roles",
  "value": {
    "agent_type": "research_pro",
    "output_format": "text",
    "prompt": "Atomic task. Anchor on {input}. List recently CLOSED or filled job postings relevant to [CONTEXT: target functions] from the last 6-12 months, with title, region, and the source URL. Closed roles show where headcount actually grew and the team's hiring throughput, which open roles alone do not. Verified only; cite each. If none found, say 'not found'."
  }
}
```

## Leadership changes

```json
{
  "kind": "agent",
  "name": "Leadership changes",
  "key": "leadership_changes",
  "value": {
    "agent_type": "research_pro",
    "output_format": "text",
    "prompt": "Atomic task. Anchor on {input}. List recent (last 12-18 months) leadership changes in [CONTEXT: target functions] — new hires, departures, promotions, reporting-line changes. Each as: date, who, what changed, source URL. A new owner or a vacated seat is a buying-window signal. Verified only."
  }
}
```

## Recent news

```json
{
  "kind": "agent",
  "name": "Recent news",
  "key": "recent_news",
  "value": {
    "agent_type": "research_pro",
    "output_format": "text",
    "prompt": "Atomic task. Anchor on {input}. List dated company events in the last 12-18 months: M&A, rebrands, product launches, partnerships, funding, expansion, major customer wins. Each as one line: date, event, source URL. Verified only."
  }
}
```

## Tech stack

```json
{
  "kind": "agent",
  "name": "Tech stack",
  "key": "tech_stack",
  "value": {
    "agent_type": "research_pro",
    "output_format": "text",
    "prompt": "Atomic task. Anchor on {input}. Identify the CRM and [CONTEXT: the relevant tooling category the offer sits beside] with evidence: job descriptions that name tools, BuiltWith, employee profiles. Each detection cites its source. If only inferred, label inferred. If not found, say 'not found' rather than guessing."
  }
}
```

## Division focus

```json
{
  "kind": "agent",
  "name": "Division focus",
  "key": "division_focus",
  "value": {
    "agent_type": "research_pro",
    "output_format": "text",
    "prompt": "Atomic task. Anchor on {input}. For each main division or operating unit, state what it is currently focused on or investing in. Each division is a distinct buying center with its own priorities. Cite sources."
  }
}
```

## Adding ICP-specific columns

For segmentation or personalization signals tied to a specific ICP, design columns with the `enrichment-design` skill and add them here the same way. Keep each atomic and sourced.
