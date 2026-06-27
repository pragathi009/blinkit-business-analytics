"""
dashboard.py
------------
Interactive analytics dashboard powered by Plotly Dash + DuckDB.
Reads directly from your DuckDB database.

Usage:
    pip install dash plotly duckdb pandas
    python dashboard/dashboard.py
    → Open http://127.0.0.1:8050 in your browser
"""

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import os

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "analytics.duckdb"))

app = Dash(__name__)
app.title = "Analytics Dashboard"

# ── COLORS ───────────────────────────────────────────────────────────────────
COLORS = {
    "bg": "#0f1117",
    "card": "#1a1d27",
    "accent": "#6366f1",
    "text": "#e2e8f0",
    "muted": "#64748b",
    "green": "#22c55e",
    "red": "#ef4444",
}

CARD = {
    "background": COLORS["card"],
    "borderRadius": "12px",
    "padding": "20px",
    "marginBottom": "16px",
}


# ── HELPERS ───────────────────────────────────────────────────────────────────

def db_exists() -> bool:
    return os.path.exists(DB_PATH)


def query(sql: str) -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(sql).df()
    con.close()
    return df


def get_tables() -> list[str]:
    if not db_exists():
        return []
    con = duckdb.connect(DB_PATH, read_only=True)
    tables = con.execute("SHOW TABLES").df()["name"].tolist()
    con.close()
    return tables


def get_columns(table: str) -> list[str]:
    con = duckdb.connect(DB_PATH, read_only=True)
    cols = con.execute(f"DESCRIBE {table}").df()["column_name"].tolist()
    con.close()
    return cols


# ── LAYOUT ───────────────────────────────────────────────────────────────────

