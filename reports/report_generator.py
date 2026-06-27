"""
report_generator.py
-------------------
Generate a polished HTML analytics report from your DuckDB database.
Opens in any browser; can be saved as PDF via browser Print → Save as PDF.

Usage:
    python reports/report_generator.py --table sales --x category --y revenue
"""

import duckdb
import pandas as pd
import plotly.express as px
import plotly.io as pio
import argparse
import os
from datetime import datetime

DB_PATH = "data/analytics.duckdb"
REPORT_DIR = "reports/output"


def query(sql: str, db_path: str = DB_PATH) -> pd.DataFrame:
    con = duckdb.connect(db_path, read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


def fig_to_html(fig) -> str:
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)


def generate_report(table: str, x_col: str, y_col: str, db_path: str = DB_PATH) -> str:
    df = query(f"SELECT * FROM {table}", db_path)
    total_rows = len(df)
    unique_x = df[x_col].nunique()

    # ── Aggregation ──
    if pd.api.types.is_numeric_dtype(df[y_col]):
        agg = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)
        metric_label = f"Sum of {y_col}"
        total_metric = df[y_col].sum()
        avg_metric = df[y_col].mean()
    else:
        agg = df[x_col].value_counts().reset_index()
        agg.columns = [x_col, y_col]
        metric_label = f"Count by {x_col}"
        total_metric = total_rows
        avg_metric = total_rows / unique_x

    # ── Charts ──
    bar = px.bar(agg.head(15), x=x_col, y=y_col,
                 title=f"Top 15: {metric_label}",
                 color=y_col, color_continuous_scale="Blues")
    bar.update_layout(showlegend=False)

    pie = px.pie(agg.head(8), names=x_col, values=y_col,
                 title=f"Share of {y_col} (Top 8)",
                 color_discrete_sequence=px.colors.qualitative.Set2)

    # ── KPIs ──
    kpis = {
        "Total Rows": f"{total_rows:,}",
        f"Unique {x_col}": f"{unique_x:,}",
        f"Total {y_col}": f"{total_metric:,.2f}" if isinstance(total_metric, float) else f"{total_metric:,}",
        f"Avg {y_col}": f"{avg_metric:,.2f}",
    }

    kpi_html = "".join(f"""
        <div class="kpi-card">
            <div class="kpi-label">{k}</div>
            <div class="kpi-value">{v}</div>
        </div>""" for k, v in kpis.items())

    # ── Data sample ──
    sample_html = df.head(10).to_html(index=False, classes="data-table", border=0)

    # ── HTML template ──
    report_date = datetime.now().strftime("%B %d, %Y at %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Analytics Report — {table}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; color: #1e293b; }}
  .header {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white;
             padding: 40px 48px; }}
  .header h1 {{ font-size: 32px; font-weight: 700; }}
  .header p  {{ margin-top: 8px; opacity: .8; font-size: 14px; }}
  .content {{ max-width: 1200px; margin: 0 auto; padding: 40px 24px; }}
  .kpi-row {{ display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }}
  .kpi-card {{ background: white; border-radius: 12px; padding: 20px 24px; flex: 1;
               min-width: 180px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .kpi-label {{ font-size: 12px; color: #64748b; text-transform: uppercase;
                letter-spacing: 1px; margin-bottom: 8px; }}
  .kpi-value {{ font-size: 28px; font-weight: 700; color: #4f46e5; }}
  .charts-row {{ display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }}
  .chart-card {{ background: white; border-radius: 12px; padding: 20px;
                 box-shadow: 0 1px 3px rgba(0,0,0,.08); flex: 1; min-width: 300px; }}
  .section-title {{ font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #1e293b; }}
  .data-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .data-table th {{ background: #f1f5f9; padding: 10px 12px; text-align: left;
                    font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }}
  .data-table td {{ padding: 9px 12px; border-bottom: 1px solid #f1f5f9; color: #334155; }}
  .data-table tr:hover td {{ background: #f8fafc; }}
  .table-card {{ background: white; border-radius: 12px; padding: 24px;
                 box-shadow: 0 1px 3px rgba(0,0,0,.08); overflow-x: auto; }}
  .footer {{ text-align: center; color: #94a3b8; font-size: 12px; padding: 32px; }}
</style>
</head>
<body>
<div class="header">
  <h1>📊 Analytics Report</h1>
  <p>Table: <strong>{table}</strong> &nbsp;|&nbsp; Generated: {report_date}</p>
</div>
<div class="content">
  <h2 class="section-title">Key Metrics</h2>
  <div class="kpi-row">{kpi_html}</div>

  <h2 class="section-title">Charts</h2>
  <div class="charts-row">
    <div class="chart-card">{fig_to_html(bar)}</div>
    <div class="chart-card">{fig_to_html(pie)}</div>
  </div>

  <h2 class="section-title">Data Sample (first 10 rows)</h2>
  <div class="table-card">{sample_html}</div>
</div>
<div class="footer">Generated by Analytics Project · {report_date}</div>
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--table",  required=True, help="Table name in DuckDB")
    parser.add_argument("--x",      required=True, help="Category / X-axis column")
    parser.add_argument("--y",      required=True, help="Metric / Y-axis column")
    parser.add_argument("--db",     default=DB_PATH)
    parser.add_argument("--out",    default=None,  help="Output HTML path (optional)")
    args = parser.parse_args()

    html = generate_report(args.table, args.x, args.y, args.db)

    os.makedirs(REPORT_DIR, exist_ok=True)
    out_path = args.out or f"{REPORT_DIR}/{args.table}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
    with open(out_path, "w") as f:
        f.write(html)

    print(f"\n✅ Report saved → {out_path}")
    print("   Open in your browser, then File → Print → Save as PDF to export.\n")


if __name__ == "__main__":
    main()
