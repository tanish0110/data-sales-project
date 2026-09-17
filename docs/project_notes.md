# Project Notes

This file captures small project notes for future reference and handoff.

## Current Scope

- Ingest raw sales data from Excel into DuckDB.
- Clean and normalize the data in a dbt staging layer.
- Build business-facing marts for reporting.
- Export mart outputs to CSV for Power BI.

## Suggested Future Improvements

- Add optional data quality checks for missing channels or invalid dates.
- Add a lightweight dashboard or sample report for quick review.
- Expand the dbt tests to cover edge cases in weekly comparisons.
- Add an optional automation script for full refresh from source to export.

## Notes

This project is intentionally simple and transparent so it can be understood quickly by new users and reviewers.
