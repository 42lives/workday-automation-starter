# Receipt Report

`receipt-report` creates a local expense report draft from receipt files.

It is a safe starter version of a receipt automation workflow:

1. place receipt files in a staging folder,
2. infer date, category, vendor, and amount from safe sample filenames,
3. create a month/category organization plan,
4. generate an expense report draft,
5. export Markdown, JSON, or CSV.

The public repository does not perform OCR and does not create Word files by default. Those steps should stay optional because receipts can contain private financial data.

## Filename Pattern

Use sample filenames like:

```text
2026-06-12_meal_cafe_12800_lunch.jpg
2026-06-13_taxi_station_9500_meeting.png
2026-06-14_office_store_34000_supplies.txt
```

## Example

```bash
python3 -m workday_automation_starter receipt-report examples/receipts
```

CSV output:

```bash
python3 -m workday_automation_starter receipt-report examples/receipts --format csv
```

## Integration Boundary

Future connectors may add OCR, Word export, or accounting-system import. The default workflow should keep data local, generate a reviewable draft first, and avoid committing real receipts.
