# Output shape — `extruct-research/accounts/{slug}.js`

The dashboard at `extruct-research/` is account-agnostic. It mounts whatever data lives in `accounts/{slug}.js`. This file defines the exact `window.*` globals the dashboard expects. The helpers in `src/lib/helpers.js` build derived lookups on top of these.

Treat this as a hard interface. The dashboard renders nothing useful if any required global is missing or has a wrong shape.

## What you provide

```js
window.ACCOUNT       // metadata + hero strip
window.TLDR          // AI summary (left rail of Tasks tab)
window.DOORS         // 3–4 strategies (formerly "doors")
window.DOOR_PLANS    // per-strategy thesis + plan
window.SIGNALS       // sourced events (10–30 typical)
window.FLAGS         // time-bounded windows (2–5 typical)
window.TECH          // tech-stack detections with evidence
window.TEAMS         // internal team/academy list
window.PEOPLE        // 10–15 curated named buyers
window.PERSON_SIGNAL // person↔signal tagging (Tier 1/2/3)
window.SUBSIDIARIES  // legal entities / divisions
window.TEAM_MEMBERS  // team name → array of (name, role, linkedin, email, refId?)
window.SUBSIDIARY_MEMBERS  // subsidiary id → array of same shape
window.SUBSIDIARY_SIGNALS  // subsidiary id → signal ids
window.TECH_CATEGORIES     // tech-stack groupings
window.ACADEMIES           // internal L&D programs
window.PLAYBOOKS           // task category → hue
window.TASKS               // 15–25 actionable tasks
```

## What you don't provide

These are computed by `src/lib/helpers.js` from the data above. Don't redeclare them:

- `SIGNAL_BY_ID`, `PERSON_BY_ID`, `SUBSIDIARY_BY_ID`, `TASK_BY_ID` — ID lookups
- `STRATEGY_NAME_BY_DOOR`, `getStrategyName` — strip "Door N:" prefix for display
- `getSignalStrategies`, `getDoorByLabel`, `getRelatedForSignal`, `getSignalsForPerson` — joins
- `getTeamMembers`, `getSubsidiaryMembers`, `getSubsidiarySignals` — accessors
- `getAllPeople` — memoized dedupe of TEAM_MEMBERS + SUBSIDIARY_MEMBERS
- `getTasksForStrategy`, `getDoorPlan` — task / plan accessors
- The Tier-1 bootstrap that promotes each `p.signals[]` entry into a PERSON_SIGNAL row
- The `actioned: true` → `status: "actioned"` promotion for tasks

## Field-by-field

### `window.ACCOUNT`

```js
window.ACCOUNT = {
  name: "BASF",                                    // string
  version: "Brief v4",                             // string, shown in AI summary chip
  domain: "basf.com",                              // string
  description: "BASF is the world's largest...",   // 1–2 sentences for the hero
  attributes: [
    { icon: "industry",  label: "Chemicals & Materials" },
    { icon: "headcount", label: "111,000 headcount" },
    { icon: "hq",        label: "HQ in Ludwigshafen, DE" },
    { icon: "parent",    label: "Parent of 38 orgs" },
    { icon: "url",       label: "basf.com", external: true },
    { icon: "linkedin",  label: "BASF", external: true },
    { icon: "type",      label: "Public · DAX 40" },
  ],
};
```

`icon` values supported: `industry`, `headcount`, `hq`, `parent`, `aka`, `url`, `linkedin`, `type`.

### `window.TLDR`

```js
window.TLDR = {
  thesis: "BASF is under cost pressure but cannot solve...",
  why_now: [
    { label: "CoreShift", text: "creates executive urgency.", detail: "CEO-level cost-out program announced..." },
    { label: "Ludwigshafen", text: "creates workforce-productivity pressure.", detail: "December 2025 site agreement..." },
    // 3–5 entries
  ],
  best_wedge: {
    avoid: "Do not pitch \"learning.\"",
    pitch: "qualification infrastructure for transformation programs",
  },
  first_path: "Start with GBS / People Services...",
  second_path: "Use Coatings and Agricultural Solutions...",
};
```

Only the thesis · why_now · best_wedge are surfaced in the Tasks left rail. first_path and second_path are stored but currently hidden from the rail.

### `window.DOORS`

```js
window.DOORS = [
  {
    id: "door-1",
    title: "Door 1: Human Capability Future",      // "Door N: <strategy name>"
    subtitle: "Strategic L&D, corporate",          // displayed under name
    hue: "indigo",                                 // see hue palette below
    macro: "AI-supported skills management is already in BASF's 2025 sustainability statement...",
    top: [                                         // legacy preview; can be empty
      { name: "Uta Schulz", role: "Head of Human Capability Future" },
    ],
  },
  // 3–4 doors total
];
```

