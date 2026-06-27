# 🛒 Blinkit Business Analytics

> End-to-end data analytics project on Blinkit's grocery delivery business — from raw data cleaning to SQL analysis to interactive dashboards and reports.

## 📌 Project Overview

This project performs a full business analysis on Blinkit (formerly Grofers) — India's leading quick-commerce grocery platform. The goal is to uncover actionable insights around **sales performance, outlet trends, product categories, and customer ratings** using a structured analytics pipeline.

**Pipeline:**
```
Raw CSV Data → Data Cleaning (Python) → SQL Analysis (DuckDB) → Dashboard (Plotly Dash) → Reports (HTML/PDF)
```

---

## 📁 Project Structure

```
blinkit-business-analytics/
│
├── data/
│   ├── raw/                        # Original dataset (CSV)
│   │   └── blinkit_data.csv
│   └── cleaned/                    # Cleaned, analysis-ready CSV
│       └── blinkit_clean.csv
│
├── utils/
│   └── cleaner.py                  # Data cleaning script
│
├── sql/
│   ├── sql_engine.py               # DuckDB loader & query runner
│   └── queries/
│       ├── sales_by_outlet.sql
│       ├── category_performance.sql
│       ├── location_analysis.sql
│       ├── fat_content_analysis.sql
│       └── yearly_trends.sql
│
├── notebooks/
│   └── exploratory_analysis.ipynb  # EDA notebook (optional)
│
├── dashboard/
│   └── dashboard.py                # Interactive Plotly Dash app
│
├── reports/
│   ├── report_generator.py         # HTML report generator
│   └── output/                     # Generated reports land here
│
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

**Source:** [Blinkit Grocery Dataset — Kaggle](https://www.kaggle.com/datasets/...)

| Column | Description |
|---|---|
| `Item_Identifier` | Unique product ID |
| `Item_Weight` | Weight of the product |
| `Item_Fat_Content` | Low Fat / Regular |
| `Item_Visibility` | % display area in store |
| `Item_Type` | Product category (Fruits, Snacks, Dairy…) |
| `Item_MRP` | Maximum Retail Price |
| `Outlet_Identifier` | Unique outlet ID |
| `Outlet_Establishment_Year` | Year outlet was opened |
| `Outlet_Size` | Small / Medium / High |
| `Outlet_Location_Type` | Tier 1 / Tier 2 / Tier 3 |
| `Outlet_Type` | Grocery Store / Supermarket Type 1/2/3 |
| `Item_Outlet_Sales` | **Target variable — total sales** |

**Dataset size:** ~8,500 rows × 12 columns

---

## ⚙️ Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Data Cleaning | pandas, openpyxl |
| SQL Engine | DuckDB (serverless, file-based) |
| Dashboard | Plotly Dash |
| Reporting | Plotly + custom HTML/CSS |
| Version Control | Git + GitHub |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/blinkit-business-analytics.git
cd blinkit-business-analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add the Dataset
Download the dataset and place it at:
```
data/raw/blinkit_data.csv
```

### 4. Clean the Data
```bash
python utils/cleaner.py \
  --input data/raw/blinkit_data.csv \
  --output data/cleaned/blinkit_clean.csv
```

What this does automatically:
- Standardizes column names to `snake_case`
- Fixes inconsistent `Item_Fat_Content` values (`low fat`, `LF` → `Low Fat`)
- Removes duplicate rows
- Handles missing values in `Item_Weight` and `Outlet_Size`
- Parses and validates data types

### 5. Load into DuckDB
```bash
python sql/sql_engine.py \
  --load data/cleaned/blinkit_clean.csv \
  --table blinkit
```

### 6. Run SQL Analysis
```bash
# Check schema
python sql/sql_engine.py --describe blinkit

# Run a specific query
python sql/sql_engine.py --query "SELECT outlet_type, ROUND(SUM(item_outlet_sales),2) AS total_sales FROM blinkit GROUP BY outlet_type ORDER BY total_sales DESC"

# Run a saved query file
python sql/sql_engine.py --file sql/queries/sales_by_outlet.sql
```

### 7. Launch the Dashboard
```bash
python dashboard/dashboard.py
```
Open **http://127.0.0.1:8050** in your browser.

### 8. Generate a Report
```bash
python reports/report_generator.py \
  --table blinkit \
  --x outlet_type \
  --y item_outlet_sales
```
Report is saved in `reports/output/`. Open in Chrome → `Print → Save as PDF`.

---

## 🔍 Key SQL Analyses

### Sales by Outlet Type
```sql
SELECT
    outlet_type,
    COUNT(*)                                AS total_items,
    ROUND(SUM(item_outlet_sales), 2)        AS total_sales,
    ROUND(AVG(item_outlet_sales), 2)        AS avg_sales
FROM blinkit
GROUP BY outlet_type
ORDER BY total_sales DESC;
```

### Category Performance
```sql
SELECT
    item_type,
    ROUND(SUM(item_outlet_sales), 2)        AS total_sales,
    ROUND(AVG(item_mrp), 2)                 AS avg_mrp,
    ROUND(AVG(item_outlet_sales), 2)        AS avg_sales
FROM blinkit
GROUP BY item_type
ORDER BY total_sales DESC
LIMIT 10;
```

### Sales Trend by Outlet Age
```sql
SELECT
    outlet_establishment_year               AS year,
    COUNT(DISTINCT outlet_identifier)       AS outlets,
    ROUND(SUM(item_outlet_sales), 2)        AS total_sales
FROM blinkit
GROUP BY outlet_establishment_year
ORDER BY year;
```

### Fat Content vs Sales
```sql
SELECT
    item_fat_content,
    COUNT(*)                                AS items,
    ROUND(AVG(item_outlet_sales), 2)        AS avg_sales,
    ROUND(SUM(item_outlet_sales), 2)        AS total_sales
FROM blinkit
GROUP BY item_fat_content;
```

---

## 📈 Dashboard Features

- **KPI Cards** — Total Sales, Avg Sales per Item, Total Items, Avg Rating
- **Sales by Outlet Type** — Bar chart comparison
- **Category Breakdown** — Horizontal bar chart of top 10 item types
- **Location Performance** — Tier 1 vs 2 vs 3 sales comparison
- **Fat Content Split** — Pie chart (Low Fat vs Regular)
- **Outlet Establishment Trend** — Line chart of sales over founding year
- **Data Preview Table** — First 10 rows of filtered data

---

## 📋 Project Phases

- [x] Phase 1 — Repository setup & dataset collection
- [x] Phase 2 — Data cleaning & preprocessing
- [x] Phase 3 — SQL analysis with DuckDB
- [ ] Phase 4 — Interactive dashboard (Plotly Dash)
- [ ] Phase 5 — Report generation
- [ ] Phase 6 — Insights summary & business recommendations

---

## 💡 Insights (Preview)

> Full findings will be added after completing analysis phases.

- **Supermarket Type 1** outlets account for the largest share of total sales
- **Tier 3 cities** surprisingly outperform Tier 1 in total revenue
- **Fruits & Vegetables** and **Snack Foods** are the top-selling categories
- Outlets established around **2002–2004** show the highest cumulative sales

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](LICENSE)

---

## 👤 Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-linkedin)

---

*Built as a portfolio data analytics project. Not affiliated with Blinkit or Zomato.*
