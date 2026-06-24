# Campaign Kit

`campaign-kit` creates a local campaign package from one topic.

It is a safe starter version of a one-stop marketing workflow:

1. enter a campaign topic,
2. create a proposal draft,
3. create a presentation outline,
4. create card-news copy and image prompts,
5. save a package manifest.

The public repository does not perform live news search, Word export, PPT export, or image generation by default. Those steps should stay optional and reviewable.

## Example

```bash
python3 -m workday_automation_starter campaign-kit \
  --topic "2026 eco trend product planning" \
  --output-dir outputs/eco-campaign \
  --cards 4
```

Generated files:

- `proposal.md`
- `slides-outline.md`
- `card-news.md`
- `campaign-manifest.json`

## Integration Boundary

Future connectors may export to Word, PPT, or image generation tools. The default workflow should keep every generated asset in local text files first so a person can review claims, copyright risks, and brand suitability.
