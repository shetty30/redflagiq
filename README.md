# 🚨 RedFlagIQ

> Automated forensic financial analysis — input a stock ticker, get a structured red flag report in seconds.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Status](https://img.shields.io/badge/Status-In%20Development-orange?style=flat-square)
![Domain](https://img.shields.io/badge/Domain-FinTech%20%7C%20Finance-1F4E79?style=flat-square)
![Type](https://img.shields.io/badge/Type-Portfolio%20Project-green?style=flat-square)

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

| Index | Ratio | Red Flag Threshold |
|-------|-------|--------------------|
| DSRI | Days Sales Receivable Index | > 1.031 |
| GMI | Gross Margin Index | > 1.014 |
| AQI | Asset Quality Index | > 1.040 |
| SGI | Sales Growth Index | > 1.134 |
| DEPI | Depreciation Index | > 1.001 |
| SGAI | SGA Expense Index | > 1.054 |
| LVGI | Leverage Index | > 1.111 |
| TATA | Total Accruals to Total Assets | > 0.018 |

### Altman Z-Score (Bankruptcy Risk)
Predicts financial distress using 5 weighted ratios.

| Z-Score | Zone | Signal |
|---------|------|--------|
| > 2.99 | 🟢 Safe | No immediate distress |
| 1.81 – 2.99 | 🟡 Grey | Monitor closely |
| < 1.81 | 🔴 Distress | High bankruptcy risk |

### Custom Red Flag Layer
Additional heuristics on top of the formal models:
- Revenue growing but Operating Cash Flow flat or declining
- Accounts Receivable growing 2x faster than Revenue
- Gross Margin declining > 3% YoY for 2 consecutive years
- Debt-to-Equity spike > 40% in a single year
- Net Income positive but Free Cash Flow negative

---

## 🗂️ Project Structure

```
redflagiq/
│
├── data/
│   ├── raw/                  # Raw API response files
│   └── processed/            # Cleaned, structured financials
│
├── models/
│   ├── beneish_mscore.py     # Beneish M-Score logic
│   ├── altman_zscore.py      # Altman Z-Score logic
│   └── ratio_analysis.py     # Supporting financial ratios
│
├── notebooks/
│   └── analysis.ipynb        # Exploratory analysis
│
├── excel/
│   └── framework.xlsx        # Finance lead's Excel model (source of truth)
│
├── powerbi/
│   └── dashboard.pbix        # PowerBI dashboard
│
├── src/
│   ├── data_fetch.py         # Pulls data from APIs
│   ├── preprocessor.py       # Cleans and structures data
│   └── report_generator.py   # Auto-generates red flag reports
│
├── outputs/
│   └── reports/              # Generated company reports
│
├── requirements.txt
├── README.md
└── main.py                   # Entry point
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

### 3. (Optional) Set up FMP API key

If using Financial Modeling Prep API for additional data:

```bash
export FMP_API_KEY=your_api_key_here
```

> The project uses `yfinance` by default — no API key needed. FMP is an optional upgrade for richer data.

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

Where `tickers.csv` is a single-column CSV with stock tickers:

```
AAPL
MSFT
TSLA
AMZN
```

### Output

Each run generates:
- A **CSV** in `outputs/` with scores and flags for all companies
- A **PDF report** per company in `outputs/reports/`

The CSV auto-connects to the **PowerBI dashboard** when placed in the correct path.

---

## 📊 Output Example

```
Ticker  | M-Score | Z-Score | Custom Flags | Risk Rating
--------|---------|---------|--------------|-------------
AAPL    | -2.51   | 4.12    | 0            | LOW
XYZ     | -1.45   | 1.62    | 4            | HIGH
ABC     | -1.90   | 2.10    | 2            | MEDIUM
```

---

## 🧩 Tech Stack

| Layer | Tool |
|-------|------|
| Data Ingestion | `yfinance` / Financial Modeling Prep API |
| Data Processing | Python, Pandas, NumPy |
| Scoring Models | Python (translated from Excel framework) |
| Report Generation | `fpdf2` |
| Dashboard | Microsoft PowerBI |
| Financial Model | Microsoft Excel |
| Version Control | GitHub |

---

## 👥 Team

| Name | Role | Contribution |
|------|------|--------------|
| Shresti Shukla | Finance Lead | Financial framework, Beneish/Altman model design, Excel model, PowerBI dashboard |
| Shriya Shetty | Finance & Tech Lead | Data pipeline, model automation, report generation, GitHub |

---

## 🌿 Branching Strategy

```
main                      ← Production-ready code only
├── dev                   ← Integration branch (merge here first)
├── feature/data-pipeline ← Tech lead
├── feature/scoring-models← Tech lead
└── finance/excel-framework ← Finance lead (Excel + PowerBI uploads)
```

**Rules:**
- Never push directly to `main`
- All PRs go into `dev` first, merged to `main` after testing
- Finance lead uploads files via GitHub web interface — no terminal needed

---

## 📅 Roadmap

- [x] Project scoped and PRD written
- [ ] Data pipeline — pull financials via API
- [ ] Beneish M-Score automated
- [ ] Altman Z-Score automated
- [ ] Custom red flag layer
- [ ] PDF report generator
- [ ] PowerBI dashboard (Finance Lead)
- [ ] Batch processing (50 companies)
- [ ] README finalised

---

## ⚠️ Disclaimer

This project is built for **educational and portfolio purposes only**. Nothing in this tool constitutes financial, investment, or legal advice. Always consult a qualified professional before making financial decisions.

---

## 📄 License

This project is not licensed for commercial use. For academic and portfolio use only.

---

*Built as a collaborative Finance + Technology portfolio project.*