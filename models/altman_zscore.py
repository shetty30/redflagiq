"""
altman_zscore.py
----------------
Calculates the Altman Z-Score for financial distress prediction.
Translated directly from Shreshti's Excel framework.

Z > 2.99   →  Safe Zone    (low distress risk)
1.81–2.99  →  Grey Zone    (uncertain)
Z < 1.81   →  Distress Zone (high bankruptcy risk)

Note: Uses the original 1968 Altman model for publicly traded manufacturers.
For non-manufacturers / service companies, Z-Score is still widely used
as a relative benchmark even if thresholds may vary.
"""

import numpy as np
import pandas as pd


# ── Altman weights (original 1968 model) ──────────────────────────────────────
WEIGHTS = {
    "X1": 1.2,   # Working Capital / Total Assets
    "X2": 1.4,   # Retained Earnings / Total Assets
    "X3": 3.3,   # EBIT / Total Assets
    "X4": 0.6,   # Market Cap / Total Liabilities
    "X5": 1.0,   # Revenue / Total Assets
}

ZONES = {
    "safe":     2.99,
    "grey":     1.81,
}


def _safe_div(a, b, fallback=np.nan):
    """Division with zero/NaN protection."""
    try:
        if pd.isna(b) or b == 0:
            return fallback
        return a / b
    except Exception:
        return fallback


def calculate_zscore(financials: pd.DataFrame, info: dict) -> dict:
    """
    Calculate Altman Z-Score using most recent year of financials.

    Args:
        financials: cleaned DataFrame from preprocessor (rows = years, most recent first)
        info:       company info dict (must include market_cap)

    Returns:
        dict with all 5 factors, Z-Score, zone, and component breakdown
    """
    df  = financials
    row = df.iloc[0]     # Most recent year (FY2024)

    ticker    = info.get("ticker", "N/A")
    curr_year = str(df.index[0])[:4]

    # Market cap: use from info (current) — yfinance gives live market cap
    market_cap = row.get("market_cap", np.nan)
    if pd.isna(market_cap):
        market_cap = info.get("market_cap", np.nan)
        if market_cap:
            market_cap = market_cap / 1_000_000    # Convert to millions

    # ── X1 — Working Capital / Total Assets ───────────────────────────────────
    # Liquidity: can the company cover short-term obligations?
    X1 = _safe_div(row["working_cap"], row["total_assets"])

    # ── X2 — Retained Earnings / Total Assets ─────────────────────────────────
    # Cumulative profitability. Negative for Apple = aggressive buybacks, not losses.
    X2 = _safe_div(row["retained_earn"], row["total_assets"])

    # ── X3 — EBIT / Total Assets ──────────────────────────────────────────────
    # Operating efficiency: profit generated per dollar of assets.
    X3 = _safe_div(row["ebit"], row["total_assets"])

    # ── X4 — Market Cap / Total Liabilities ───────────────────────────────────
    # Market-based solvency: does market value cover all debts?
    X4 = _safe_div(market_cap, row["total_liab"])

    # ── X5 — Revenue / Total Assets ───────────────────────────────────────────
    # Asset turnover: how efficiently are assets used to generate revenue?
    X5 = _safe_div(row["revenue"], row["total_assets"])

    # ── Final Z-Score ──────────────────────────────────────────────────────────
    factors = {"X1": X1, "X2": X2, "X3": X3, "X4": X4, "X5": X5}

    # Replace NaN with 0 for score calc (conservative)
    factors_clean = {k: (v if not pd.isna(v) else 0.0) for k, v in factors.items()}

    z_score = sum(WEIGHTS[k] * v for k, v in factors_clean.items())

    # ── Weighted breakdown ─────────────────────────────────────────────────────
    weighted = {k: round(WEIGHTS[k] * factors_clean[k], 4) for k in factors}

    # ── Zone verdict ──────────────────────────────────────────────────────────
    if z_score > ZONES["safe"]:
        zone    = "SAFE ZONE"
        risk    = "LOW"
        meaning = "No immediate financial distress signal"
    elif z_score > ZONES["grey"]:
        zone    = "GREY ZONE"
        risk    = "MEDIUM"
        meaning = "Uncertain — monitor financial health closely"
    else:
        zone    = "DISTRESS ZONE"
        risk    = "HIGH"
        meaning = "High probability of financial distress"

    result = {
        "ticker":    ticker,
        "curr_year": curr_year,
        "factors":   factors,
        "weighted":  weighted,
        "z_score":   round(z_score, 4),
        "zone":      zone,
        "risk":      risk,
        "meaning":   meaning,
        "weights":   WEIGHTS,
        "market_cap_used": market_cap,
    }

    _print_results(result)
    return result


def _print_results(r: dict):
    labels = {
        "X1": "Working Capital / Total Assets",
        "X2": "Retained Earnings / Total Assets",
        "X3": "EBIT / Total Assets",
        "X4": "Market Cap / Total Liabilities",
        "X5": "Revenue / Total Assets",
    }
    print(f"\n{'='*60}")
    print(f"  ALTMAN Z-SCORE  |  {r['ticker']}  |  FY{r['curr_year']}")
    print(f"{'='*60}")
    for k, val in r["factors"].items():
        weight    = r["weights"][k]
        weighted  = r["weighted"][k]
        val_str   = f"{val:.4f}" if not pd.isna(val) else "   N/A"
        label     = labels[k]
        print(f"  {k}  ({weight}×)  {val_str:>8}  →  weighted: {weighted:>8.4f}   {label}")
    print(f"{'─'*60}")
    print(f"  Z-Score:   {r['z_score']:>8.4f}")
    print(f"  Zone:      {r['zone']}")
    print(f"  Meaning:   {r['meaning']}")
    print(f"{'='*60}\n")
