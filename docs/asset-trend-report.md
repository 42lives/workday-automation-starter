# Asset Trend Report

`asset-trend-report` creates a local personal finance trend package from sanitized market, real-estate, or newsletter notes.

It is a safe starter version of an asset management workflow:

1. collect sanitized stock, macro, real-estate, FX, or newsletter items,
2. filter by a personal watchlist,
3. rank items by simple importance signals,
4. create a market digest,
5. create a Google-Sheets-ready portfolio journal CSV,
6. create a weekly report draft,
7. create a connector checklist,
8. save a package manifest.

The public repository does not perform live web search, read real Gmail newsletters, write to Google Sheets, export Word files, or give investment advice.

## Example

```bash
python3 -m workday_automation_starter asset-trend-report \
  --items examples/assets/sample-asset-trends.csv \
  --output-dir outputs/asset-trends \
  --watchlist AAPL \
  --watchlist SPY \
  --limit 5
```

Generated files:

- `market-digest.md`
- `portfolio-journal.csv`
- `weekly-report.md`
- `connector-checklist.md`
- `asset-trend-manifest.json`

## Connector Boundary

Future connectors may search the web, read Gmail newsletters, write reviewed rows to Google Sheets, or export a Word report. They should remain optional and require preview.

Do not connect brokerage accounts, store account numbers, publish balances, or treat generated summaries as buy/sell recommendations.
