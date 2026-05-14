"""
beneish_mscore.py
-----------------
Calculates the Beneish M-Score for earnings manipulation detection.
Translated directly from Shreshti's Excel framework.

M-Score > -1.78  ->  Likely Manipulator
M-Score > -2.22  ->  Grey Zone
M-Score < -2.22  ->  Unlikely Manipulator

Fix log:
- DEPI: removed incorrect PPE proxy using total_assets - current_assets.
  Now uses depreciation / (depreciation + capex) as PPE proxy.
- LVGI: uses long_term_debt only per Beneish (1999) paper, not total liabilities.
- NaN fallback changed to ratio-specific neutral values (not blanket 1.0).
"""

import numpy as np
import pandas as pd

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

NEUTRAL = {
    "DSRI": 1.0,
    "GMI":  1.0,
    "AQI":  1.0,
    "SGI":  1.0,
    "DEPI": 1.0,
    "SGAI": 1.0,
    "TATA": 0.0,
    "LVGI": 1.0,
}


def _safe_div(a, b, fallback=np.nan):
    try:
        if pd.isna(b) or b == 0:
            return fallback
        result = a / b
        return fallback if np.isinf(result) else result
    except Exception:
        return fallback


def _get(row, col, fallback=np.nan):
    try:
        val = row[col]
        return val if not pd.isna(val) else fallback
    except Exception:
        return fallback


def calculate_mscore(financials: pd.DataFrame, info: dict) -> dict:
    df = financials

    if len(df) < 2:
        raise ValueError("Beneish M-Score requires at least 2 years of data.")

    curr = df.iloc[0]
    prev = df.iloc[1]

    ticker    = info.get("ticker", "N/A")
    curr_year = str(df.index[0])[:4]
    prev_year = str(df.index[1])[:4]

    # 1. DSRI
    dsri_curr = _safe_div(_get(curr, "accounts_rec"), _get(curr, "revenue"))
    dsri_prev = _safe_div(_get(prev, "accounts_rec"), _get(prev, "revenue"))
    DSRI      = _safe_div(dsri_curr, dsri_prev)

    # 2. GMI — inverse (prior / current)
    gm_curr = _safe_div(_get(curr, "gross_profit"), _get(curr, "revenue"))
    gm_prev = _safe_div(_get(prev, "gross_profit"), _get(prev, "revenue"))
    GMI     = _safe_div(gm_prev, gm_curr)

    # 3. AQI — intangibles / total assets proxy
    def _aq(row):
        ta    = _get(row, "total_assets")
        intan = _get(row, "intangibles", 0)
        if pd.isna(ta) or ta == 0:
            return np.nan
        return intan / ta

    aq_curr = _aq(curr)
    aq_prev = _aq(prev)
    AQI = 1.0 if (pd.isna(aq_prev) or aq_prev == 0) else _safe_div(aq_curr, aq_prev, 1.0)

    # 4. SGI
    SGI = _safe_div(_get(curr, "revenue"), _get(prev, "revenue"))

    # 5. DEPI — inverse (prior / current)
    # Uses dep / (dep + capex) as PPE proxy — avoids the massive
    # total_assets - current_assets number that inflated DEPI before.
    def _depr_rate(row):
        dep   = _get(row, "depreciation")
        capex = _get(row, "capex", 0)
        if pd.isna(dep) or dep == 0:
            return np.nan
        denominator = dep + abs(capex)
        return _safe_div(dep, denominator)

    DEPI = _safe_div(_depr_rate(prev), _depr_rate(curr))

    # 6. SGAI
    sgai_curr = _safe_div(_get(curr, "sga"), _get(curr, "revenue"))
    sgai_prev = _safe_div(_get(prev, "sga"), _get(prev, "revenue"))
    SGAI      = _safe_div(sgai_curr, sgai_prev)

    # 7. LVGI — long-term debt / total assets only (per original paper)
    lev_curr = _safe_div(_get(curr, "long_term_debt"), _get(curr, "total_assets"))
    lev_prev = _safe_div(_get(prev, "long_term_debt"), _get(prev, "total_assets"))
    LVGI     = _safe_div(lev_curr, lev_prev)

    # 8. TATA
    TATA = _safe_div(
        _get(curr, "net_income") - _get(curr, "operating_cf"),
        _get(curr, "total_assets")
    )

    ratios = {
        "DSRI": DSRI, "GMI": GMI, "AQI": AQI, "SGI": SGI,
        "DEPI": DEPI, "SGAI": SGAI, "TATA": TATA, "LVGI": LVGI,
    }

    ratios_clean = {
        k: (v if (not pd.isna(v) and not np.isinf(v)) else NEUTRAL[k])
        for k, v in ratios.items()
    }

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

    if m_score > -1.78:
        verdict = "LIKELY MANIPULATOR"
        risk    = "HIGH"
    elif m_score > -2.22:
        verdict = "GREY ZONE - Monitor"
        risk    = "MEDIUM"
    else:
        verdict = "UNLIKELY MANIPULATOR"
        risk    = "LOW"

    flagged = [
        name for name, value in ratios.items()
        if not pd.isna(value) and not np.isinf(value) and value > THRESHOLDS[name]
    ]

    result = {
        "ticker":         ticker,
        "curr_year":      curr_year,
        "prev_year":      prev_year,
        "ratios":         ratios,
        "m_score":        round(m_score, 4),
        "verdict":        verdict,
        "risk":           risk,
        "flagged_ratios": flagged,
        "thresholds":     THRESHOLDS,
    }

    _print_results(result)
    return result


def _print_results(r: dict):
    print(f"\n{'='*58}")
    print(f"  BENEISH M-SCORE  |  {r['ticker']}  |  {r['curr_year']} vs {r['prev_year']}")
    print(f"{'='*58}")
    for name, val in r["ratios"].items():
        threshold = r["thresholds"][name]
        flag      = "🔴" if (not pd.isna(val) and val > threshold) else "✅"
        val_str   = f"{val:.4f}" if (val == val and not np.isinf(val)) else "  N/A"
        print(f"  {flag}  {name:<6}  {val_str:>8}   (threshold: >{threshold})")
    print(f"{'─'*58}")
    print(f"  M-Score :  {r['m_score']:>8.4f}")
    print(f"  Verdict :  {r['verdict']}")
    if r["flagged_ratios"]:
        print(f"  Flagged :  {', '.join(r['flagged_ratios'])}")
    print(f"{'='*58}\n")