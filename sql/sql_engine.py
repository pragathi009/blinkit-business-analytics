"""
sql_engine.py
-------------
Load cleaned CSVs into DuckDB and run SQL analytics.
DuckDB is file-based, needs no server, and speaks full SQL + window functions.

Usage:
    python sql/sql_engine.py --load data/cleaned/sales_clean.csv --table sales
    python sql/sql_engine.py --query "SELECT * FROM sales LIMIT 10"
    python sql/sql_engine.py --file  sql/queries/monthly_revenue.sql
"""

import duckdb
import pandas as pd
import argparse
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DB_PATH = "data/analytics.duckdb"   # change path if needed


# ── CONNECT ──────────────────────────────────────────────────────────────────

def connect(db_path: str = DB_PATH) -> duckdb.DuckDBPyConnection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)
    log.info(f"Connected to DuckDB at {db_path}")
    return con


# ── LOAD CSV → TABLE ─────────────────────────────────────────────────────────

def load_csv(con, csv_path: str, table_name: str, replace: bool = True) -> None:
    """Load a cleaned CSV into a DuckDB table."""
    if replace:
        con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"""
        CREATE TABLE {table_name} AS
        SELECT * FROM read_csv_auto('{csv_path}', header=True)
    """)
    count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    log.info(f"Loaded '{csv_path}' → table '{table_name}' ({count:,} rows)")


# ── RUN QUERY ────────────────────────────────────────────────────────────────

def run_query(con, sql: str, print_results: bool = True) -> pd.DataFrame:
    """Execute SQL and return a pandas DataFrame."""
    df = con.execute(sql).df()
    if print_results:
        print(f"\n── RESULT ({len(df):,} rows) ──────────────────────────")
        print(df.to_string(index=False))
        print()
    return df


def run_file(con, sql_file: str) -> pd.DataFrame:
    """Execute a .sql file."""
    with open(sql_file) as f:
        sql = f.read()
    log.info(f"Running: {sql_file}")
    return run_query(con, sql)


# ── LIST TABLES ──────────────────────────────────────────────────────────────

def list_tables(con) -> None:
    tables = con.execute("SHOW TABLES").df()
    print("\n── TABLES IN DATABASE ─────────────────")
    print(tables.to_string(index=False))
    print()


# ── SCHEMA ───────────────────────────────────────────────────────────────────

def describe_table(con, table_name: str) -> None:
    df = con.execute(f"DESCRIBE {table_name}").df()
    print(f"\n── SCHEMA: {table_name} ───────────────────")
    print(df.to_string(index=False))
    print()


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DuckDB SQL engine for analytics.")
    parser.add_argument("--db",     default=DB_PATH,  help="DuckDB file path")
    parser.add_argument("--load",   help="CSV path to load")
    parser.add_argument("--table",  help="Table name for --load")
    parser.add_argument("--query",  help="Inline SQL to run")
    parser.add_argument("--file",   help=".sql file to run")
    parser.add_argument("--list",   action="store_true", help="List all tables")
    parser.add_argument("--describe", help="Describe a table schema")
    args = parser.parse_args()

    con = connect(args.db)

    if args.load and args.table:
        load_csv(con, args.load, args.table)
    if args.list:
        list_tables(con)
    if args.describe:
        describe_table(con, args.describe)
    if args.query:
        run_query(con, args.query)
    if args.file:
        run_file(con, args.file)

    con.close()


if __name__ == "__main__":
    main()
