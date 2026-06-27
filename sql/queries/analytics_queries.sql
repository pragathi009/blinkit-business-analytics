-- ============================================================
-- analytics_queries.sql
-- Common SQL patterns for data analytics.
-- Replace <table> and column names to match your data.
-- Run with: python sql/sql_engine.py --file sql/queries/analytics_queries.sql
-- ============================================================


-- ── 1. ROW COUNT & OVERVIEW ──────────────────────────────────
SELECT
    COUNT(*)                        AS total_rows,
    COUNT(DISTINCT id)              AS unique_records     -- replace 'id' with your key
FROM <table>;


-- ── 2. MISSING VALUES PER COLUMN ────────────────────────────
-- DuckDB trick: unpivot nulls across all columns
SELECT
    column_name,
    null_count,
    ROUND(100.0 * null_count / total_rows, 1) AS null_pct
FROM (
    SELECT COUNT(*) AS total_rows FROM <table>
),
LATERAL (
    SELECT unnest(column_names)   AS column_name,
           unnest(null_counts)    AS null_count
    FROM (
        SELECT
            list(col)   AS column_names,
            list(nulls) AS null_counts
        FROM (
            SELECT column_name AS col,
                   SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END) AS nulls
            FROM (UNPIVOT (SELECT * FROM <table>) ON COLUMNS(*))
            GROUP BY column_name
        )
    )
)
ORDER BY null_pct DESC;


-- ── 3. SUMMARY STATS (numeric column) ───────────────────────
SELECT
    COUNT(<amount_col>)                              AS count,
    ROUND(AVG(<amount_col>), 2)                      AS mean,
    ROUND(STDDEV(<amount_col>), 2)                   AS std_dev,
    MIN(<amount_col>)                                AS min,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY <amount_col>) AS p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY <amount_col>) AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY <amount_col>) AS p75,
    MAX(<amount_col>)                                AS max
FROM <table>;


-- ── 4. AGGREGATION BY CATEGORY ──────────────────────────────
SELECT
    <category_col>,
    COUNT(*)                        AS record_count,
    ROUND(SUM(<amount_col>), 2)     AS total_amount,
    ROUND(AVG(<amount_col>), 2)     AS avg_amount
FROM <table>
GROUP BY <category_col>
ORDER BY total_amount DESC;


-- ── 5. TIME-SERIES TREND (monthly) ──────────────────────────
SELECT
    DATE_TRUNC('month', <date_col>)::DATE   AS month,
    COUNT(*)                                AS records,
    ROUND(SUM(<amount_col>), 2)             AS total
FROM <table>
WHERE <date_col> IS NOT NULL
GROUP BY 1
ORDER BY 1;


-- ── 6. RUNNING TOTAL (WINDOW FUNCTION) ──────────────────────
SELECT
    DATE_TRUNC('month', <date_col>)::DATE   AS month,
    SUM(<amount_col>)                        AS monthly_total,
    SUM(SUM(<amount_col>)) OVER (
        ORDER BY DATE_TRUNC('month', <date_col>)
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                        AS running_total
FROM <table>
GROUP BY 1
ORDER BY 1;


-- ── 7. MONTH-OVER-MONTH GROWTH ───────────────────────────────
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', <date_col>)::DATE AS month,
        SUM(<amount_col>)                      AS total
    FROM <table>
    GROUP BY 1
)
SELECT
    month,
    total,
    LAG(total) OVER (ORDER BY month)   AS prev_month,
    ROUND(
        100.0 * (total - LAG(total) OVER (ORDER BY month))
              / NULLIF(LAG(total) OVER (ORDER BY month), 0),
        1
    )                                  AS mom_growth_pct
FROM monthly
ORDER BY month;


-- ── 8. TOP 10 RECORDS ────────────────────────────────────────
SELECT *
FROM <table>
ORDER BY <amount_col> DESC
LIMIT 10;


-- ── 9. RANK BY CATEGORY ─────────────────────────────────────
SELECT
    <category_col>,
    <amount_col>,
    RANK() OVER (ORDER BY <amount_col> DESC) AS rank
FROM <table>
QUALIFY rank <= 10;


-- ── 10. MULTI-TABLE JOIN TEMPLATE ───────────────────────────
SELECT
    a.<key_col>,
    a.<col1>,
    b.<col2>
FROM <table_a> a
LEFT JOIN <table_b> b
    ON a.<key_col> = b.<key_col>
WHERE a.<date_col> >= '2024-01-01'
ORDER BY a.<date_col>;
