"""
ingest.py
Loads Sales_Data.xlsx (Transaction Data + Weekly Summary sheets) into DuckDB
as raw tables. This is the "ingestion" layer of the pipeline: it moves data
from source to warehouse without applying business logic. Cleaning /
transformation happens later in dbt staging models.

Usage:
    1. Put Sales_Data.xlsx inside a `data/` folder next to this script.
    2. Run:  python ingest.py
    3. Output: a `sales_pipeline.duckdb` file with schema `raw` containing
       raw_transactions and raw_weekly_summary tables.
"""

from pathlib import Path
import sys

import duckdb
import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SOURCE_FILE = Path("data/Sales_Data.xlsx")
DB_FILE = Path("sales_pipeline.duckdb")

TRANSACTION_SHEET = "Transaction Data"
WEEKLY_SHEET = "Weekly Summary (Layer 2)"


def parse_time_of_day(timestamp_str: str):
    """
    The source Timestamp column looks like '07:11-010626'
    (HH:MM-DDMMYY). We only need the HH:MM portion since the date
    itself is already available cleanly in 'Date (parsed)'.
    Returns None if the value is missing or malformed, rather than
    guessing -- bad ingestion should surface nulls, not fabricate data.
    """
    if pd.isna(timestamp_str):
        return None
    try:
        time_part = str(timestamp_str).split("-")[0]
        return pd.to_datetime(time_part, format="%H:%M").time()
    except (ValueError, IndexError):
        return None


def load_transactions(xls: pd.ExcelFile) -> pd.DataFrame:
    df = pd.read_excel(xls, sheet_name=TRANSACTION_SHEET)

    # Standardize column names: lowercase, underscores -- makes downstream
    # SQL (DuckDB / dbt) much less error-prone than dealing with spaces.
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[()]", "", regex=True)
    )

    # Explicit, nullable-safe type casting. Int64 (capital I) is pandas'
    # nullable integer type -- regular int64 breaks on any NaN.
    df["order_id"] = df["order_id"].astype("Int64")
    df["device_id"] = df["device_id"].astype("Int64")
    df["order_quantity"] = df["order_quantity"].astype("Int64")
    df["nps_survey"] = df["nps_survey"].astype("Int64")  # stays null, not imputed
    df["sale"] = df["sale"].astype("float64")
    df["date_parsed"] = pd.to_datetime(df["date_parsed"], errors="coerce")

    # Derive a proper order_datetime from date + time-of-day, but KEEP the
    # original timestamp column untouched too -- raw layer should never
    # discard source data, only add derived helper columns.
    df["time_of_day"] = df["timestamp"].apply(parse_time_of_day)
    df["order_datetime"] = df.apply(
        lambda r: pd.Timestamp.combine(r["date_parsed"], r["time_of_day"])
        if pd.notna(r["date_parsed"]) and r["time_of_day"] is not None
        else pd.NaT,
        axis=1,
    )

    # Like the Weekly Summary sheet, this sheet has a trailing blank row and
    # an embedded notes row appended after the real transactions. Every real
    # transaction has an order_id, so we use that as the filter -- documented
    # here rather than silently dropped.
    before = len(df)
    df = df[df["order_id"].notna()].reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"Note: dropped {dropped} non-data footer row(s) from Transaction Data sheet (blank/notes).")

    return df


def load_weekly_summary(xls: pd.ExcelFile) -> pd.DataFrame:
    df = pd.read_excel(xls, sheet_name=WEEKLY_SHEET)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[()%]", "", regex=True)
    )
    df["week_start_date"] = pd.to_datetime(df["week_start_date"], errors="coerce")

    # The source sheet has a legend + notes row appended after the real
    # weekly data (visible if you open the Excel file directly). These
    # aren't data -- every real week row has a week_start_date, so we drop
    # rows missing one. This is a deliberate, documented decision, not
    # silent data loss.
    before = len(df)
    df = df[df["week_start_date"].notna()].reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"Note: dropped {dropped} non-data footer row(s) from Weekly Summary sheet (legend/notes).")

    return df


def log_quality_summary(name: str, df: pd.DataFrame) -> None:
    print(f"\n--- {name} ---")
    print(f"Rows: {len(df)}")
    null_counts = df.isna().sum()
    nulls = null_counts[null_counts > 0]
    if len(nulls):
        print("Columns with nulls:")
        for col, count in nulls.items():
            pct = round(count / len(df) * 100, 1)
            print(f"  {col}: {count} ({pct}%)")
    else:
        print("No nulls found.")


def main():
    if not SOURCE_FILE.exists():
        sys.exit(
            f"ERROR: {SOURCE_FILE} not found. "
            f"Create a 'data' folder next to this script and put Sales_Data.xlsx inside it."
        )

    xls = pd.ExcelFile(SOURCE_FILE)

    transactions_df = load_transactions(xls)
    weekly_df = load_weekly_summary(xls)

    log_quality_summary("raw_transactions", transactions_df)
    log_quality_summary("raw_weekly_summary", weekly_df)

    con = duckdb.connect(str(DB_FILE))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    # register() exposes the pandas df to DuckDB's SQL engine directly,
    # avoiding a slower row-by-row insert.
    con.register("transactions_view", transactions_df)
    con.register("weekly_view", weekly_df)

    con.execute("CREATE OR REPLACE TABLE raw.raw_transactions AS SELECT * FROM transactions_view;")
    con.execute("CREATE OR REPLACE TABLE raw.raw_weekly_summary AS SELECT * FROM weekly_view;")

    row_counts = con.execute(
        """
        SELECT 'raw_transactions' AS table_name, COUNT(*) AS row_count FROM raw.raw_transactions
        UNION ALL
        SELECT 'raw_weekly_summary', COUNT(*) FROM raw.raw_weekly_summary
        """
    ).fetchall()

    print(f"\nLoaded into {DB_FILE}:")
    for table_name, count in row_counts:
        print(f"  raw.{table_name}: {count} rows")

    con.close()
    print("\nIngestion complete.")


if __name__ == "__main__":
    main()
