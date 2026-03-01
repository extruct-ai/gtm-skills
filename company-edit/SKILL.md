---
name: company-edit
description: >
  Format raw company data into consistent, publishable lists for blog articles. Triggers on: "format companies", "company list", "format list", "edit company list".
---

# Format Company List

Format raw company data into a consistent, publishable list for blog articles.

## Input
$ARGUMENTS

## Formatting Rules

### Every company entry MUST include a YC batch
No exceptions. If a batch is missing, look it up on ycombinator.com/companies before formatting. Every company appears as either a "detailed" or "minimal" entry.

### Detailed entry format (top entries per category)
```
- Company Name (Batch, $Funding Round): One-liner description
```

Examples:
- Cofactr (W22, $17.2M Series A): Electronic component supply chain intelligence
- Topological (S25): Physics-based CAD optimization, 1930x faster than current methods
- Gridware (W21, $55M growth round): Wildfire prevention through real-time grid monitoring

### Category header format
```
*Category Name*
```

### What goes in parentheses
- YC batch: always required — (W24), (S25), (X25), (F25)
- Funding: only if the user provided it — $17.2M Series A, $44M Series B, $4M seed
- Nothing else. No "ex-Tesla", no "Germany", no team background, no valuations

### What goes after the colon
- Short factual one-liner. One sentence max.
- No em-dashes, no elaboration, no second clause

### Every company gets a one-liner
- No minimal/comma-separated entries. Every company is a detailed entry with a one-liner description.

## Critical constraints
1. ONLY format companies the user explicitly provides. Never add companies from research files or memory.
2. NEVER skip a company the user listed.
3. If a batch is unknown, search ycombinator.com/companies to find it before outputting.
4. Do not reorder categories unless the user asks.
5. Do not merge or split categories unless the user asks.

## Output
Return the formatted company list ready to paste into the article. Nothing else — no commentary, no changelog, no explanations.
