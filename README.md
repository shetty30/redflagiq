# 🚨 RedFlagIQ

> Automated forensic financial analysis — input a stock ticker, get a structured red flag report in seconds.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-FF4B4B?style=flat-square&logo=streamlit)
![Status](https://img.shields.io/badge/Status-Complete-success?style=flat-square)
![Domain](https://img.shields.io/badge/Domain-FinTech%20%7C%20Finance-1F4E79?style=flat-square)
![Models](https://img.shields.io/badge/Models-Beneish%20%7C%20Altman%20%7C%20Custom-2E75B6?style=flat-square)
![Tested On](https://img.shields.io/badge/Tested%20On-10%20Companies-black?style=flat-square)

---

## 🚀 Live Demo

**[→ Open RedFlagIQ Dashboard](https://shetty30-redflagiq-dashboard.streamlit.app)**

---

## 📌 What This Does

Financial statement analysis is hours of manual work. Analysts cross-reference ratios across years, apply scoring models, and look for anomalies — one company at a time.

RedFlagIQ automates it.

Input a stock ticker → pull 5 years of financials → run 3 forensic models → get a structured risk report with a **Low / Medium / High** severity rating. Batch mode handles 10 companies in under 2 minutes.

---

## 🧠 Models

### Beneish M-Score — Earnings Manipulation Detection
Detects likelihood of financial statement manipulation across 8 financial ratios. Score above **−1.78** signals potential manipulation.

| Ratio | What It Checks | Red Flag |
|-------|---------------|----------|
| DSRI | Receivables growing faster than sales | > 1.031 |
| GMI | Gross margin deteriorating | > 1.014 |
| AQI | Non-productive assets growing | > 1.040 |
| SGI | Revenue growth pressure | > 1.134 |
| DEPI | Depreciation rate slowing | > 1.001 |
| SGAI | Overheads outpacing revenue | > 1.054 |
| TATA | Earnings not backed by cash | > 0.018 |
| LVGI | Leverage increasing | > 1.111 |

**Verdict:** `> −1.78` = 🔴 Likely Manipulator · `−2.22 to −1.78` = 🟡 Grey Zone · `< −2.22` = 🟢 Unlikely

---

### Altman Z-Score — Bankruptcy & Distress Prediction
Predicts financial distress using 5 weighted ratios.

| Factor | Ratio | Weight |
|--------|-------|--------|
| X1 | Working Capital / Total Assets | 1.2× |
| X2 | Retained Earnings / Total Assets | 1.4× |
| X3 | EBIT / Total Assets | 3.3× |
| X4 | Market Cap / Total Liabilities | 0.6× |
| X5 | Revenue / Total Assets | 1.0× |

**Zones:** `> 2.99` = 🟢 Safe · `1.81–2.99` = 🟡 Grey · `< 1.81` = 🔴 Distress

---

### Custom Red Flag Layer — Analyst Heuristics
5 qualitative checks built from the finance team's Excel framework:

- Revenue growing but Operating Cash Flow flat or declining
- Accounts Receivable growing 2× faster than Revenue
- Gross Margin declining year-over-year
- Debt-to-Equity spike > 40% in a single year
- Net Income positive but Free Cash Flow negative

---

## 📊 Dashboard — 5 Pages

Built with Streamlit + Plotly. Deployed on Streamlit Cloud.

| Page | What It Shows |
|------|--------------|
| Overview | KPI cards, M-Score bar chart, risk donut, company risk table, recent activity |
| Company View | Gauges, flag checklist, score progress bars — per company |
| Comparison | Risk quadrant scatter plot, M/Z-Score rankings, full comparison table |
| Beneish M-Score | 8 ratio breakdown, formula, AAPL walkthrough, all-company bars |
| Altman Z-Score | 5 factor breakdown, zone reference, AAPL walkthrough, all-company bars |

---

## 🗂️ Project Structure

```
redflagiq/
│
├── data/
│   ├── raw/                  # Raw API response files (auto-generated)
│   └── processed/            # Cleaned, structured financials (auto-generated)
│
├── models/
│   ├── beneish_mscore.py     # Beneish M-Score — 8 ratios + weighted formula
│   ├── altman_zscore.py      # Altman Z-Score — 5 factors + zone classification
│   └── ratio_analysis.py     # Custom red flag heuristics — 5 analyst checks
│
├── notebooks/
│   └── analysis.ipynb        # Step-by-step AAPL exploratory analysis (33 cells)
│
├── excel/
│   └── framework.xlsx        # Finance lead's Excel model — source of truth
│
├── src/
│   ├── data_fetch.py         # Fetches financials via yfinance — single + batch
│   ├── preprocessor.py       # Cleans raw data, standardises line items
│   └── report_generator.py   # Auto-generates per-company PDF reports
│
├── outputs/
│   ├── reports/              # Generated PDF reports per company
│   └── results.csv           # Structured output — feeds Streamlit dashboard
│
├── dashboard.py              # Streamlit dashboard — 5-page interactive app
├── main.py                   # Pipeline entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run Locally

### 1. Clone

```bash
git clone https://github.com/shetty30/redflagiq.git
cd redflagiq
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Run pipeline

```bash
# Single company
python main.py --ticker AAPL

# Batch
python main.py --batch tickers.csv
```

### 4. Launch dashboard

```bash
streamlit run dashboard.py
```

---

## 🧩 Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Data Ingestion | `yfinance` | Pull 5 years of financial statements |
| Data Processing | `pandas`, `numpy` | Clean and standardise raw data |
| Scoring Models | Python | Beneish, Altman, custom flag logic |
| Report Generation | `fpdf2` | Auto-generate per-company PDF |
| Dashboard | Streamlit + Plotly | 5-page interactive web app |
| Financial Model | Microsoft Excel | Logic framework — source of truth |
| Notebook | Jupyter | Exploratory analysis — 33 cells |
| Version Control | GitHub | Collaboration and CI |

---

## 👥 Team

| Name | Role | Contribution |
|------|------|--------------|
| **Shriya Shetty** | Finance & Tech Lead | Data pipeline, model automation in Python, PDF report generator, Streamlit dashboard, Jupyter notebook, GitHub |
| **Shreshti Shukla** | Finance Lead | Beneish & Altman framework research, Excel model (source of truth), custom red flag logic, analyst findings |

---

## 🌿 Branching Strategy

```
main                          ← Production. No direct pushes.
├── dev                       ← Integration branch
├── feature/data-pipeline     ← Tech lead
├── feature/scoring-models    ← Tech lead
└── finance/excel-framework   ← Finance lead
```

---

## 📅 Roadmap

- [x] Project scoped — PRD written
- [x] Data pipeline — yfinance with retry + batch mode
- [x] Beneish M-Score automated — 8 ratios
- [x] Altman Z-Score automated — 5 factors
- [x] Custom red flag layer — 5 heuristic checks
- [x] PDF report generator
- [x] Pipeline entry point — `main.py`
- [x] Jupyter notebook — 33-cell AAPL walkthrough
- [x] Excel model — finance framework (Shreshti)
- [x] Cross-validation — Python output matches Excel exactly
- [x] Streamlit dashboard — 5 pages, deployed on Streamlit Cloud
- [x] Batch tested — 10 S&P listed companies

---



*Built by Shriya Shetty & Shreshti Shukla — RedFlagIQ · Finance + Technology Portfolio Project*
