# Tiering Framework

Detailed decision matrix for assigning companies to tiers.

## Tier Decision Matrix

| Signal | Tier 1 | Tier 2 | Tier 3 |
|--------|--------|--------|--------|
| Hypothesis fit score (if grade column) | 4-5 | 2-3 | 1 or N/A |
| Enrichment fields populated | 4+ of 5 | 2-3 of 5 | 0-1 of 5 |
| Hook signal available | Yes (specific) | Generic only | None |
| Company profile depth | Rich description + recent data | Basic description | Minimal or stale |
| Vertical match to hypothesis | Exact | Adjacent | No match |

## Scoring Formula (optional)

If you want a numeric score per company:

```
tier_score = (hypothesis_fit * 0.4) + (data_richness * 0.3) + (hook_available * 0.3)

Where:
- hypothesis_fit: 0-5 (from grade column or manual assessment)
- data_richness: 0-5 (count of populated fields / total fields * 5)
- hook_available: 0 (no hook), 3 (generic hook), 5 (specific hook)

Tier 1: score >= 3.5
Tier 2: score >= 2.0
Tier 3: score < 2.0
```

## Tier-Specific Actions

### Tier 1: Full Personalization Pipeline

1. Run through `email-generation` with hypothesis + hook signal
2. Review each email via `copy-feedback` (Perplexity persona research)
3. Iterate until satisfied
4. Upload to Instantly in a separate, high-touch campaign

**Expected volume:** 10-20% of list (20-50 companies)
**Email quality:** Highly personalized P1 with specific hook

### Tier 2: Templated with Hypothesis Variation

1. Run through `email-generation` with hypothesis only (no individual hooks)
2. Group by hypothesis — each group gets a slightly different P1
3. Spot-check 5-10 emails for quality
4. Upload to Instantly in main campaign

**Expected volume:** 50-60% of list (100-300 companies)
**Email quality:** Hypothesis-personalized but not individually researched

### Tier 3: Hold or Re-Process

Options:
1. **Re-enrich:** Run additional enrichment columns to fill gaps
2. **Different campaign:** Save for a broader, less-targeted campaign
3. **Drop:** If the company truly doesn't fit any hypothesis

**Expected volume:** 20-30% of list
**Email quality:** Do not email until upgraded to Tier 2+

## Common Tier Distribution Issues

| Issue | Fix |
|-------|-----|
| 80%+ in Tier 3 | Hypotheses don't match the list — re-run `market-problems-deep-research` or rebuild the list |
| 50%+ in Tier 1 | Tiering too lenient — tighten the hook signal requirement |
| 0% in Tier 1 | No personalization columns — run `data-points-builder` in personalization mode |
| Even split across all 3 | Usually correct — proceed with pipeline |
