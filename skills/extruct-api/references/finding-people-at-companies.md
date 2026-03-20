# Finding People At Companies

Use this playbook when the user starts with companies and wants people, leadership, or contactable decision-makers at those companies.

All commands below use `<extruct_api_cli>` as shorthand for the resolved absolute path to this skill's bundled CLI. Resolve that path from the directory containing `SKILL.md` before running any command.

## When To Use It

Use this playbook when the user asks to:

- find leadership or decision-makers at a set of companies
- branch from company rows into a people workflow
- generate a child people table from company context

Do not use this playbook when:

- the user already has people rows and wants direct people enrichment
- the user only wants company-level research

## Starting State

You need a `company` table with the correct company rows.

## Default Command Flow

### Inspect The Company Table

```bash
<extruct_api_cli> tables get <company_table_id>
<extruct_api_cli> columns list <company_table_id>
```

### Add A `company_people_finder` Column

Use broader role families when you want more coverage and exact titles when you want a narrower search.

```bash
<extruct_api_cli> columns add <company_table_id> --payload '{
  "column_configs":[
    {
      "kind":"company_people_finder",
      "name":"Decision Makers",
      "key":"decision_makers",
      "value":{
        "roles":["VP Sales","sales leadership","revenue operations"]
      }
    }
  ]
}'
```

### Run Only The New Finder Column

```bash
<extruct_api_cli> tables run <company_table_id> --payload '{
  "mode":"new",
  "columns":["<people_finder_column_id>"]
}'
<extruct_api_cli> tables poll <company_table_id>
```

### Find The Generated Child People Table

Inspect the parent table and read `child_relationships`:

```bash
<extruct_api_cli> tables get <company_table_id>
```

Typical relationship shape:

```json
{
  "child_relationships": [
    {
      "table_id": "people-table-uuid",
      "relationship_type": "company_people"
    }
  ]
}
```

### Inspect The People Rows Before Contact Enrichment

```bash
<extruct_api_cli> tables get <people_table_id>
<extruct_api_cli> tables data <people_table_id> --limit 20 --columns input,company_website
```

## Safe Iteration Rules

- run the people finder by itself before adding contact columns
- use broader role families for coverage and narrower titles only when needed
- validate the generated people rows before adding email or phone lookups
- treat the child people table as its own workflow boundary

## What To Inspect

- whether the generated roles match the user intent
- whether the profile URLs look plausible
- whether zero-result companies look like true zero-result cases
- whether the child people table has enough quality to justify contact enrichment

## Next Playbooks

- Continue to `researching-people.md` to add email, phone, LinkedIn, or derived people columns.
- If the company table itself still needs more company research first, go back to `researching-companies.md`.
