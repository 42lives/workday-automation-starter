# Research Pack

`research-pack` creates a local research summary and presentation package from a source folder.

It is a safe starter version of a paper/PDF workflow:

1. put source notes, extracted PDF text, or PDF placeholders in a folder,
2. summarize extracted text notes,
3. register PDF files as placeholders until text extraction is added,
4. create a literature summary draft,
5. create a presentation guide,
6. create image prompts for intro or visual assets,
7. save a package manifest.

The public repository does not parse copyrighted PDFs, create Word files, create PPTX files, or generate images by default. Those steps should stay optional and reviewable.

## Example

```bash
python3 -m workday_automation_starter research-pack \
  --topic "AI workflow research" \
  --sources examples/research \
  --output-dir outputs/research-pack \
  --images 3
```

Generated files:

- `literature-summary.md`
- `presentation-guide.md`
- `image-prompts.md`
- `research-manifest.json`

## Integration Boundary

Future connectors may add PDF text extraction, Word export, PPTX export, or image generation. The default workflow should keep source material local and require human review before sharing summaries or slides. Do not commit copyrighted PDFs unless they are explicitly licensed for redistribution.
