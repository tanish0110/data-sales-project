"""
export_marts.py
Exports the dbt mart tables from sales_pipeline.duckdb into CSV files
that Power BI can load directly. Run this from the project root
(the folder containing sales_pipeline.duckdb), not from inside the
sales_pipeline dbt folder.

Usage:
    python export_marts.py
"""

from pathlib import Path
import duckdb

DB_FILE = Path("sales_pipeline.duckdb")
OUTPUT_DIR = Path("powerbi_exports")

MARTS = [
    "mart_weekly_reconciliation",
    "mart_channel_performance",
    "mart_weekly_trend",
]


def main():
    if not DB_FILE.exists():
        raise SystemExit(f"ERROR: {DB_FILE} not found. Run this from your project root folder.")

    OUTPUT_DIR.mkdir(exist_ok=True)
    con = duckdb.connect(str(DB_FILE))

    for mart in MARTS:
        out_path = OUTPUT_DIR / f"{mart}.csv"
        con.execute(f"COPY main.{mart} TO '{out_path}' (HEADER, DELIMITER ',')")
        row_count = con.execute(f"SELECT COUNT(*) FROM main.{mart}").fetchone()[0]
        print(f"Exported {mart}: {row_count} rows -> {out_path}")

    con.close()
    print("\nDone. Load the CSVs in powerbi_exports/ into Power BI (Get Data > Text/CSV).")


if __name__ == "__main__":
    main()