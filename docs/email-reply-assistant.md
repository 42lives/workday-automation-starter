# Email Reply Assistant

`email-reply-assistant` creates a local package for review-worthy email replies and Notion-style archiving.

It is a safe starter version of a Gmail and Notion workflow:

1. read a sanitized email export,
2. optionally keep only messages from a recent time window,
3. filter messages that likely need a reply,
4. include important senders even when the wording is unclear,
5. draft business-tone reply text,
6. create a Notion-ready archive CSV,
7. create an approval checklist,
8. save a package manifest.

The public repository does not connect to Gmail, save real Gmail drafts, send email, or write to Notion. Those steps should stay optional and require user review.

## Example

```bash
python3 -m workday_automation_starter email-reply-assistant \
  --emails examples/emails/sample-inbox.txt \
  --output-dir outputs/email-reply \
  --important-sender operations@example.test \
  --status "Pending review" \
  --since-hours 24 \
  --now "2026-06-27 10:00"
```

Generated files:

- `reply-drafts.md`
- `notion-archive.csv`
- `approval-checklist.md`
- `email-reply-manifest.json`

## Human Approval Boundary

Before connecting Gmail or Notion:

1. review every reply draft,
2. confirm recipient, tone, deadline, and promised action,
3. create Gmail drafts only after review,
4. send email only after a human clicks the final send button,
5. import Notion rows only after checking privacy and workspace permissions.

## Time Window

Use `--since-hours 24` to model a recent Gmail review. Use `--now` in examples and tests when the result should be deterministic.
