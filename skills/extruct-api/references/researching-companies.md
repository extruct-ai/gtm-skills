# Researching Companies

Use this playbook when the user wants to enrich companies, add custom research fields, or score a set of companies in a reusable table workflow.

All commands below use `<extruct_api_cli>` as shorthand for the resolved absolute path to this skill's bundled CLI. Resolve that path from the directory containing `SKILL.md` before running any command.

## When To Use It

Use this playbook when the user asks to:

- create a company table and populate it with companies
- add research columns such as funding, pricing, news, or competitors
- rerun only new company research columns
- inspect enriched company-table results

Do not use this playbook when:

- the user only wants one-off company discovery
- the user mainly wants people rather than company-level research

## Starting State

You need one of these:

- an existing `company` table, or
- a shortlist of company domains or URLs that can become table rows

## Default Command Flow

### Start A New Company Table

Create the table:

```bash
<extruct_api_cli> tables create --payload '{
  "name":"Target Accounts",
  "kind":"company"
}'
```

Add rows:

```bash
<extruct_api_cli> rows create <table_id> --payload '{
  "rows":[
    {"data":{"input":"extruct.ai"}},
    {"data":{"input":"stripe.com"}}
  ],
  "run":false
}'
```

### Extend An Existing Company Table

Inspect before mutating:

```bash
<extruct_api_cli> tables get <table_id>
<extruct_api_cli> columns list <table_id>
<extruct_api_cli> tables data <table_id> --limit 20
<extruct_api_cli> tables data <table_id> --limit 20 --columns company_name,company_website
```

### Add Columns

Design columns from `column-guide.md`, then add them:

```bash
<extruct_api_cli> columns add <table_id> --payload '{ "column_configs":[ ... ] }'
```

### Run Only The New Work

```bash
<extruct_api_cli> tables run <table_id> --payload '{
  "mode":"new",
  "columns":["<new_column_id_1>","<new_column_id_2>"]
}'
<extruct_api_cli> tables poll <table_id>
```

### Read Results

```bash
<extruct_api_cli> tables data <table_id> --limit 20 --offset 0 --columns company_name,latest_funding
```

## Safe Iteration Rules

- prefer built-in company columns before custom prompts
- add a small number of new columns at a time
- use `mode: "new"` and explicit column ids for incremental work
- inspect a small result page before adding more layers, and project only the fields the user asked about
- if one prompt is trying to do multiple jobs, split it into separate columns

## What To Inspect

- whether each column answers one clear question
- whether output formats are structured enough for downstream use
- whether `Not found` behavior is acceptable
- whether a downstream `llm` transformation should replace an extra research column

## Next Playbooks

- If the user wants to discover more companies first, go back to `finding-companies.md`.
- If the user now wants people at the researched companies, continue to `finding-people-at-companies.md`.
