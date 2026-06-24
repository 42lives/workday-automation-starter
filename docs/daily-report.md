# Daily and Weekly Report Drafts

`daily-report` creates a report draft from sanitized email and calendar sample files.

It is designed as a privacy-safe version of a common office automation workflow:

1. collect relevant emails,
2. collect calendar events,
3. summarize key issues,
4. list meetings and follow-ups,
5. save a reviewable report draft.

The public repository does not connect to real Gmail or Google Calendar. Use sample exports first, then add real integrations only after privacy boundaries are clear. Optional connector expectations are documented in [`integrations.md`](integrations.md).

## Example

```bash
python3 -m workday_automation_starter daily-report \
  --emails examples/emails/sample-inbox.txt \
  --calendar examples/calendar/sample-week.csv \
  --period weekly
```

JSON output is available for later dashboards or document generation:

```bash
python3 -m workday_automation_starter daily-report \
  --emails examples/emails/sample-inbox.txt \
  --calendar examples/calendar/sample-week.csv \
  --period weekly \
  --format json
```

## Next Steps

- Add Word export after the Markdown draft is stable.
- Add filtering by sender or project.
- Add a privacy preflight before processing real exports.
- Add optional Notion or Google Docs export boundaries.
- Add optional Gmail and Google Calendar connectors only after preview, token, and storage rules are clear.
