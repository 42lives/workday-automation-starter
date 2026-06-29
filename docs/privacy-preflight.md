# Privacy Preflight

`privacy-preflight` scans a folder before using real files in automation workflows.

It checks for:

- private-looking file names and extensions,
- credential-like file names,
- secret-like tokens in text files,
- email-like personal data,
- private or credential-like wording.

## Example

```bash
python3 -m workday_automation_starter privacy-preflight ~/Downloads --format markdown
python3 -m workday_automation_starter privacy-preflight ~/Downloads --format json
```

## Review Boundary

This command does not move, upload, publish, or delete files. It creates a local review report so users can inspect privacy risks before running folder cleanup, document generation, email workflows, or connector-based automations.

Do not treat a clean report as a legal or security guarantee. Review sensitive folders manually before connecting Gmail, Notion, Google Sheets, web search, document export, or AI tools.
