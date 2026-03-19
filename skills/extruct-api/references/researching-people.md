# Researching People

Use this playbook when the user already has people rows, either from a generated child people table or from their own input, and now wants enrichment or contact data.

All commands below use `<extruct_api_cli>` as shorthand for the resolved absolute path to this skill's bundled CLI. Resolve that path from the directory containing `SKILL.md` before running any command.

## When To Use It

Use this playbook when the user asks to:

- enrich people rows with email, phone, LinkedIn, or derived classifications
- work with a standalone `people` table
- continue after a `company_people_finder` workflow

Do not use this playbook when:

- the user first needs to discover people from companies
- the user only wants company-level research

## Starting State

You need one of these:

- a generated child `people` table, or
- a standalone `people` table with strong person context in each row

## Default Command Flow

### Create A Standalone People Table When Needed

If the user is not starting from a generated child people table, create a `people` table. If you want `email_finder` or `phone_finder`, include a local input column keyed exactly `company_website`.

```bash
<extruct_api_cli> tables create --payload '{
  "name":"Target Contacts",
  "kind":"people",
  "column_configs":[
    {
      "kind":"input",
      "name":"Company Website",
      "key":"company_website"
    }
  ]
}'
```

### Add Or Inspect People Rows

The safest standalone `input` is full name plus LinkedIn URL, and current role if you have it.

```bash
<extruct_api_cli> rows create <people_table_id> --payload '{
  "rows":[
    {
      "data":{
        "input":"Jane Doe, VP Sales, https://linkedin.com/in/jane-doe",
        "company_website":"extruct.ai"
      }
    }
  ],
  "run":false
}'
```

Inspect before adding more enrichment:

```bash
<extruct_api_cli> tables get <people_table_id>
<extruct_api_cli> tables data <people_table_id> --limit 20 --columns input,company_website
```

### Add Contact Or Derived Columns

```bash
<extruct_api_cli> columns add <people_table_id> --payload '{
  "column_configs":[
    {
      "kind":"email_finder",
      "name":"Work Email",
      "key":"work_email"
    },
    {
      "kind":"phone_finder",
      "name":"Direct Phone",
      "key":"direct_phone"
    }
  ]
}'
```

Use `column-guide.md` for `linkedin`, `llm`, `department`, `seniority`, and `reverse_email_lookup` patterns.

### Run, Poll, And Read

```bash
<extruct_api_cli> tables run <people_table_id> --payload '{
  "mode":"new",
  "columns":["<column_id_1>","<column_id_2>"]
}'
<extruct_api_cli> tables poll <people_table_id>
<extruct_api_cli> tables data <people_table_id> --limit 20 --columns input,work_email,direct_phone
```

## Safe Iteration Rules

- separate people discovery from contact enrichment
- confirm `company_website` exists before adding `email_finder` or `phone_finder`
- keep contact enrichment and derived `llm` transformations as separate steps when possible
- use `--columns` on result reads whenever you only need a surgical slice of the data
- remember that `research_pro` is not allowed on `people`-table custom agent columns

## What To Inspect

- whether rows have enough person context
- whether profile URLs and company website context line up
- whether email results belong to the expected domain
- whether phone results are sparse but plausible
- whether derived classifications are grounded in the current role

## Next Playbooks

- If the user first needs people discovery from companies, go back to `finding-people-at-companies.md`.
- If the user wants more company-level enrichment around the same accounts, go to `researching-companies.md`.
