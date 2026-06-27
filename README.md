# 🛒 Blinkit Business Analytics

End-to-end data analytics project on Blinkit's grocery delivery business — from raw data cleaning to SQL analysis to interactive dashboards.

##  Project Overview

This project performs a full business analysis on **Blinkit** — India's leading quick-commerce grocery platform. The goal is to uncover actionable insights around sales performance, outlet trends, product categories, and customer ratings using a structured analytics pipeline.

**Pipeline:**
```
Raw CSV Data → Data Cleaning (Python) → SQL Analysis (DuckDB) → Dashboard (Plotly Dash)
```

## Dataset

**Source:** Blinkit Grocery Dataset

**Dataset size:** 8,523 rows × 12 columns

## ⚙️ Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.13 |
| Data Cleaning | pandas, openpyxl |
| SQL Engine | DuckDB (serverless, file-based) |
| Dashboard | Plotly Dash |
| Version Control | Git + GitHub |


## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/blinkit-business-analytics.git
cd blinkit-business-analytics
```

### 2. Install Dependencies
```bash
pip install pandas openpyxl duckdb plotly dash
```

### 3. Clean the Data
```bash
python utils/cleaner.py --input data/raw/blinkit_data.csv --output data/cleaned/blinkit_clean.csv
```

### 4. Load into DuckDB
```bash
python sql/sql_engine.py --load data/cleaned/blinkit_clean.csv --table blinkit
```

### 5. Run SQL Queries
```bash
python sql/sql_engine.py --query "SELECT * FROM blinkit LIMIT 5"
```

### 6. Launch Dashboard
```bash
python dashboard/dashboard.py
```
Open **http://localhost:8050** in your browser.

##  SQL Analysis & Results

### Sales by Outlet Type
```sql
SELECT outlet_type, COUNT(*) AS total_items,
       ROUND(SUM(sales), 2) AS total_sales,
       ROUND(AVG(sales), 2) AS avg_sales
FROM blinkit GROUP BY outlet_type ORDER BY total_sales DESC
```
| Outlet Type | Total Items | Total Sales | Avg Sales |
|---|---|---|---|
| Supermarket Type1 | 5,577 | ₹7,87,549 | ₹141.21 |
| Grocery Store | 1,083 | ₹1,51,939 | ₹140.29 |
| Supermarket Type2 | 928 | ₹1,31,477 | ₹141.68 |
| Supermarket Type3 | 935 | ₹1,30,714 | ₹139.80 |

###  Sales by Location Tier
```sql
SELECT outlet_location_type, COUNT(*) AS total_items,
       ROUND(SUM(sales), 2) AS total_sales
FROM blinkit GROUP BY outlet_location_type ORDER BY total_sales DESC
```
| Location | Total Items | Total Sales |
|---|---|---|
| Tier 3 | 3,350 | ₹4,72,133 |
| Tier 2 | 2,785 | ₹3,93,150 |
| Tier 1 | 2,388 | ₹3,36,397 |

### 3️ Top 10 Item Categories
```sql
SELECT item_type, ROUND(SUM(sales), 2) AS total_sales
FROM blinkit GROUP BY item_type ORDER BY total_sales DESC LIMIT 10

### 4️⃣ Fat Content vs Sales
```sql
SELECT item_fat_content, COUNT(*) AS total_items,
       ROUND(SUM(sales), 2) AS total_sales
FROM blinkit GROUP BY item_fat_content ORDER BY total_sales DESC
```
| Fat Content | Total Items | Total Sales |
|---|---|---|
| Low Fat | 5,517 | ₹7,76,319 |
| Regular | 3,006 | ₹4,25,361 |

### 5️⃣ Sales by Outlet Size
| Outlet Size | Total Items | Total Sales |
|---|---|---|
| Medium | 3,631 | ₹5,07,895 |
| Small | 3,139 | ₹4,44,794 |
| High | 1,753 | ₹2,48,991 |

### 6️⃣ Best Outlet Type + Location Combo
| Outlet Type | Location | Total Sales |
|---|---|---|
| Supermarket Type1 | Tier 2 | ₹3,93,150 |
| Supermarket Type1 | Tier 1 | ₹2,62,590 |
| Supermarket Type1 | Tier 3 | ₹1,31,809 |
| Supermarket Type2 | Tier 3 | ₹1,31,477 |


## Dashboard Features

- KPI cards — Total Sales, Avg Sales, Total Items, Avg Rating
- Sales by Outlet Type — Bar chart
- Category breakdown — Top item types
- Location performance — Tier comparison
- Fat content split — Pie chart
- Live data preview table

## 📋 Project Phases

- [x] Phase 1 — Repository setup & dataset collection
- [x] Phase 2 — Data cleaning & preprocessing
- [x] Phase 3 — SQL analysis with DuckDB
- [x] Phase 4 — Interactive dashboard (Plotly Dash)
- [ ] Phase 5 — Report generation
- [ ] Phase 6 — Advanced visualizations & business recommendations

---

## Author

**D Pragathi**
- GitHub: [pragathi009](https://github.com/pragathi009)