**Hue palette**: `indigo`, `blue`, `purple`, `mint`, `green`, `teal`, `orange`, `yellow`, `pink`, `cyan`. Each maps to predefined CSS tokens.

### `window.DOOR_PLANS`

See [strategy-plans.md](strategy-plans.md) for the full authoring guide. Shape:

```js
window.DOOR_PLANS = {
  "door-1": {
    thesis: "...",
    whyNow: "...",
    wedge: "...",
    buyerSequence: [
      { person_id: "p-uta-schulz", rank: 1, rationale: "...", openingMove: "..." },
      // 2–5 buyers
    ],
    riskTriggers: ["...", "...", "..."],
    proofPoints: ["s1", "s11", "s13"],
  },
  // one entry per door
};
```

### `window.SIGNALS`

```js
window.SIGNALS = [
  {
    id: "s1",                                      // sN convention
    title: "AI-supported skills + competencies management in HR systems",
    date: "2025-12-31",                            // ISO 8601
    confidence: "H",                               // H / M / L
    sourceLabel: "BASF Sustainability (publications landing)",
    sourceUrl: "https://www.basf.com/...",         // CURL-VERIFIED 2xx (or 999 for LinkedIn)
    sourceType: "primary",                         // primary / social / profile / derived
    sourceCount: 1,
    quote: "BASF integrated AI-supported skills...",
    bucket: "AI / L&D",                            // human-readable category
    bucketHue: "blue",                             // hue palette
    why: "Direct match for Area9's category. Self-disclosed by BASF in primary materials.",
    context: "Optional jargon explanation for the signal page.",
    new: true,                                     // optional NEW pill
  },
  // 10–30 signals typical
];
```

If `sourceType: "derived"`, set `sourceUrl: null` and the dashboard renders a "Derived" pill instead of a broken link.

### `window.FLAGS`

```js
window.FLAGS = [
  {
    id: "flag-1",
    title: "Coatings carve-out: Carlyle/QIA close Q2 2026",
    severity: "high",                              // high / medium / low
    deadline: "Q2 2026",
    updated: "2026-03-26",
    summary: "Jens Luehring NAMED as incoming CEO post-close...",
    contacts: [
      { name: "Jens Luehring", role: "Incoming CEO, BASF Coatings", priority: "strategic" },
    ],
  },
  // 2–5 flags typical
];
```

### `window.TECH`

```js
window.TECH = [
  {
    name: "SAP SuccessFactors BizX",
    category: "HRIS · core",
    status: "confirmed",                           // confirmed / partial / inferred
    note: "Likely native LMS. Area9 sits as adaptive layer above.",
    logo: "sap",                                   // optional
    source: { kind: "signal", id: "s8", label: "Ege Ozoktas · LinkedIn title" },
  },
  {
    name: "FLOWSPARKS",
    category: "Specialty authoring",
    status: "partial",
    note: "Public case study referenced; URL not yet captured.",
    source: { kind: "needed", label: "Need case-study URL" },
  },
  // ...
];
```

**Source kinds**:
- `signal` — references a signal ID; renders as clickable chip to SignalPage
- `url` — external URL; renders as link
- `derived` — rules-based inference; renders as muted label
- `inferred` — industry baseline; renders as muted label
- `needed` — proof is missing; renders italic in warning color

Only `confirmed` items should have a `signal` or `url` source. `partial` and `inferred` are honest downgrades.

### `window.TEAMS`

```js
window.TEAMS = [
  {
    name: "Human Capability Future Unit",
    function: "Strategic L&D",
    size: 12,                                      // approximate headcount
    signals: 3,                                    // signal count tagged to team
    head: "Uta Schulz",                            // human-readable name
    site: "Ludwigshafen",
    doors: ["Door 1"],                             // array of Door N labels
    isNew: false,                                  // optional NEW pill
  },
  // 8–20 teams typical
];
```

### `window.PEOPLE`

```js
window.PEOPLE = [
  {
    id: "p-uta-schulz",                            // p-{firstname-lastname} convention
    name: "Uta Schulz",
    role: "Head of Human Capability Future",
    company: "BASF SE",
    location: "Ludwigshafen, DE",
    avatar: "US",                                  // 2-letter monogram
    avatarHue: "indigo",
    door: "Door 1",                                // primary door
    doorHue: "indigo",
    bucket: "L&D",
    seniority: "Head",                             // Head / VP / Director / Senior Manager / ...
    rank: 1,                                       // 1 = highest-priority
    score: 96,                                     // 0–100; bucket × seniority × signal density
    signals: ["s1", "s2", "s3"],                   // signal IDs (becomes Tier-1 PERSON_SIGNAL rows)
    angle: "Uta runs the Human Capability Future Unit, the named owner of the AI-supported skills management...",
    linkedin: "http://www.linkedin.com/in/uta-schulz-3246ba5",
    email: "uta.schulz@basf.com",                  // optional
    activity: [
      { type: "linkedin", date: "2026-05-12", text: "Reposted Sarah Grisard's note..." },
      { type: "speaking", date: "2026-03-08", text: "Panel at HR Frühjahrstagung..." },
    ],
    isNew: false,                                  // optional NEW pill
  },
  // 10–15 curated buyers
];
```

