# Writing a strategy plan

Every strategy (door) carries a structured `plan` object that becomes the StrategyPage Plan tab in the dashboard. The plan is what a senior AE would write up in a doc and pass to a teammate inheriting the account — concrete enough to execute against, abstract enough to survive a new buyer surfacing tomorrow.

## Data shape

```js
window.DOOR_PLANS["door-N"] = {
  thesis:         "Why this strategy exists as a distinct play. 3–4 sentences.",
  whyNow:         "Timing: what window is open right now and when it closes.",
  wedge:          "The specific positioning angle. What to lead with, what to avoid.",
  buyerSequence:  [
    {
      person_id:    "p-...",
      rank:         1,                              // sequence order
      rationale:    "Why this person at this position in the sequence.",
      openingMove:  "The exact first move to make with this person.",
    },
    // ... 2–5 buyers in priority order
  ],
  riskTriggers:   ["...", "...", "..."],            // 3–5 concrete failure modes
  proofPoints:    ["s1", "s11", "s13"],             // signal IDs that back the plan
};
```

## How to author each section

### Thesis

Why does this strategy exist as a distinct play *and not a slice of another*? Answer in 3–4 sentences. Lead with the structural fact (public commitment / awarded program / largest budget envelope / net-new buyer layer), then state the wedge in one line.

- **Bad thesis**: "L&D at BASF" *(that's an industry, not a thesis)*
- **Good thesis**: "Corporate strategic L&D is the highest-leverage door because the public AI-skills commitment removes the standard objection in one sentence and the named owner is a senior buyer with a thinner reporting chain than the org chart suggests."

### Why now

Name the dates. Specific weeks and quarters, not generic "recent activity". Identify the window: what triggered it (a signal), what closes it (an event or a calendar boundary), how long the window stays open.

- **Bad why-now**: "There's been recent activity at the company"
- **Good why-now**: "The corporate HR chain thinned twice in twelve months: Spandau exited the SVP Corporate HR seat in July 2025; CEO Kamieth absorbed the portfolio May 1, 2026. The 12-month staging window (May–April) is open. After September 2026 the GES plan locks; Uta's commitment becomes a deliverable, not an opportunity."

Without a calendar boundary, this isn't a why-now — it's a why-this.

### Wedge

The wedge is *what to lead with* and *what to avoid leading with*. Two halves matter equally. If the wedge doesn't tell the rep what NOT to say in the first meeting, it isn't a wedge.

- **Bad wedge**: "we sell adaptive learning"
- **Good wedge**: "Pitch \"qualification infrastructure for transformation programs\" — not \"learning\". Lead with the operating-model question: \"What's the measurement layer that turns the disclosure into capability vs activity?\" Do not pitch a tool; ask the architecture question."

### Buyer sequence

Ordered list, 2–5 people. Each step carries three fields:

- **`rank`** — 1 = engage first, 2 = engage second, etc. *Not seniority; not score. Sequence order.* The top-scored buyer is sometimes second or third in the sequence because they need a warm intro from a champion first. Sort by access, not by title.
- **`rationale`** — 1–2 sentences on why this person at this position. Why not first? Why not last? What does this position give us that the others don't?
- **`openingMove`** — the exact first move. Not "introduce ourselves"; the actual sentence to send or the actual question to ask. The opening move is what the rep will copy-paste.

Example:
```js
{
  person_id: "p-uta-schulz",
  rank: 1,
  rationale: "Strategic ceiling buyer. Named owner of the public AI-skills commitment. Engage her first; everyone else triangulates off her position.",
  openingMove: "Reference the 2025 sustainability statement language verbatim. Ask: \"What's the operating model for measuring capability versus activity?\" Don't pitch adaptive learning. Pitch the question."
}
```

### Risks & blockers

Concrete failure modes, not vague concerns. Each item names what could go wrong **and** how to mitigate it.

- **Bad risk**: "buyer may say no"
- **Good risk**: "Aucoin defaults to 'let the existing L&D team handle this' because he's new to L&D. Mitigate by leading on engineering-skills measurement which is GES-native, not learning-vendor-shaped."

If the risk doesn't have a mitigation, it's not on the list — it's a "kill the strategy" question, not a risk.

### Proof points

Signal IDs only. If a claim in the plan can't be traced to a signal, the claim doesn't go in the plan. Three to five is the right range; more than that means the plan is over-evidenced for a one-pager.

## Anti-patterns

- **The "ranked by score" buyer sequence.** Sequence is about *order of approach*, not seniority. Don't sort by score; reason about access.
- **The "we can also do" wedge.** Adding "we can also help with X" weakens the wedge. The wedge is one positioning. Multiple positionings = no positioning.
- **The "ongoing" why-now.** A why-now without a calendar boundary is a why-this. Calendar boundary or drop the section.
- **The "trust us" risk list.** Every risk must have a concrete failure mode and a concrete mitigation. "Could go wrong" is not a risk.
- **The hand-wavy thesis.** If the thesis can fit on a sales-deck slide as-is, it's marketing copy, not a thesis. The thesis is for the rep, not the prospect.

## Quality check (run before shipping a plan)

A finished plan should pass these five tests:

1. **Repeatability test.** Read the wedge aloud. Could a new rep on the team repeat it back without notes after one read? If no, compress.
2. **First-meeting test.** Pick step 1 of the buyer sequence. Could a rep walk into the meeting tomorrow with just the `openingMove` and run the conversation for 30 minutes? If no, the opening move is too abstract.
3. **Calendar test.** Read the why-now. Is there at least one specific date or quarter? If no, fix it.
4. **Signal trace test.** Pick any claim in the thesis or why-now. Can it be traced to a signal ID in `proofPoints`? If no, either source it or remove it.
5. **Generator test.** Could a Tier 3 LLM agent reading this plan produce 3–5 tasks that pass the existing task quality bar? If no, the plan doesn't have enough material for execution.

The dashboard's StrategyPage Plan tab is the surface this object renders to. Sections that read as "thin" on the rendered page are the sections where the underlying writing wasn't doing the work.
