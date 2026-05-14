# 🚨 RedFlagIQ

> Automated forensic financial analysis — input a stock ticker, get a structured red flag report in seconds.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)
![Domain](https://img.shields.io/badge/Domain-FinTech%20%7C%20Finance-1F4E79?style=flat-square)
![Type](https://img.shields.io/badge/Type-Portfolio%20Project-green?style=flat-square)
![Models](https://img.shields.io/badge/Models-Beneish%20%7C%20Altman%20%7C%20Custom-2E75B6?style=flat-square)
![Tested On](https://img.shields.io/badge/Tested%20On-AAPL-black?style=flat-square&logo=apple)

---

## 📌 What This Does

Analysing financial statements for red flags is tedious and time-consuming. Analysts manually cross-reference ratios across years, apply scoring models, and look for anomalies — hours of work per company.

This tool automates it.

Input a stock ticker → the system pulls 5 years of financials → runs **Beneish M-Score**, **Altman Z-Score**, and a **custom red flag layer** → outputs a structured risk report with a **Low / Medium / High** severity rating.

Run it across 50 companies in under 10 minutes.

---

## 🧠 Models Used

### Beneish M-Score (Earnings Manipulation)
Detects likelihood of financial statement manipulation using 8 financial ratios. A score above **-1.78** signals potential manipulation.

| Index | Ratio | What It Checks | Red Flag Threshold |
|-------|-------|----------------|--------------------|
| DSRI | Days Sales Receivable Index | Receivables growing faster than sales? | > 1.031 |
| GMI | Gross Margin Index | Gross margin deteriorating? | > 1.014 |
| AQI | Asset Quality Index | Non-productive assets growing? | > 1.040 |
| SGI | Sales Growth Index | Growth so high it creates manipulation pressure? | > 1.134 |
| DEPI | Depreciation Index | Depreciation being slowed to inflate assets? | > 1.001 |
| SGAI | SGA Expense Index | Overheads growing faster than revenue? | > 1.054 |
| LVGI | Leverage Index | Debt rising relative to assets? | > 1.111 |
| TATA | Total Accruals to Total Assets | Earnings backed by real cash? | > 0.018 |

**M-Score Interpretation:**
- `> -1.78` → 🔴 Likely Manipulator
- `-2.22 to -1.78` → 🟡 Grey Zone — Monitor
- `< -2.22` → 🟢 Unlikely Manipulator

---

### Altman Z-Score (Bankruptcy Risk)
Predicts financial distress using 5 weighted ratios.

| Factor | Ratio | Weight |
|--------|-------|--------|
| X1 | Working Capital / Total Assets | 1.2 |
| X2 | Retained Earnings / Total Assets | 1.4 |
| X3 | EBIT / Total Assets | 3.3 |
| X4 | Market Cap / Total Liabilities | 0.6 |
| X5 | Revenue / Total Assets | 1.0 |

**Z-Score Zones:**

| Z-Score | Zone | Signal |
|---------|------|--------|
| > 2.99 | 🟢 Safe | No immediate distress |
| 1.81 – 2.99 | 🟡 Grey | Monitor closely |
| < 1.81 | 🔴 Distress | High bankruptcy risk |

---

### Custom Red Flag Layer
Analyst heuristics on top of the formal models — translated from the finance team's Excel framework:

- Revenue growing but Operating Cash Flow flat or declining
- Accounts Receivable growing 2x faster than Revenue
- Gross Margin declining year-over-year
- Debt-to-Equity spike > 40% in a single year
- Net Income positive but Free Cash Flow negative

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
│   ├── beneish_mscore.py     # Beneish M-Score — all 8 ratios + weighted formula
│   ├── altman_zscore.py      # Altman Z-Score — all 5 factors + zone classification
│   └── ratio_analysis.py     # Custom red flag heuristics — 5 analyst checks
│
├── notebooks/
│   └── analysis.ipynb        # Step-by-step AAPL exploratory analysis (33 cells)
│
├── excel/
│   └── framework.xlsx        # Finance lead's Excel model — source of truth for all logic
│
├── powerbi/
│   └── dashboard.pbix        # PowerBI dashboard — connects to outputs/results.csv
│
├── src/
│   ├── data_fetch.py         # Fetches financials via yfinance — single + batch mode
│   ├── preprocessor.py       # Cleans raw data, standardises line items
│   └── report_generator.py   # Auto-generates per-company PDF reports
│
├── outputs/
│   ├── reports/              # Generated PDF reports per company
│   └── results.csv           # Structured output — feeds PowerBI dashboard directly
│
├── requirements.txt
├── README.md
└── main.py                   # Entry point — full pipeline in one command
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- pip

### 1. Clone the repo

```bash
git clone https://github.com/shetty30/redflagiq.git
cd redflagiq
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **requirements.txt includes:** `yfinance`, `pandas`, `numpy`, `fpdf2`, `openpyxl`

---

## 🚀 Usage

### Single company analysis

```bash
python main.py --ticker AAPL
```

### Batch analysis (multiple companies)

```bash
python main.py --batch tickers.csv
```

Where `tickers.csv` is a single-column CSV with one ticker per row:

```
AAPL
MSFT
TSLA
AMZN
```

### Use cached data (skip re-fetching)

```bash
python main.py --ticker AAPL --no-fetch
```

### Exploratory analysis (notebook)

```bash
cd notebooks
jupyter notebook analysis.ipynb
```

---

## 📊 What Gets Generated

### Per-company PDF Report
Auto-generated in `outputs/reports/` containing:
- Company info and analysis period
- Beneish M-Score with all 8 ratio values and flags
- Altman Z-Score with all 5 weighted factors
- Custom red flag checklist with details
- Overall Risk Rating — LOW / MEDIUM / HIGH

### Structured CSV (for PowerBI)
Saved to `outputs/results.csv` — Shreshti's PowerBI dashboard connects to this file directly.

| Column | Description |
|--------|-------------|
| `ticker` | Stock ticker |
| `m_score` | Beneish M-Score value |
| `m_score_verdict` | Likely Manipulator / Grey Zone / Unlikely |
| `z_score` | Altman Z-Score value |
| `z_score_zone` | Safe / Grey / Distress |
| `custom_flags_triggered` | Number of custom flags triggered (0–5) |
| `overall_risk` | LOW / MEDIUM / HIGH |

### Terminal Output Example

```
══════════════════════════════════════════════════════════════════════
  REDFLAGIQ BATCH SUMMARY
══════════════════════════════════════════════════════════════════════
  TICKER   COMPANY                   M-SCORE  Z-SCORE  FLAGS  RISK
  ──────────────────────────────────────────────────────────────────
  AAPL     Apple Inc.                  -2.89     8.85      1  🟢 LOW
  XYZ      XYZ Corp                    -1.45     1.62      4  🔴 HIGH
  ABC      ABC Holdings                -1.90     2.10      2  🟡 MEDIUM
══════════════════════════════════════════════════════════════════════
```

---

## 🧩 Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Data Ingestion | `yfinance` | Pull 5 years of financial statements |
| Data Processing | `pandas`, `numpy` | Clean, standardise, structure raw data |
| Scoring Models | Python | Beneish M-Score, Altman Z-Score, custom flags |
| Report Generation | `fpdf2` | Auto-generate per-company PDF reports |
| CSV Export | `pandas` | Feed structured results to PowerBI |
| Dashboard | Microsoft PowerBI | Visualise scores across companies |
| Financial Model | Microsoft Excel | Logic framework — source of truth |
| Notebook | Jupyter | Step-by-step exploratory analysis |
| Version Control | GitHub | Collaboration and code management |

---

## 👥 Team

| Name | Role | Contribution |
|------|------|--------------|
| Shreshti Shukla | Finance Lead | Beneish/Altman research, Excel model framework, custom red flag logic, PowerBI dashboard |
| Shriya Shetty | Finance & Tech Lead | Data pipeline, model automation, PDF report generator, notebook, GitHub |

---

## 🌿 Branching Strategy

```
main                        ← Production-ready code only. No direct pushes.
├── dev                     ← Integration branch. Merge here first.
├── feature/data-pipeline   ← Tech lead
├── feature/scoring-models  ← Tech lead
└── finance/excel-framework ← Finance lead (Excel + PowerBI file uploads only)
```

**Rules:**
- Never push directly to `main`
- All PRs merge into `dev` first, then `dev` → `main` after testing
- Finance lead uploads files via GitHub web interface — no terminal needed
- `excel/framework.xlsx` is never edited directly by the tech lead

---

## 📅 Roadmap

- [x] Project scoped — PRD written
- [x] README documented
- [x] Folder structure set up
- [x] `data_fetch.py` — yfinance pipeline with retry + batch mode
- [x] `preprocessor.py` — data cleaning and standardisation
- [x] `beneish_mscore.py` — all 8 ratios automated
- [x] `altman_zscore.py` — all 5 factors automated
- [x] `ratio_analysis.py` — 5 custom red flag checks
- [x] `report_generator.py` — PDF report auto-generation
- [x] `main.py` — full pipeline entry point
- [x] `analysis.ipynb` — AAPL exploratory notebook (33 cells)
- [x] Excel model — pre-filled AAPL framework (Shreshti)
- [ ] PowerBI dashboard (Shreshti — in progress)
- [ ] Batch test across 50 companies
- [ ] Validation — Python output vs Excel output cross-check

---

## ⚠️ Disclaimer

This project is built for **educational and portfolio purposes only**. Nothing in this tool constitutes financial, investment, or legal advice. Always consult a qualified professional before making financial decisions.

---

## 📄 License

Not licensed for commercial use. For academic and portfolio use only.

---

*Built by Shriya Shetty & Shreshti Shukla | RedFlagIQ — Finance + Technology Portfolio Project*
