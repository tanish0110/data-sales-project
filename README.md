# Data Sales Project

This project builds a simple end-to-end sales analytics pipeline using Python, DuckDB, and dbt. It ingests sales data from an Excel workbook, loads the raw tables into a local DuckDB database, transforms the data in dbt, and exports reporting-ready tables for Power BI.

## Overview

The goal of this project is to turn raw sales data into clean, trusted output that supports business questions such as:

- Which sales channel generates the most revenue?
- Are weekly transaction totals consistent with the company-reported summary?
- How do revenue, marketing spend, and conversion trends behave over time?

---

## Pipeline Flow

1. The source Excel file is placed in the `data/` folder.
2. `ingest.py` reads the workbook and loads the raw data into DuckDB.
3. dbt models transform the raw data into cleaned staging tables.
4. dbt marts create business-ready analytics tables.
5. `export_marts.py` exports the final tables as CSV files for Power BI.

```text
Excel source data
    -> ingest.py
    -> sales_pipeline.duckdb
    -> dbt staging models
    -> dbt marts
    -> powerbi_exports/*.csv
```

---

## Repository Structure

```text
.
├── data/
│   └── Sales_Data.xlsx                    # Source Excel workbook
├── sales_pipeline/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_transactions.sql
│   │   │   └── stg_weekly_summary.sql
│   │   └── marts/
│   │       ├── mart_channel_performance.sql
│   │       ├── mart_weekly_reconciliation.sql
│   │       └── mart_weekly_trend.sql
│   ├── dbt_project.yml
│   ├── README.md
│   └── target/
├── ingest.py                              # Raw ingestion into DuckDB
├── export_marts.py                        # Export marts to CSV
├── requirements.txt                       # Python dependencies
├── sales_pipeline.duckdb                  # Local warehouse database
├── powerbi_exports/
│   ├── mart_channel_performance.csv
│   ├── mart_weekly_reconciliation.csv
│   └── mart_weekly_trend.csv
├── dbt_test.yml                           # GitHub Actions CI pipeline
├── README.md                              # Project documentation
├── CHANGELOG.md                           # Project notes and change history
├── .gitignore                             # Local environment exclusions
└── .github/                               # Optional GitHub configuration
```

---

## Main Components

### 1. Ingestion Layer

The script [ingest.py](ingest.py) reads the source workbook and creates raw tables in DuckDB.

It loads the following source sheets:

- `Transaction Data`
- `Weekly Summary (Layer 2)`

The raw layer stores data in the `raw` schema:

- `raw.raw_transactions`
- `raw.raw_weekly_summary`

This layer preserves the original source records and standardizes the structure for downstream processing.

### 2. dbt Transformation Layer

The dbt project in [sales_pipeline](sales_pipeline) cleans and models the raw tables.

#### Staging models

- [sales_pipeline/models/staging/stg_transactions.sql](sales_pipeline/models/staging/stg_transactions.sql)
  - Cleans transaction data
  - Keeps one row per order
  - Creates `week_start_date` for easier weekly analysis

- [sales_pipeline/models/staging/stg_weekly_summary.sql](sales_pipeline/models/staging/stg_weekly_summary.sql)
  - Cleans weekly metrics
  - Extracts week numbers for comparison with transaction data

#### Mart models

- [sales_pipeline/models/marts/mart_channel_performance.sql](sales_pipeline/models/marts/mart_channel_performance.sql)
  - Measures channel performance by revenue and order count

- [sales_pipeline/models/marts/mart_weekly_reconciliation.sql](sales_pipeline/models/marts/mart_weekly_reconciliation.sql)
  - Compares calculated totals with reported summary totals
  - Adds a `MATCH` or `MISMATCH` status for data validation

- [sales_pipeline/models/marts/mart_weekly_trend.sql](sales_pipeline/models/marts/mart_weekly_trend.sql)
  - Connects revenue trends with marketing spend and conversion metrics

### 3. Export Layer

The script [export_marts.py](export_marts.py) exports the dbt mart tables as CSV files into [powerbi_exports](powerbi_exports). These files are ready for import into Power BI.

---

## Quick Start

### Prerequisites

- Python 3.10+
- A local virtual environment (recommended)
- The source Excel file available in `data/Sales_Data.xlsx`

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run ingestion

```powershell
python ingest.py
```

This creates the DuckDB database at:

```text
sales_pipeline.duckdb
```

### 4. Run dbt

```powershell
cd sales_pipeline
dbt debug
dbt run
dbt test
```

### 5. Export marts for Power BI

```powershell
cd ..
python export_marts.py
```

The generated CSV files appear in [powerbi_exports](powerbi_exports).

---

## Recommended Workflow

```powershell
python ingest.py
cd sales_pipeline
dbt debug
dbt run
dbt test
cd ..
python export_marts.py
```

This is the standard flow for building and exporting the project outputs.

---

## Troubleshooting

### `ERROR: data/Sales_Data.xlsx not found`

Make sure the source workbook is present in the `data/` folder and named exactly:

```text
data/Sales_Data.xlsx
```

### `dbt debug` fails to connect

Check that:

- the DuckDB database exists
- you are running the command from the correct folder
- the dbt profile is configured for the project

### Power BI import issues

Verify that the CSV files were exported successfully into [powerbi_exports](powerbi_exports) and that the files are not empty.

### Local environment clutter

Use the project `.gitignore` to avoid committing virtual environments and temporary Python files.

---

## Output Tables

The final reporting tables are:

- `main.mart_channel_performance`
- `main.mart_weekly_reconciliation`
- `main.mart_weekly_trend`

These are the values used for analysis and dashboard reporting.

---

## Notes

- The raw layer keeps the original dataset and normalizes only the structure.
- The staging layer is intentionally lightweight and focused on cleaning.
- The reconciliation mart checks whether calculated values match the reported summary.
- The export script writes the final marts to CSV so they can be used directly in Power BI.

---

## Changelog

For recent project updates and notes, see [CHANGELOG.md](CHANGELOG.md).
