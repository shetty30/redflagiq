"""
beneish_mscore.py
-----------------
Calculates the Beneish M-Score for earnings manipulation detection.
Translated directly from Shreshti's Excel framework.

M-Score > -1.78  →  Likely Manipulator
M-Score > -2.22  →  Grey Zone
M-Score < -2.22  →  Unlikely Manipulator
"""

import numpy as np
import pandas as pd


# ── Beneish weights (original 1999 paper) ─────────────────────────────────────
WEIGHTS = {
    "intercept": -4.84,
    "DSRI":  0.920,
    "GMI":   0.528,
    "AQI":   0.404,
    "SGI":   0.892,
    "DEPI":  0.115,
    "SGAI": -0.172,
    "TATA": -0.327,
    "LVGI":  4.679,
}

THRESHOLDS = {
    "DSRI":  1.031,
    "GMI":   1.014,
    "AQI":   1.040,
    "SGI":   1.134,
    "DEPI":  1.001,
    "SGAI":  1.054,
    "TATA":  0.018,
    "LVGI":  1.111,
}


def _safe_div(a, b, fallback=np.nan):
    """Division with zero/NaN protection."""
    try:
        if pd.isna(b) or b == 0:
            return fallback
        return a / b
    except Exception:
        return fallback


def calculate_mscore(financials: pd.DataFrame, info: dict) -> dict:
    """
    Calculate Beneish M-Score using two consecutive years of financials.

    Args:
        financials: cleaned DataFrame from preprocessor (rows = years, most recent first)
        info:       company info dict

    Returns:
        dict with all 8 ratios, final M-Score, verdict, and flagged ratios
    """
    df = financials

    if len(df) < 2:
        raise ValueError("Beneish M-Score requires at least 2 years of data.")

    # Most recent = current year (t), next row = prior year (t-1)
    curr = df.iloc[0]   # FY2024
    prev = df.iloc[1]   # FY2023

    ticker = info.get("ticker", "N/A")
    curr_year = str(df.index[0])[:4]
    prev_year = str(df.index[1])[:4]

    # ── 1. DSRI — Days Sales Receivable Index ─────────────────────────────────
    # Measures: Are receivables growing faster than sales?
    dsri_curr = _safe_div(curr["accounts_rec"], curr["revenue"])
    dsri_prev = _safe_div(prev["accounts_rec"], prev["revenue"])
    DSRI = _safe_div(dsri_curr, dsri_prev)

    # ── 2. GMI — Gross Margin Index ───────────────────────────────────────────
    # Measures: Is gross margin deteriorating?
    gm_curr = _safe_div(curr["gross_profit"], curr["revenue"])
    gm_prev = _safe_div(prev["gross_profit"], prev["revenue"])
    GMI = _safe_div(gm_prev, gm_curr)          # Note: prior / current (inverse)

    # ── 3. AQI — Asset Quality Index ──────────────────────────────────────────
    # Measures: Are non-productive (soft) assets growing?
    # Non-current non-physical assets = Total Assets - Current Assets - PPE proxy
    def asset_quality_ratio(row):
        ppe_proxy = row["total_assets"] - row["current_assets"]
        numerator = row["total_assets"] - row["current_assets"] - ppe_proxy
        return _safe_div(numerator, row["total_assets"])

    aq_curr = _safe_div(
        curr["intangibles"] if not pd.isna(curr["intangibles"]) else 0,
        curr["total_assets"]
    )
    aq_prev = _safe_div(
        prev["intangibles"] if not pd.isna(prev["intangibles"]) else 0,
        prev["total_assets"]
    )
    AQI = _safe_div(aq_curr, aq_prev) if aq_prev != 0 else 1.0

    # ── 4. SGI — Sales Growth Index ───────────────────────────────────────────
    # Measures: Is revenue growth very high (pressure to sustain)?
    SGI = _safe_div(curr["revenue"], prev["revenue"])

    # ── 5. DEPI — Depreciation Index ──────────────────────────────────────────
    # Measures: Is the company slowing depreciation to inflate assets?
    def depr_rate(row):
        ppe = row["total_assets"] - row["current_assets"]
        return _safe_div(row["depreciation"], row["depreciation"] + ppe)

    depr_curr = depr_rate(curr)
    depr_prev = depr_rate(prev)
    DEPI = _safe_div(depr_prev, depr_curr)     # prior / current

    # ── 6. SGAI — SGA Expense Index ───────────────────────────────────────────
    # Measures: Are overheads growing faster than revenue?
    sgai_curr = _safe_div(curr["sga"], curr["revenue"])
    sgai_prev = _safe_div(prev["sga"], prev["revenue"])
    SGAI = _safe_div(sgai_curr, sgai_prev)

    # ── 7. LVGI — Leverage Index ──────────────────────────────────────────────
    # Measures: Is debt rising relative to assets?
    lev_curr = _safe_div(
        curr["long_term_debt"] + curr["current_liab"], curr["total_assets"]
    )
    lev_prev = _safe_div(
        prev["long_term_debt"] + prev["current_liab"], prev["total_assets"]
    )
    LVGI = _safe_div(lev_curr, lev_prev)

    # ── 8. TATA — Total Accruals to Total Assets ──────────────────────────────
    # Measures: Are earnings backed by real cash?
    TATA = _safe_div(
        curr["net_income"] - curr["operating_cf"],
        curr["total_assets"]
    )

    # ── Final M-Score ──────────────────────────────────────────────────────────
    ratios = {
        "DSRI": DSRI, "GMI": GMI, "AQI": AQI, "SGI": SGI,
        "DEPI": DEPI, "SGAI": SGAI, "TATA": TATA, "LVGI": LVGI,
    }

    # Handle NaN ratios — replace with neutral value 1.0 to avoid breaking score
    ratios_clean = {k: (v if not pd.isna(v) else 1.0) for k, v in ratios.items()}

    m_score = (
        WEIGHTS["intercept"]
        + WEIGHTS["DSRI"]  * ratios_clean["DSRI"]
        + WEIGHTS["GMI"]   * ratios_clean["GMI"]
        + WEIGHTS["AQI"]   * ratios_clean["AQI"]
        + WEIGHTS["SGI"]   * ratios_clean["SGI"]
        + WEIGHTS["DEPI"]  * ratios_clean["DEPI"]
        + WEIGHTS["SGAI"]  * ratios_clean["SGAI"]
        + WEIGHTS["TATA"]  * ratios_clean["TATA"]
        + WEIGHTS["LVGI"]  * ratios_clean["LVGI"]
    )

    # ── Verdict ────────────────────────────────────────────────────────────────
    if m_score > -1.78:
        verdict = "LIKELY MANIPULATOR"
        risk    = "HIGH"
    elif m_score > -2.22:
        verdict = "GREY ZONE - Monitor"
        risk    = "MEDIUM"
    else:
        verdict = "UNLIKELY MANIPULATOR"
        risk    = "LOW"

    # ── Flag individual ratios ─────────────────────────────────────────────────
    flagged = []
    for ratio_name, value in ratios.items():
        threshold = THRESHOLDS[ratio_name]
        if not pd.isna(value) and value > threshold:
            flagged.append(ratio_name)

    result = {
        "ticker":       ticker,
        "curr_year":    curr_year,
        "prev_year":    prev_year,
        "ratios":       ratios,
        "m_score":      round(m_score, 4),
        "verdict":      verdict,
        "risk":         risk,
        "flagged_ratios": flagged,
        "thresholds":   THRESHOLDS,
    }

    _print_results(result)
    return result


def _print_results(r: dict):
    print(f"\n{'='*55}")
    print(f"  BENEISH M-SCORE  |  {r['ticker']}  |  {r['curr_year']} vs {r['prev_year']}")
    print(f"{'='*55}")
    for name, val in r["ratios"].items():
        threshold = r["thresholds"][name]
        flag = "🔴" if (not pd.isna(val) and val > threshold) else "✅"
        val_str = f"{val:.4f}" if not pd.isna(val) else "  N/A"
        print(f"  {flag}  {name:<6}  {val_str:>8}   (threshold: >{threshold})")
    print(f"{'─'*55}")
    print(f"  M-Score:   {r['m_score']:>8.4f}")
    print(f"  Verdict:   {r['verdict']}")
    if r["flagged_ratios"]:
        print(f"  Flagged:   {', '.join(r['flagged_ratios'])}")
    print(f"{'='*55}\n")
