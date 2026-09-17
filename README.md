# Data Sales Project

This project builds a small end-to-end sales analytics pipeline using Python, DuckDB, and dbt. It ingests sales data from an Excel workbook, loads it into a local DuckDB warehouse, transforms the data in dbt, and exports curated mart tables for reporting in Power BI.

## Project Goal

The main purpose is to turn raw sales data into clean, analysis-ready tables that can answer questions like:

- Which sales channel performs best?
- How do actual weekly transaction totals compare with reported weekly summary numbers?
- How does revenue trend against marketing spend and conversion rate?

---

## Pipeline Overview

The flow is:

1. Raw Excel file is read from the data folder.
2. Python ingestion script loads the data into DuckDB as raw tables.
3. dbt models clean and structure the data in staging tables.
4. dbt marts calculate business views for reporting.
5. CSV files are exported for Power BI consumption.

### Data flow

raw data in Excel
    -> ingest.py
    -> sales_pipeline.duckdb
    -> dbt staging models
    -> dbt mart models
    -> powerbi_exports/*.csv

---

## Repository Structure

```text
.
├── data/
│   └── Sales_Data.xlsx                 # Source sales Excel file
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
│   └── target/                         # dbt compiled output
├── ingest.py                           # Load raw Excel sheets into DuckDB
├── export_marts.py                     # Export mart tables as CSV files
├── requirements.txt                    # Python dependencies
├── sales_pipeline.duckdb               # Local database used by the pipeline
├── powerbi_exports/
│   ├── mart_channel_performance.csv
│   ├── mart_weekly_reconciliation.csv
│   └── mart_weekly_trend.csv
├── dbt_test.yml                        # GitHub Actions workflow for CI checks
└── README.md                           # This file
```

---

## Main Components

### 1) Ingestion layer

The script [ingest.py](ingest.py) reads the Excel workbook and creates raw tables in DuckDB.

It loads two main sheets:

- Transaction Data
- Weekly Summary (Layer 2)

The raw tables are created under the DuckDB schema named raw:

- raw.raw_transactions
- raw.raw_weekly_summary

This layer keeps the original source data as-is, only standardizing column names and adding a few derived fields for downstream use.

### 2) dbt transformation layer

The project in [sales_pipeline](sales_pipeline) contains dbt models that transform the raw tables into clean staging and mart tables.

#### Staging models

- [sales_pipeline/models/staging/stg_transactions.sql](sales_pipeline/models/staging/stg_transactions.sql)
  - Cleans transaction-level sales data.
  - Keeps one row per order.
  - Creates a week_start_date field for joins.

- [sales_pipeline/models/staging/stg_weekly_summary.sql](sales_pipeline/models/staging/stg_weekly_summary.sql)
  - Cleans weekly summary metrics.
  - Extracts week numbers and prepares marketing and conversion metrics.

#### Mart models

- [sales_pipeline/models/marts/mart_channel_performance.sql](sales_pipeline/models/marts/mart_channel_performance.sql)
  - Shows sales metrics by channel.
  - Includes revenue, average order value, and revenue share.

- [sales_pipeline/models/marts/mart_weekly_reconciliation.sql](sales_pipeline/models/marts/mart_weekly_reconciliation.sql)
  - Compares calculated weekly totals with reported weekly numbers.
  - Adds a reconciliation status: MATCH or MISMATCH.

- [sales_pipeline/models/marts/mart_weekly_trend.sql](sales_pipeline/models/marts/mart_weekly_trend.sql)
  - Combines transaction revenue with weekly marketing and conversion data.
  - Useful for trend and performance analysis.

### 3) Export layer

The script [export_marts.py](export_marts.py) exports the mart tables from DuckDB into CSV files inside [powerbi_exports](powerbi_exports).

These CSVs can be directly imported into Power BI.

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Access to the Excel file in the data folder
- A local environment such as venv or conda

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

### 3. Prepare the source file

Place the sales workbook in:

```text
data/Sales_Data.xlsx
```

Make sure the workbook contains the expected sheets:

- Transaction Data
- Weekly Summary (Layer 2)

### 4. Run the ingestion step

```powershell
python ingest.py
```

This creates the DuckDB database at:

```text
sales_pipeline.duckdb
```

---

## Run the dbt Project

From the project root:

```powershell
cd sales_pipeline
```

Then run:

```powershell
dbt debug
dbt run
dbt test
```

These commands validate the connection, build the staging and mart models, and run data quality tests.

---

## Export for Power BI

After dbt has built the mart tables, run:

```powershell
python export_marts.py
```

This generates CSV files in [powerbi_exports](powerbi_exports) for import into Power BI.

The exported marts are:

- mart_channel_performance.csv
- mart_weekly_reconciliation.csv
- mart_weekly_trend.csv

---

## Output Tables

The final business-facing outputs are:

- main.mart_channel_performance
- main.mart_weekly_reconciliation
- main.mart_weekly_trend

These are the tables designed for analysis and dashboarding.

---

## Notes

- The raw layer keeps original source data and only normalizes columns.
- The staging layer is intentionally lightweight and keeps transformations simple.
- The reconciliation mart checks if calculated weekly values match the reported summary.
- The export script writes the final marts to CSV so they are easy to load into Power BI.

---

## Typical Workflow

```powershell
python ingest.py
cd sales_pipeline
dbt debug
dbt run
dbt test
cd ..
python export_marts.py
```

This is the standard sequence for loading and transforming the sales dataset.
