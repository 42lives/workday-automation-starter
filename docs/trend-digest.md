# Trend Digest

`trend-digest` creates a local trend report from sanitized news or newsletter items.

It is a privacy-safe version of a common knowledge-capture workflow:

1. collect trend or newsletter items,
2. filter by topic,
3. create 3-line summaries,
4. assign a simple importance score,
5. export Markdown, JSON, or Notion-ready CSV.

The public repository does not perform live web search and does not write to Notion. Those should remain optional connector steps.

## Example

```bash
python3 -m workday_automation_starter trend-digest \
  --items examples/trends/sample-news.csv \
  --topic AI \
  --limit 10
```

Create Notion-ready CSV:

```bash
python3 -m workday_automation_starter trend-digest \
  --items examples/trends/sample-news.csv \
  --topic AI \
  --format csv
```

## Integration Boundary

Future connectors may search the web or publish to Notion, but the default workflow should remain useful with local sample files and sanitized exports.