def layout():
    if not db_exists():
        return html.Div(
            style={"background": COLORS["bg"], "minHeight": "100vh",
                   "fontFamily": "Inter, sans-serif", "padding": "24px"},
            children=[
                html.Div([
                    html.H1("📊 Analytics Dashboard",
                            style={"color": COLORS["text"], "margin": 0, "fontSize": "28px"}),
                    html.P("No DuckDB database was found.",
                           style={"color": COLORS["muted"], "marginTop": "12px", "fontSize": "16px"}),
                    html.P(
                        "Create or load the dataset first, then restart the dashboard.",
                        style={"color": COLORS["muted"], "marginTop": "4px", "fontSize": "14px"},
                    ),
                    html.Pre(f"Expected database path: {DB_PATH}",
                             style={"color": COLORS["text"], "background": COLORS["card"],
                                    "padding": "12px", "borderRadius": "10px", "overflowX": "auto"}),
                    html.P("Run: python sql/sql_engine.py --load data/cleaned/yourfile.csv --table mytable",
                           style={"color": COLORS["accent"], "marginTop": "16px", "fontSize": "14px"}),
                ], style={**CARD, "maxWidth": "800px", "margin": "0 auto"}),
            ]
        )

    tables = get_tables()
    table_options = [{"label": t, "value": t} for t in tables]

    return html.Div(
        style={"background": COLORS["bg"], "minHeight": "100vh",
               "fontFamily": "Inter, sans-serif", "padding": "24px"},
        children=[
            # Header
            html.Div([
                html.H1("📊 Analytics Dashboard",
                        style={"color": COLORS["text"], "margin": 0, "fontSize": "28px"}),
                html.P("Select a table and columns to explore your data.",
                       style={"color": COLORS["muted"], "marginTop": "4px"}),
            ], style={"marginBottom": "28px"}),

            # Controls row
            html.Div([
                html.Div([
                    html.Label("Table", style={"color": COLORS["muted"], "fontSize": "12px",
                                               "textTransform": "uppercase", "letterSpacing": "1px"}),
                    dcc.Dropdown(id="table-select", options=table_options,
                                 value=tables[0] if tables else None,
                                 style={"marginTop": "6px"}),
                ], style={"flex": 1, "marginRight": "16px"}),

                html.Div([
                    html.Label("X Axis / Category", style={"color": COLORS["muted"], "fontSize": "12px",
                                                            "textTransform": "uppercase"}),
                    dcc.Dropdown(id="x-col", style={"marginTop": "6px"}),
                ], style={"flex": 1, "marginRight": "16px"}),

                html.Div([
                    html.Label("Y Axis / Metric", style={"color": COLORS["muted"], "fontSize": "12px",
                                                         "textTransform": "uppercase"}),
                    dcc.Dropdown(id="y-col", style={"marginTop": "6px"}),
                ], style={"flex": 1}),
            ], style={"display": "flex", "marginBottom": "24px"}),

            # KPI cards
            html.Div(id="kpi-cards", style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

            # Charts row
            html.Div([
                html.Div([dcc.Graph(id="bar-chart")],
                         style={**CARD, "flex": 1, "marginRight": "16px"}),
                html.Div([dcc.Graph(id="pie-chart")],
                         style={**CARD, "flex": 1}),
            ], style={"display": "flex"}),

            # Line chart (full width)
            html.Div([dcc.Graph(id="line-chart")], style=CARD),

            # Data table preview
            html.Div([
                html.H3("Data Preview", style={"color": COLORS["text"], "marginTop": 0}),
                html.Div(id="data-preview"),
            ], style=CARD),
        ]
    )


app.layout = layout


# ── CALLBACKS ─────────────────────────────────────────────────────────────────

@callback(
    Output("x-col", "options"),
    Output("x-col", "value"),
    Output("y-col", "options"),
    Output("y-col", "value"),
    Input("table-select", "value"),
)
def update_column_dropdowns(table):
    if not table:
        return [], None, [], None
    cols = get_columns(table)
    options = [{"label": c, "value": c} for c in cols]
    return options, cols[0], options, cols[1] if len(cols) > 1 else cols[0]


@callback(
    Output("kpi-cards", "children"),
    Output("bar-chart", "figure"),
    Output("pie-chart", "figure"),
    Output("line-chart", "figure"),
    Output("data-preview", "children"),
    Input("table-select", "value"),
    Input("x-col", "value"),
    Input("y-col", "value"),
)
def update_charts(table, x_col, y_col):
    if not table or not x_col or not y_col:
        empty = go.Figure()
        return [], empty, empty, empty, ""

    df = query(f"SELECT * FROM {table} LIMIT 5000")
    total_rows = query(f"SELECT COUNT(*) AS n FROM {table}").iloc[0, 0]
    unique_x = df[x_col].nunique()

    # ── KPI cards ──
    kpis = [
        ("Total Rows", f"{total_rows:,}", COLORS["accent"]),
        (f"Unique {x_col}", f"{unique_x:,}", COLORS["green"]),
    ]
    if pd.api.types.is_numeric_dtype(df[y_col]):
        kpis.append((f"Avg {y_col}", f"{df[y_col].mean():,.2f}", "#f59e0b"))
        kpis.append((f"Total {y_col}", f"{df[y_col].sum():,.2f}", "#ec4899"))

    kpi_cards = [
        html.Div([
            html.P(label, style={"color": COLORS["muted"], "fontSize": "12px",
                                 "margin": 0, "textTransform": "uppercase"}),
            html.H2(value, style={"color": color, "margin": "4px 0 0", "fontSize": "28px"}),
        ], style={**CARD, "flex": 1, "marginBottom": 0})
        for label, value, color in kpis
    ]

    plot_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text"]),
        margin=dict(t=40, b=40, l=40, r=20),
    )

    # ── Bar chart ──
    if pd.api.types.is_numeric_dtype(df[y_col]):
        agg = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False).head(20)
    else:
        agg = df.groupby(x_col)[y_col].count().reset_index()
        agg.columns = [x_col, y_col]
        agg = agg.sort_values(y_col, ascending=False).head(20)

    bar = px.bar(agg, x=x_col, y=y_col, title=f"{y_col} by {x_col} (Top 20)",
                 color=y_col, color_continuous_scale="Viridis")
    bar.update_layout(**plot_layout)

    # ── Pie chart ──
    pie = px.pie(agg.head(10), names=x_col, values=y_col,
                 title=f"Distribution of {y_col} by {x_col}",
                 color_discrete_sequence=px.colors.sequential.Plasma_r)
    pie.update_layout(**plot_layout)

    # ── Line chart (date if available, else index) ──
    date_cols = [c for c in df.columns
                 if pd.api.types.is_datetime64_any_dtype(df[c])
                 or any(k in c for k in ("date", "time", "dt", "month", "year"))]

    if date_cols:
        date_col = date_cols[0]
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            ts = df.dropna(subset=[date_col]).set_index(date_col).sort_index()
            if pd.api.types.is_numeric_dtype(ts[y_col]):
                ts_monthly = ts[y_col].resample("ME").sum().reset_index()
                line = px.line(ts_monthly, x=date_col, y=y_col,
                               title=f"{y_col} Over Time (monthly)")
                line.update_traces(line_color=COLORS["accent"])
                line.update_layout(**plot_layout)
            else:
                line = go.Figure(layout=plot_layout)
        except Exception:
            line = go.Figure(layout=plot_layout)
    else:
        line = go.Figure(layout=plot_layout)
        line.update_layout(title="No date column detected for time-series chart.")

    # ── Data preview ──
    preview_df = df.head(10)
    preview = html.Table(
        [html.Thead(html.Tr([html.Th(c, style={"color": COLORS["accent"],
                                               "padding": "8px", "textAlign": "left",
                                               "borderBottom": f"1px solid {COLORS['muted']}"})
                             for c in preview_df.columns]))] +
        [html.Tbody([
            html.Tr([
                html.Td(str(preview_df.iloc[i][c]),
                        style={"color": COLORS["text"], "padding": "6px 8px",
                               "borderBottom": f"1px solid {COLORS['card']}"})
                for c in preview_df.columns
            ]) for i in range(len(preview_df))
        ])],
        style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px"}
    )

    return kpi_cards, bar, pie, line, preview


# ── RUN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"\n⚠️  No database found at '{DB_PATH}'.")
        print("   First load your cleaned CSVs:")
        print("   python sql/sql_engine.py --load data/cleaned/yourfile.csv --table mytable\n")
    app.run(debug=True, host="0.0.0.0", port=8050)
