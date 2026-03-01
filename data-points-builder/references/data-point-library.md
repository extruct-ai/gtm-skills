# Data Point Library

Pre-built column configs organized by use case. Copy and customize for your campaign.

## Segmentation Columns

### Company Size & Stage

```python
{
    "kind": "agent", "name": "Employee Count Bucket", "key": "employee_bucket",
    "value": {
        "agent_type": "llm",
        "prompt": "Based on the company profile for {input}, classify employee count into one of these buckets. Return ONLY the label.",
        "output_format": "select",
        "labels": ["1-10", "11-50", "51-200", "201-500", "500+"]
    }
}
```

```python
{
    "kind": "agent", "name": "Funding Stage", "key": "funding_stage",
    "value": {
        "agent_type": "research_pro",
        "prompt": "Find the latest funding round for {input}. Return the stage name only (e.g., Seed, Series A, Series B). If bootstrapped or unknown, return 'Bootstrapped'. If public, return 'Public'.",
        "output_format": "select",
        "labels": ["Bootstrapped", "Seed", "Series A", "Series B", "Series C+", "Public"]
    }
}
```

### Technology & Infrastructure

```python
{
    "kind": "agent", "name": "CRM Platform", "key": "crm_platform",
    "value": {
        "agent_type": "research_pro",
        "prompt": "What CRM or sales platform does {input} use? Look for evidence in job postings, case studies, or tech stack databases. Return the platform name (e.g., Salesforce, HubSpot, Pipedrive). If unknown, return 'Unknown'.",
        "output_format": "text"
    }
}
```

```python
{
    "kind": "agent", "name": "Tech Stack Maturity", "key": "tech_maturity",
    "value": {
        "agent_type": "research_reasoning",
        "prompt": "Assess the technology maturity of {input}. Consider: do they have a modern website? Do they use cloud services? Do job postings mention modern tools? Rate 1 (minimal tech) to 5 (advanced).",
        "output_format": "grade"
    }
}
```

### Market Position

```python
{
    "kind": "agent", "name": "Geographic Coverage", "key": "geo_coverage",
    "value": {
        "agent_type": "research_pro",
        "prompt": "How many locations, offices, or markets does {input} operate in? Classify as: Local (1 city), Regional (1 state/region), National (multiple states), International. Return ONLY the label.",
        "output_format": "select",
        "labels": ["Local", "Regional", "National", "International"]
    }
}
```

```python
{
    "kind": "agent", "name": "Primary Vertical", "key": "primary_vertical",
    "value": {
        "agent_type": "llm",
        "prompt": "Based on the company profile for {input}, what is their primary industry vertical? Return a specific label, not a broad category. Examples: 'SaaS', 'Logistics', 'Healthcare', 'Manufacturing'. Return one label only.",
        "output_format": "text"
    }
}
```

## Personalization Columns

### Leadership & Public Signals

```python
{
    "kind": "agent", "name": "CEO Public Statement", "key": "ceo_statement",
    "value": {
        "agent_type": "research_pro",
        "prompt": "Find a recent public statement, interview, blog post, or LinkedIn post by the CEO or founder of {input}. Focus on their views about [TOPIC]. Return a 1-2 sentence summary with the source URL. If nothing found, return 'No public statements found'.",
        "output_format": "text"
    }
}
```

```python
{
    "kind": "agent", "name": "Recent News", "key": "recent_news",
    "value": {
        "agent_type": "research_pro",
        "prompt": "Find the most significant news about {input} from the last 6 months. Focus on: product launches, partnerships, funding, leadership changes, or expansion. Return a 1-sentence summary with date. If nothing found, return 'No recent news'.",
        "output_format": "text"
    }
}
```

### Hiring Signals

```python
{
    "kind": "agent", "name": "Key Hiring Signals", "key": "hiring_signals",
    "value": {
        "agent_type": "research_pro",
        "prompt": "Check if {input} is currently hiring for roles related to [FUNCTION]. Look at their careers page and job boards. Return: role title(s) and what it signals about their priorities. If no relevant openings, return 'No relevant openings'.",
        "output_format": "text"
    }
}
```

### Competitive Context

```python
{
    "kind": "agent", "name": "Current Tools", "key": "current_tools",
    "value": {
        "agent_type": "research_pro",
        "prompt": "What tools or platforms does {input} currently use for [FUNCTION]? Look in job postings, case studies, tech directories, and G2 reviews. Return tool names. If unknown, return 'Unknown'.",
        "output_format": "text"
    }
}
```

## Hypothesis Scoring Columns

### Template: Binary Hypothesis Match

```python
{
    "kind": "agent", "name": "Hypothesis: [NAME]", "key": "hyp_[key]",
    "value": {
        "agent_type": "research_reasoning",
        "prompt": "Evaluate whether {input} matches this hypothesis: '[HYPOTHESIS DESCRIPTION]'. Look for evidence that confirms or denies this. Return a JSON object.",
        "output_format": "json",
        "output_schema": {
            "type": "object",
            "properties": {
                "match": {"type": "boolean"},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                "evidence": {"type": "string"}
            }
        }
    }
}
```

### Template: Hypothesis Fit Score

```python
{
    "kind": "agent", "name": "Fit: [HYPOTHESIS]", "key": "fit_[key]",
    "value": {
        "agent_type": "research_reasoning",
        "prompt": "Rate how well {input} fits this hypothesis on a 1-5 scale: '[HYPOTHESIS]'. 1 = no fit, 3 = possible fit, 5 = strong fit. Consider: [SPECIFIC CRITERIA]. Return ONLY a number.",
        "output_format": "grade"
    }
}
```

## Combo Patterns

### Segmentation + Personalization (5-column setup)

1. Primary Vertical (select) — segmentation
2. Company Size Bucket (select) — segmentation
3. Hypothesis Fit Score (grade) — segmentation
4. Recent News (text) — personalization
5. Leadership Statement (text) — personalization

### Pure Segmentation (4-column setup)

1. Primary Vertical (select)
2. Tech Maturity (grade)
3. Geographic Coverage (select)
4. Hypothesis Match (json with match + evidence)

### Pure Personalization (3-column setup)

1. CEO Public Statement (text)
2. Recent Product Launch (text)
3. Current Tools for [function] (text)
