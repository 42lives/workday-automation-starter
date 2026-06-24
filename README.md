# Workday Automation Starter

Local-first office automation examples for working professionals who want to use AI-style workflows without exposing private work data.

This project turns common daily tasks into small, reviewable command-line workflows:

- Plan how to organize a messy downloads folder.
- Turn a long note into a presentation outline.
- Summarize sample email text into a Notion-ready Markdown or CSV task list.

The tools are intentionally simple and dependency-free. They are safe starter workflows that can later be connected to Codex, ChatGPT, Notion, Gmail, or document tools after the privacy boundary is clear.

## Why This Exists

Many people start using AI because they want to automate repeated office work: document drafting, presentation preparation, file organization, email follow-up, and knowledge capture. The hard part is not only generating text. The hard part is turning that intent into repeatable, inspectable workflows.

Workday Automation Starter provides small examples that run locally first, use sample data, and produce files a person can review before using them in real work.

## Installation

No external dependencies are required.

```bash
python3 -m workday_automation_starter --help
```

## Usage

Create a file organization plan:

```bash
python3 -m workday_automation_starter file-plan examples --format markdown
```

Create a presentation outline from a note:

```bash
python3 -m workday_automation_starter doc-outline examples/docs/generative-ai-guide.txt --slides 5
```

Create a Notion-ready summary from sample email text:

```bash
python3 -m workday_automation_starter email-digest examples/emails/sample-inbox.txt --format markdown
python3 -m workday_automation_starter email-digest examples/emails/sample-inbox.txt --format csv
```

## Commands

### `file-plan`

Scans a folder and creates a dry-run organization plan. It does not move files.

The plan groups files into:

- documents,
- presentations,
- spreadsheets,
- images,
- code,
- archives,
- possible private files,
- other files.

### `doc-outline`

Turns a plain text note into a presentation outline with a title, slide headings, and bullet points.

This is a deterministic starter workflow, not a language model. It is meant to show the shape of a safe automation step before connecting an AI assistant.

### `email-digest`

Reads sample email text and creates a reviewable digest for Notion-style knowledge capture.

The input format is intentionally simple:

```text
From: teammate@example.test
Subject: Project update
Body: Please review the draft by Friday.
```

Use sample data only. Do not commit real email content.

## Privacy

This project does not call Gmail, Notion, OpenAI, analytics, or any remote API. All examples run locally.

## OpenAI Codex Fit

Codex can help turn these starter workflows into safer real tools: tests, file handling, document export, plugin boundaries, privacy checks, and reviewable automation steps. The project is designed for working professionals and non-professional developers who want to learn automation through practical examples.

## Roadmap

- Add Word/Markdown export templates.
- Add PPTX generation after the outline workflow is stable.
- Add a safe sample Notion import workflow.
- Add a privacy preflight check before processing real folders.
- Add a guided automation checklist for new workflows.

## License

MIT
