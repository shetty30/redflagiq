"""
ratio_analysis.py
-----------------
Custom red flag heuristics beyond Beneish & Altman.
Translated directly from Shreshti's Custom Red Flags Excel sheet.

These are qualitative finance checks that add an analyst lens
on top of the quantitative models.
"""

import numpy as np
import pandas as pd


RED_FLAGS = [
    {
        "id":   1,
        "name": "Revenue growing but OCF flat or declining",
        "desc": "Revenue growth > 10% AND OCF growth < 2%. "
                "Earnings not backed by actual cash generation.",
    },
    {
        "id":   2,
        "name": "Receivables growing 2x faster than revenue",
        "desc": "AR growth > 2× revenue growth. "
                "Possible fictitious or uncollected sales being booked.",
    },
    {
        "id":   3,
        "name": "Gross margin declining year-over-year",
        "desc": "Gross margin shrank compared to prior year. "
                "Core business pricing power or cost control is weakening.",
    },
    {
        "id":   4,
        "name": "Debt-to-equity spike > 40% in one year",
        "desc": "D/E ratio jumped > 40% YoY. "
                "Rapid leverage increase signals rising financial risk.",
    },
    {
        "id":   5,
        "name": "Net income positive but free cash flow negative",
        "desc": "NI > 0 but FCF < 0. "
                "Company reporting profits on paper but burning cash in reality.",
    },
]


def _safe_div(a, b, fallback=np.nan):
    try:
        if pd.isna(b) or b == 0:
            return fallback
        return a / b
    except Exception:
        return fallback


def _growth(curr, prev):
    """Year-over-year growth rate."""
    return _safe_div(curr - prev, abs(prev))


def run_red_flags(financials: pd.DataFrame, info: dict) -> dict:
    """
    Run all 5 custom red flag checks.

    Args:
        financials: cleaned DataFrame from preprocessor (most recent year first)
        info:       company info dict

    Returns:
        dict with results for each flag, count of flags triggered, severity
    """
    df = financials

    if len(df) < 2:
        raise ValueError("Custom red flags require at least 2 years of data.")

    curr = df.iloc[0]   # Current year
    prev = df.iloc[1]   # Prior year

    ticker    = info.get("ticker", "N/A")
    curr_year = str(df.index[0])[:4]
    prev_year = str(df.index[1])[:4]

    results = []

    # ── Flag 1: Revenue growing but OCF flat ──────────────────────────────────
    rev_growth = _growth(curr["revenue"], prev["revenue"])
    ocf_growth = _growth(curr["operating_cf"], prev["operating_cf"])
    flag1 = (
        not pd.isna(rev_growth) and not pd.isna(ocf_growth)
        and rev_growth > 0.10
        and ocf_growth < 0.02
    )
    results.append({
        **RED_FLAGS[0],
        "triggered": flag1,
        "detail":    f"Revenue growth: {rev_growth:.1%} | OCF growth: {ocf_growth:.1%}",
        "curr_val":  f"OCF: ${curr['operating_cf']:,.0f}M",
        "prev_val":  f"OCF: ${prev['operating_cf']:,.0f}M",
    })

    # ── Flag 2: AR growing 2x faster than revenue ─────────────────────────────
    ar_growth  = _growth(curr["accounts_rec"], prev["accounts_rec"])
    flag2 = (
        not pd.isna(ar_growth) and not pd.isna(rev_growth)
        and ar_growth > 2 * rev_growth
        and ar_growth > 0   # Only flag if AR actually grew
    )
    results.append({
        **RED_FLAGS[1],
        "triggered": flag2,
        "detail":    f"AR growth: {ar_growth:.1%} | Revenue growth: {rev_growth:.1%} "
                     f"| AR/Rev ratio: {ar_growth:.1%} vs 2×{rev_growth:.1%}={2*rev_growth:.1%}",
        "curr_val":  f"AR: ${curr['accounts_rec']:,.0f}M",
        "prev_val":  f"AR: ${prev['accounts_rec']:,.0f}M",
    })

    # ── Flag 3: Gross margin declining ────────────────────────────────────────
    gm_curr = _safe_div(curr["gross_profit"], curr["revenue"])
    gm_prev = _safe_div(prev["gross_profit"], prev["revenue"])
    flag3 = (
        not pd.isna(gm_curr) and not pd.isna(gm_prev)
        and gm_curr < gm_prev
    )
    results.append({
        **RED_FLAGS[2],
        "triggered": flag3,
        "detail":    f"Gross margin: {gm_prev:.1%} -> {gm_curr:.1%} "
                     f"(change: {gm_curr - gm_prev:+.1%})",
        "curr_val":  f"GM: {gm_curr:.1%}",
        "prev_val":  f"GM: {gm_prev:.1%}",
    })

    # ── Flag 4: D/E spike > 40% ───────────────────────────────────────────────
    equity_curr = curr["total_assets"] - curr["total_liab"]
    equity_prev = prev["total_assets"] - prev["total_liab"]
    de_curr = _safe_div(curr["long_term_debt"], equity_curr)
    de_prev = _safe_div(prev["long_term_debt"], equity_prev)
    de_change = _growth(de_curr, de_prev)
    flag4 = (
        not pd.isna(de_change)
        and abs(de_change) > 0.40
        and de_curr > de_prev   # Only flag if D/E increased
    )
    results.append({
        **RED_FLAGS[3],
        "triggered": flag4,
        "detail":    f"D/E ratio: {de_prev:.2f}x -> {de_curr:.2f}x "
                     f"(change: {de_change:+.1%})",
        "curr_val":  f"D/E: {de_curr:.2f}x",
        "prev_val":  f"D/E: {de_prev:.2f}x",
    })

    # ── Flag 5: NI positive but FCF negative ──────────────────────────────────
    flag5 = (
        not pd.isna(curr["net_income"]) and not pd.isna(curr["free_cf"])
        and curr["net_income"] > 0
        and curr["free_cf"] < 0
    )
    results.append({
        **RED_FLAGS[4],
        "triggered": flag5,
        "detail":    f"Net Income: ${curr['net_income']:,.0f}M | "
                     f"FCF: ${curr['free_cf']:,.0f}M",
        "curr_val":  f"NI: ${curr['net_income']:,.0f}M | FCF: ${curr['free_cf']:,.0f}M",
        "prev_val":  "-",
    })

    # ── Aggregate ──────────────────────────────────────────────────────────────
    triggered_count = sum(1 for r in results if r["triggered"])

    if triggered_count >= 4:
        severity = "HIGH"
    elif triggered_count >= 2:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    output = {
        "ticker":            ticker,
        "curr_year":         curr_year,
        "prev_year":         prev_year,
        "flags":             results,
        "triggered_count":   triggered_count,
        "total_flags":       len(results),
        "severity":          severity,
    }

    _print_results(output)
    return output


def _print_results(r: dict):
    print(f"\n{'='*60}")
    print(f"  CUSTOM RED FLAGS  |  {r['ticker']}  |  {r['curr_year']} vs {r['prev_year']}")
    print(f"{'='*60}")
    for flag in r["flags"]:
        icon = "🔴 FLAG" if flag["triggered"] else "✅  OK "
        print(f"  {icon}  [{flag['id']}] {flag['name']}")
        print(f"         {flag['detail']}")
    print(f"{'─'*60}")
    print(f"  Flags triggered:  {r['triggered_count']} / {r['total_flags']}")
    print(f"  Severity:         {r['severity']}")
    print(f"{'='*60}\n")
