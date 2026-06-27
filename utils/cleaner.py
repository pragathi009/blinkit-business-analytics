"""
data_cleaner.py
---------------
General-purpose CSV/Excel cleaner.
Usage: python utils/cleaner.py --input data/raw/yourfile.csv --output data/cleaned/yourfile_clean.csv
"""

import pandas as pd
import argparse
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ── 1. LOAD ──────────────────────────────────────────────────────────────────

def load_file(path: str) -> pd.DataFrame:
    """Load CSV or Excel file into a DataFrame."""
    ext = os.path.splitext(path)[-1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(path)
        log.info(f"Loaded Excel: {path} → {df.shape}")
    elif ext == ".csv":
        df = pd.read_csv(path)
        log.info(f"Loaded CSV: {path} → {df.shape}")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return df


# ── 2. INSPECT ───────────────────────────────────────────────────────────────

def inspect(df: pd.DataFrame) -> None:
    """Print a quick data quality summary."""
    print("\n── SHAPE ──────────────────────────────")
    print(f"  Rows: {df.shape[0]:,}  |  Columns: {df.shape[1]}")

    print("\n── DTYPES & NULL COUNTS ───────────────")
    summary = pd.DataFrame({
        "dtype": df.dtypes,
        "nulls": df.isnull().sum(),
        "null_%": (df.isnull().mean() * 100).round(1),
        "unique": df.nunique()
    })
    print(summary.to_string())

    print("\n── DUPLICATES ─────────────────────────")
    print(f"  Duplicate rows: {df.duplicated().sum():,}")
    print()


# ── 3. CLEAN ─────────────────────────────────────────────────────────────────

def clean(df: pd.DataFrame) -> pd.DataFrame:
    original_rows = len(df)

    # 3a. Standardize column names → snake_case
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[\s\-/]+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
    )
    log.info("Column names standardized to snake_case.")

    # 3b. Drop fully empty rows / columns
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # 3c. Remove duplicate rows
    before_dedup = len(df)
    df.drop_duplicates(inplace=True)
    log.info(f"Removed {before_dedup - len(df):,} duplicate rows.")

    # 3d. Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # 3e. Auto-detect & parse date columns
    for col in df.columns:
        if any(kw in col for kw in ("date", "time", "dt", "day", "month", "year")):
            try:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                log.info(f"  Parsed '{col}' as datetime.")
            except Exception:
                pass

    # 3f. Attempt numeric coercion on object columns that look numeric
    for col in df.select_dtypes(include="object").columns:
        converted = pd.to_numeric(df[col].str.replace(r"[$,€£%]", "", regex=True), errors="coerce")
        if converted.notna().mean() > 0.8:          # >80% convertible → apply
            df[col] = converted
            log.info(f"  Coerced '{col}' to numeric.")

    log.info(f"Cleaning complete. Rows: {original_rows:,} → {len(df):,}")
    return df


# ── 4. SAVE ──────────────────────────────────────────────────────────────────

def save(df: pd.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    log.info(f"Saved cleaned file → {path}")


# ── 5. MAIN ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Clean a CSV or Excel file.")
    parser.add_argument("--input",  required=True, help="Path to raw file")
    parser.add_argument("--output", required=True, help="Path for cleaned CSV")
    parser.add_argument("--inspect-only", action="store_true",
                        help="Print quality report without saving")
    args = parser.parse_args()

    df = load_file(args.input)
    inspect(df)

    if not args.inspect_only:
        df_clean = clean(df)
        save(df_clean, args.output)
        print("\n── POST-CLEAN SUMMARY ─────────────────")
        inspect(df_clean)


if __name__ == "__main__":
    main()
