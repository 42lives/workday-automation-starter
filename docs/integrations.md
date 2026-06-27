# Optional Integrations

Workday Automation Starter is local-first by default.

The repository works with sample files and sanitized exports. Users should be able to run every core workflow without connecting Gmail, Google Calendar, Notion, OpenAI, or any other account.

## Integration Modes

### 1. Sample Mode

Use the committed examples:

- `examples/emails/sample-inbox.txt`
- `examples/calendar/sample-week.csv`

This is the safest mode for learning, tests, demos, and public issues.

### 2. Export Mode

Use user-owned exports that stay outside the repository:

```bash
python3 -m workday_automation_starter daily-report \
  --emails ~/Exports/gmail-week.txt \
  --calendar ~/Exports/calendar-week.csv \
  --period weekly
```

Do not commit real exports.

### 3. Optional Connector Mode

Future Gmail, Google Calendar, or Notion integrations should be optional.

Good connector behavior:

- ask for explicit user approval,
- store no tokens in the repository,
- keep real account data out of git,
- show a preview before writing to Notion or a document,
- support local export fallback,
- document what data is read and what data is written.

Bad connector behavior:

- requiring account login for basic examples,
- committing OAuth tokens or database IDs,
- auto-sending emails or publishing pages without review,
- silently uploading private files to external services.

## Email Reply Assistant Boundary

`email-reply-assistant` creates local reply drafts and a Notion-ready CSV first:

```bash
python3 -m workday_automation_starter email-reply-assistant \
  --emails ~/Exports/gmail-last-24h.txt \
  --output-dir ~/Automation/email-reply-review \
  --important-sender partner@example.com \
  --since-hours 24
```

Future connectors may:

- fetch Gmail messages from the last 24 hours,
- create Gmail draft replies,
- write reviewed rows to a Notion database.

They should not:

- send email automatically,
- write unreviewed drafts into Gmail,
- store private email text in public repos,
- import sensitive rows to Notion without a preview.

## Suggested Future Commands

These are roadmap examples, not implemented commands:

```bash
python3 -m workday_automation_starter daily-report --source exports
python3 -m workday_automation_starter daily-report --source gmail-calendar --preview
python3 -m workday_automation_starter email-reply-assistant --source gmail --since 24h --preview
python3 -m workday_automation_starter trend-digest --source web-search --topic AI --preview
python3 -m workday_automation_starter campaign-kit --topic "Campaign idea" --export pptx --preview
python3 -m workday_automation_starter receipt-report ~/Receipts --ocr optional --preview
python3 -m workday_automation_starter research-pack --sources ~/Papers --pdf-extract optional --preview
python3 -m workday_automation_starter publish-notion weekly-report.md --preview
```

## Privacy Boundary

The user owns the decision to connect accounts. The default project should remain useful without any external connector.
