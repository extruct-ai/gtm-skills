# Finding Companies

Use this playbook when the user wants to discover companies, shortlist a market, or turn a search prompt into company candidates.

All commands below use `<extruct_api_cli>` as shorthand for the resolved absolute path to this skill's bundled CLI. Resolve that path from the directory containing `SKILL.md` before running any command.

## When To Use It

Use this playbook when the user asks for:

- semantic company discovery from a natural-language query
- similar companies from a known seed company
- a higher-precision asynchronous search with explicit criteria

Do not use this playbook when:

- the user already has a table and wants to operate on it directly
- the user already has companies and wants enrichment columns or scoring
- the user wants people rather than companies

## Choose The Right Search Path

### Use Semantic Search

Use `companies search` when the user describes a market, ICP, category, product, use case, or geography in natural language.

```bash
<extruct_api_cli> companies search --query "AI procurement startups serving enterprise finance teams" --limit 20
```

Add `--filters` when the user specifies geography, size, city, or founded range:

```bash
<extruct_api_cli> companies search --query "enterprise sales AI" \
  --filters '{"include":{"country":["United States"]},"range":{"founded":{"min":2018}}}' \
  --limit 20
```

### Use Lookalike Search

Use `companies similar` when the user already knows a reference company.

- prefer a domain or URL as `--company-identifier`
- use a UUID only when a prior Extruct response already gives you one

```bash
<extruct_api_cli> companies similar --company-identifier stripe.com --limit 20
```

### Use Deep Search

Use Deep Search when the user wants:

- a more deliberate, higher-precision search
- explicit criteria in the output
- an asynchronous workflow with polling

```bash
<extruct_api_cli> deep-search create --payload '{
  "query":"AI procurement startups serving enterprise finance teams",
  "desired_num_results":25
}'
<extruct_api_cli> deep-search poll <task_id>
<extruct_api_cli> deep-search results <task_id> --limit 20
```

Add `criteria` when the user wants explicit scoring dimensions:

```bash
<extruct_api_cli> deep-search create --payload '{
  "query":"vertical SaaS companies serving freight forwarding",
  "desired_num_results":25,
  "criteria":[
    {
      "key":"has_logistics_focus",
      "name":"Logistics Focus",
      "criterion":"Company serves freight forwarding or logistics operations."
    }
  ]
}'
```

## Safe Iteration Rules

- keep the first search narrow enough to inspect manually
- add filters before asking for many more results
- for Deep Search, start with a modest `desired_num_results` unless the user explicitly wants a large run
- if the user wants follow-on enrichment, move shortlisted company domains into a company table

## What To Inspect

- whether the returned companies actually match the intended market
- whether geography or size needs a filter
- whether a seed company was too ambiguous
- whether the user now wants a shortlist only or a reusable company table

## Next Playbooks

- If the user wants enrichment, scoring, or repeatable research over the shortlist, continue to `researching-companies.md`.
- If the user wants people at the discovered companies, continue to `finding-people-at-companies.md`.
