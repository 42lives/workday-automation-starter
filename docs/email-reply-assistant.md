# Email Reply Assistant

`email-reply-assistant` creates a local package for review-worthy email replies and Notion-style archiving.

It is a safe starter version of a Gmail and Notion workflow:

1. read a sanitized email export,
2. filter messages that likely need a reply,
3. include important senders even when the wording is unclear,
4. draft business-tone reply text,
5. create a Notion-ready archive CSV,
6. create an approval checklist,
7. save a package manifest.

The public repository does not connect to Gmail, save real Gmail drafts, send email, or write to Notion. Those steps should stay optional and require user review.

## Example

```bash
python3 -m workday_automation_starter email-reply-assistant \
  --emails examples/emails/sample-inbox.txt \
  --output-dir outputs/email-reply \
  --important-sender operations@example.test \
  --status "Pending review"
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
