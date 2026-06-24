# Smart Clean

`smart-clean` is a safer file cleanup workflow for real work folders.

It is designed around one rule: plan first, move only after review.

## Capabilities

- Include only selected files with `--include`.
- Exclude folders or files with `--exclude`.
- Protect likely private files instead of moving them.
- Use dry-run output by default.
- Move files only when `--apply` is provided.
- Save a JSON manifest with `--manifest`.

## Examples

Plan cleanup for PDFs and images:

```bash
python3 -m workday_automation_starter smart-clean ~/Downloads --include "*.pdf" --include "*.png"
```

Exclude a private folder:

```bash
python3 -m workday_automation_starter smart-clean ~/Downloads --exclude "Private/*"
```

Apply a reviewed plan:

```bash
python3 -m workday_automation_starter smart-clean ~/Downloads --apply --manifest cleanup-manifest.json
```

## Safety Model

`smart-clean` does not call a remote service and does not inspect full document content. It uses file names, extensions, include/exclude patterns, and protected-file rules to create a reviewable plan.

Files that look private are listed under `Protected` and are not moved automatically.
