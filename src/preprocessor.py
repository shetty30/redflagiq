
import os
import json
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")




INCOME_MAP = {
    "revenue":         ["Total Revenue", "Revenue", "TotalRevenue"],
    "cogs":            ["Cost Of Revenue", "Cost of Revenue", "CostOfRevenue",
                        "Cost Of Goods Sold"],
    "gross_profit":    ["Gross Profit", "GrossProfit"],
    "sga":             ["Selling General Administrative",
                        "Selling General And Administrative",
                        "SG&A", "Selling And Marketing Expense"],
    "depreciation":    ["Reconciled Depreciation", "Depreciation",
                        "Depreciation And Amortization",
                        "DepreciationAndAmortization"],
    "ebit":            ["EBIT", "Operating Income", "OperatingIncome",
                        "Total Operating Income As Reported"],
    "net_income":      ["Net Income", "NetIncome",
                        "Net Income Common Stockholders"],
}

BALANCE_MAP = {
    "total_assets":    ["Total Assets", "TotalAssets"],
    "current_assets":  ["Current Assets", "TotalCurrentAssets",
                        "Total Current Assets"],
    "current_liab":    ["Current Liabilities", "TotalCurrentLiabilities",
                        "Total Current Liabilities"],
    "accounts_rec":    ["Accounts Receivable", "Net Receivables",
                        "AccountsReceivable", "Receivables"],
    "long_term_debt":  ["Long Term Debt", "LongTermDebt",
                        "Long Term Debt And Capital Lease Obligation"],
    "total_liab":      ["Total Liabilities Net Minority Interest",
                        "Total Liabilities", "TotalLiabilitiesNetMinorityInterest"],
    "retained_earn":   ["Retained Earnings", "RetainedEarnings"],
    "intangibles":     ["Goodwill And Other Intangible Assets",
                        "Intangible Assets", "GoodwillAndOtherIntangibleAssets",
                        "Goodwill"],
}

CASHFLOW_MAP = {
    "operating_cf":    ["Operating Cash Flow", "Cash Flow From Continuing "
                        "Operating Activities", "Total Cash From Operating Activities"],
    "capex":           ["Capital Expenditure", "Purchase Of Property Plant And Equipment",
                        "Capital Expenditures"],
}


def _extract(df: pd.DataFrame, field_map: dict, field: str) -> pd.Series:
    """Try each alias for a field until one is found in the dataframe."""
    aliases = field_map.get(field, [])
    for alias in aliases:
        if alias in df.index:
            return df.loc[alias]
   
    return pd.Series(np.nan, index=df.columns)


def _to_millions(series: pd.Series) -> pd.Series:
    """Convert raw values to millions and round to 2 decimal places."""
    return (series / 1_000_000).round(2)


def preprocess(raw_data: dict) -> dict:
    """
    Clean and extract key financials from raw yfinance data.

    Args:
        raw_data: dict from data_fetch.fetch_financials()
                  keys: 'income', 'balance', 'cashflow', 'info'

    Returns:
        dict with standardised annual metrics, most recent year first.
        All monetary values in USD Millions.
    """
    income   = raw_data["income"]
    balance  = raw_data["balance"]
    cashflow = raw_data["cashflow"]
    info     = raw_data["info"]
    ticker   = info["ticker"]

    
    common_years = income.columns.intersection(
                   balance.columns).intersection(cashflow.columns)

    if len(common_years) < 2:
        raise ValueError(
            f"[{ticker}] Insufficient overlapping years across statements. "
            f"Need at least 2 years for ratio analysis."
        )

    
    common_years = sorted(common_years, reverse=True)[:5]
    income   = income[common_years]
    balance  = balance[common_years]
    cashflow = cashflow[common_years]

    
    def get_income(field):
        return _to_millions(_extract(income, INCOME_MAP, field))

    def get_balance(field):
        return _to_millions(_extract(balance, BALANCE_MAP, field))

    def get_cashflow(field):
        return _to_millions(_extract(cashflow, CASHFLOW_MAP, field))

    revenue       = get_income("revenue")
    cogs          = get_income("cogs")
    gross_profit  = get_income("gross_profit")
    sga           = get_income("sga")
    depreciation  = get_income("depreciation")
    ebit          = get_income("ebit")
    net_income    = get_income("net_income")

    total_assets  = get_balance("total_assets")
    current_assets= get_balance("current_assets")
    current_liab  = get_balance("current_liab")
    accounts_rec  = get_balance("accounts_rec")
    long_term_debt= get_balance("long_term_debt")
    total_liab    = get_balance("total_liab")
    retained_earn = get_balance("retained_earn")
    intangibles   = get_balance("intangibles")

    operating_cf  = get_cashflow("operating_cf")
    capex_raw     = get_cashflow("capex")

    
    capex         = capex_raw.abs()
    free_cf       = operating_cf - capex

   
    working_cap   = current_assets - current_liab

    
    if gross_profit.isna().all():
        gross_profit = revenue - cogs

    
    clean = pd.DataFrame({
        "revenue":        revenue,
        "cogs":           cogs,
        "gross_profit":   gross_profit,
        "sga":            sga,
        "depreciation":   depreciation,
        "ebit":           ebit,
        "net_income":     net_income,
        "total_assets":   total_assets,
        "current_assets": current_assets,
        "current_liab":   current_liab,
        "working_cap":    working_cap,
        "accounts_rec":   accounts_rec,
        "long_term_debt": long_term_debt,
        "total_liab":     total_liab,
        "retained_earn":  retained_earn,
        "intangibles":    intangibles,
        "operating_cf":   operating_cf,
        "capex":          capex,
        "free_cf":        free_cf,
    })

   
    market_cap = info.get("market_cap")
    clean["market_cap"] = (market_cap / 1_000_000) if market_cap else np.nan

    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DIR, f"{ticker}_processed.csv")
    clean.to_csv(out_path)

    print(f"[RedFlagIQ] ✅ Processed data saved → data/processed/{ticker}_processed.csv")
    print(f"[RedFlagIQ]    Years available: {[str(c.date()) for c in clean.index]}")

    return {
        "ticker":    ticker,
        "info":      info,
        "financials": clean,
    }


def load_processed(ticker: str) -> dict:
    """
    Load previously processed data from disk.
    Useful to avoid re-fetching if data already exists.
    """
    ticker   = ticker.upper().strip()
    path     = os.path.join(PROCESSED_DIR, f"{ticker}_processed.csv")
    info_path= os.path.join(
        os.path.dirname(__file__), "..", "data", "raw", ticker, "info.json"
    )

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No processed data found for {ticker}. Run fetch_financials() first."
        )

    df = pd.read_csv(path, index_col=0, parse_dates=True)
    info = {}
    if os.path.exists(info_path):
        with open(info_path) as f:
            info = json.load(f)

    return {"ticker": ticker, "info": info, "financials": df}
