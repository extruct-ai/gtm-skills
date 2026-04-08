# Generation Script Template

Python script that reads a prompt template + contact CSV, calls the LLM API per row, and writes emails to CSV and MD.

## Usage

```bash
python3 generate_emails.py \
  --prompt prompts/{vertical}/en_first_email.md \
  --contacts csv/input/{campaign}/contacts.csv \
  --output csv/output/{campaign}/emails \
  [--enrichment csv/input/{campaign}/enrichment.csv]
```

## Script structure

```python
#!/usr/bin/env python3
"""
Email generation script.
Reads a prompt template + contact CSV, calls the API per row,
writes emails to CSV and MD.
"""
import csv, json, os, sys, argparse
from pathlib import Path

# 1. Parse arguments: --prompt, --contacts, --output, --enrichment (optional)
# 2. Read the prompt template as the system/user prompt
# 3. Read the contact CSV into a list of dicts
# 4. If --enrichment is provided, merge enrichment data by matching key (e.g., company_name or email)
# 5. For each CSV row:
#    a. Format the row data as JSON
#    b. Append to the prompt as the per-contact context
#    c. Call the API and parse the JSON response
#    d. Accumulate the result
#    e. Print progress (row N/total, company name, subject line)
# 6. Write all results to CSV (for sequencer upload)
# 7. Write all results to MD (for human review, one email per section)
```

## Output format

**CSV columns:** `recipient_name`, `recipient_company`, `email`, `subject`, `body`

**MD format:**
```markdown
# Campaign: {campaign-slug}

## 1. {recipient_name} — {recipient_company}
**Subject:** {subject}

{body}

---
```

## Adapting to API provider

- **Anthropic:** use `anthropic` SDK, `client.messages.create()`
- **OpenAI:** use `openai` SDK, `client.chat.completions.create()`

Set the prompt template as the system message. Pass each contact row as the user message. Parse the JSON response for subject + body.