### `window.PERSON_SIGNAL`

```js
window.PERSON_SIGNAL = [
  {
    person_id: "p-uta-schulz",
    signal_id: "s1",
    tier: 1,                                       // 1 / 2 / 3
    confidence: 0.95,                              // 0–1
    role_category: "owner",                        // owner / accountable / affected / champion / mentioned
    rationale: "Named owner of the Human Capability Future Unit, which the 2025 Sustainability Statement credits...",
  },
  // 30–80 rows typical (each person × tagged signals)
];
```

The helpers will automatically promote each `p.signals[]` ID into a Tier-1 PERSON_SIGNAL row at load time if not already present — so you only need to declare the Tier 2 / Tier 3 rows explicitly.

### `window.SUBSIDIARIES`

```js
window.SUBSIDIARIES = [
  {
    id: "basf-se",
    name: "BASF SE",
    domain: "basf.com",
    type: "Parent · Holding",
    employees: 111000,
    site: "Ludwigshafen, DE",
    logoHue: "blue",                               // hue palette
    initials: "B",                                 // 1–2 char logo
    signals: 7,                                    // count
    isNew: false,
    flag: null,                                    // or { label, severity } if tied to a flag
    note: "Top-level holding entity...",
  },
  // 5–40 subsidiaries typical
];
```

### `window.TEAM_MEMBERS` / `window.SUBSIDIARY_MEMBERS`

The Apollo-enriched roster. Same shape, keyed differently:

```js
window.TEAM_MEMBERS = {
  "Human Capability Future Unit": [
    {
      name: "Uta Schulz",
      role: "Head of Human Capability Future",
      avatar: "US",
      avatarHue: "indigo",
      linkedin: "http://www.linkedin.com/in/uta-schulz-3246ba5",
      email: "uta.schulz@basf.com",
      location: "Ludwigshafen, Germany",
      refId: "p-uta-schulz",                       // if person is in window.PEOPLE
    },
    // ... more team members
  ],
  // ... more teams
};
```

`refId` links team-member rows to curated PEOPLE records. The dashboard uses this to render a "Named" pill on rows that map to a curated buyer.

### `window.PLAYBOOKS` and `window.TASKS`

See [the methodology runbook's task section](methodology.md#strategies--tasks-the-generation-rule) for the full task data shape. Quick reference:

```js
window.PLAYBOOKS = {
  "New decision maker":    { hue: "purple" },
  "Multi-thread":          { hue: "indigo" },
  // ... 10–16 playbooks
};

window.TASKS = [
  {
    id: "task-001",
    playbook: "Sourced commitment",                // must exist in PLAYBOOKS
    title: "Anchor Uta Schulz on her own 2025 sustainability disclosure",
    whyNow: "Uta is the named program owner of the AI-supported skills...",
    whySources: [{ kind: "signal", id: "s1" }],
    strategyId: "door-1",                          // must exist in DOORS
    primaryPersonId: "p-uta-schulz",
    multithreadPersonIds: [],
    timeSensitive: false,
    deadline: null,
    priority: 1,                                   // 1–3
    status: "active",                              // active / actioned / snoozed / dismissed
    createdAt: "2026-05-28",
    actioned: false,                               // shortcut → sets status: "actioned"
  },
  // 15–25 tasks total
];
```

For tasks tied to people not in `PEOPLE` (e.g. flag contacts), use `primaryPersonExternal` instead:

```js
{
  primaryPersonId: null,
  primaryPersonExternal: { name: "Jens Luehring", role: "Incoming CEO, BASF Coatings", location: "Münster, DE" },
  multithreadExternal: [{ name: "Sebastian Lindemann", role: "...", location: "..." }],
  // ...
}
```

## Verification checklist

Before declaring the data file done, verify:

1. **Every `sourceUrl` curl-returns 2xx** (or 999 for LinkedIn anti-bot). 404s break trust.
2. **Every `id` is unique** within its array (no duplicate signal IDs, person IDs, task IDs).
3. **`PERSON_SIGNAL` references valid `person_id` + `signal_id`** — no dangling refs.
4. **`TASKS[].strategyId` matches a `DOORS[].id`** — no orphan tasks.
5. **`TASKS[].playbook` exists in `PLAYBOOKS`** — no unmapped playbook hues.
6. **`DOOR_PLANS` has an entry for every door** (or at least the ones you authored plans for).
7. **No vendor names anywhere** (Apollo, PredictLeads) — strip these from sourceLabels.
8. **Dashboard loads via puppeteer** with no `pageerror` events.
