"""
main.py
-------
RedFlagIQ — Financial Statement Red Flag Detector
Full pipeline entry point.

Usage:
    # Single ticker
    python main.py --ticker AAPL

    # Batch from CSV
    python main.py --batch tickers.csv

    # Skip fetching (use cached data)
    python main.py --ticker AAPL --no-fetch
"""

import os
import sys
import argparse
import pandas as pd
from datetime import datetime

# ── Path setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from src.data_fetch       import fetch_financials, fetch_batch
from src.preprocessor     import preprocess, load_processed
from models.beneish_mscore import calculate_mscore
from models.altman_zscore  import calculate_zscore
from models.ratio_analysis import run_red_flags
from src.report_generator  import generate_report

OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


# ══════════════════════════════════════════════════════════════════════════════
# Core pipeline for a single ticker
# ══════════════════════════════════════════════════════════════════════════════

def run_pipeline(ticker: str, use_cache: bool = False) -> dict:
    """
    Full RedFlagIQ pipeline for a single ticker.

    Steps:
    1. Fetch financial data (or load from cache)
    2. Preprocess and clean
    3. Beneish M-Score
    4. Altman Z-Score
    5. Custom red flags
    6. Generate PDF report
    7. Return structured results dict (used for CSV export)
    """
    ticker = ticker.upper().strip()
    print(f"\n{'▓'*60}")
    print(f"  RedFlagIQ  |  Analysing: {ticker}")
    print(f"{'▓'*60}")

    # ── Step 1: Fetch or load ──────────────────────────────────────────────────
    if use_cache:
        try:
            processed = load_processed(ticker)
            print(f"[RedFlagIQ] Using cached data for {ticker}")
        except FileNotFoundError:
            print(f"[RedFlagIQ] No cache found — fetching live data...")
            raw       = fetch_financials(ticker)
            processed = preprocess(raw)
    else:
        raw       = fetch_financials(ticker)
        processed = preprocess(raw)

    financials = processed["financials"]
    info       = processed["info"]

    # ── Step 2: Run models ─────────────────────────────────────────────────────
    mscore_result   = calculate_mscore(financials, info)
    zscore_result   = calculate_zscore(financials, info)
    redflags_result = run_red_flags(financials, info)

    # ── Step 3: Generate PDF ───────────────────────────────────────────────────
    pdf_path = generate_report(mscore_result, zscore_result, redflags_result, info)

    # ── Step 4: Build results row for CSV ─────────────────────────────────────
    # NOTE: Beneish M-Score was calibrated on 1990s manufacturing firms.
    # Modern large-cap tech companies structurally score > -1.78 due to
    # high receivables and leverage. We require corroboration across
    # models before rating HIGH.
    m_high  = mscore_result["risk"]            == "HIGH"
    z_high  = zscore_result["risk"]            == "HIGH"
    z_med   = "GREY" in zscore_result["zone"]
    f_count = redflags_result["triggered_count"]

    if z_high:
        overall_risk = "HIGH"
    elif m_high and (z_high or f_count >= 3):
        overall_risk = "HIGH"
    elif m_high or z_med or f_count >= 2:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    result_row = {
        "ticker":               ticker,
        "company_name":         info.get("company_name", ticker),
        "sector":               info.get("sector", "N/A"),
        "analysis_year":        mscore_result["curr_year"],
        "prior_year":           mscore_result["prev_year"],
        # M-Score
        "m_score":              mscore_result["m_score"],
        "m_score_verdict":      mscore_result["verdict"],
        "m_score_risk":         mscore_result["risk"],
        "m_flagged_ratios":     ", ".join(mscore_result["flagged_ratios"]),
        # Z-Score
        "z_score":              zscore_result["z_score"],
        "z_score_zone":         zscore_result["zone"],
        "z_score_risk":         zscore_result["risk"],
        # Custom flags
        "custom_flags_triggered": redflags_result["triggered_count"],
        "custom_flags_total":   redflags_result["total_flags"],
        "custom_flags_severity": redflags_result["severity"],
        # Individual custom flag results
        "flag_1_revenue_ocf":   "FLAG" if redflags_result["flags"][0]["triggered"] else "OK",
        "flag_2_ar_revenue":    "FLAG" if redflags_result["flags"][1]["triggered"] else "OK",
        "flag_3_gross_margin":  "FLAG" if redflags_result["flags"][2]["triggered"] else "OK",
        "flag_4_debt_equity":   "FLAG" if redflags_result["flags"][3]["triggered"] else "OK",
        "flag_5_ni_fcf":        "FLAG" if redflags_result["flags"][4]["triggered"] else "OK",
        # Overall
        "overall_risk":         overall_risk,
        "pdf_report":           pdf_path,
        "run_timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    print(f"\n[RedFlagIQ] ✅ {ticker} complete — Overall Risk: {overall_risk}")
    return result_row


# ══════════════════════════════════════════════════════════════════════════════
# Batch pipeline + CSV export (feeds Shreshti's PowerBI)
# ══════════════════════════════════════════════════════════════════════════════

def run_batch(tickers: list, use_cache: bool = False) -> pd.DataFrame:
    """
    Run the full pipeline for multiple tickers and export results CSV.
    CSV output feeds directly into Shreshti's PowerBI dashboard.
    """
    all_results = []
    failed      = []

    print(f"\n[RedFlagIQ] Starting batch analysis for {len(tickers)} tickers...\n")

    for i, ticker in enumerate(tickers, start=1):
        print(f"\n[{i}/{len(tickers)}] ─────────────────────────────────────────")
        try:
            result = run_pipeline(ticker, use_cache=use_cache)
            all_results.append(result)
        except Exception as e:
            print(f"[RedFlagIQ] ❌ {ticker} failed: {e}")
            failed.append(ticker)

    # ── Export CSV ─────────────────────────────────────────────────────────────
    if all_results:
        df = pd.DataFrame(all_results)
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        csv_path = os.path.join(OUTPUTS_DIR, "results.csv")
        df.to_csv(csv_path, index=False)
        print(f"\n[RedFlagIQ] ✅ Results CSV saved → outputs/results.csv")
        print(f"[RedFlagIQ]    {len(all_results)} companies analysed")
        if failed:
            print(f"[RedFlagIQ]    ❌ Failed: {failed}")
        _print_summary(df)
        return df
    else:
        print("[RedFlagIQ] No results to save.")
        return pd.DataFrame()


def _print_summary(df: pd.DataFrame):
    """Print a quick summary table to terminal."""
    print(f"\n{'═'*70}")
    print(f"  REDFLAGIQ BATCH SUMMARY")
    print(f"{'═'*70}")
    print(f"  {'TICKER':<8} {'COMPANY':<25} {'M-SCORE':>8} "
          f"{'Z-SCORE':>8} {'FLAGS':>6} {'RISK':<10}")
    print(f"  {'─'*64}")
    for _, row in df.iterrows():
        risk_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
            row["overall_risk"], "⚪"
        )
        print(f"  {row['ticker']:<8} {str(row['company_name'])[:24]:<25} "
              f"{row['m_score']:>8.2f} {row['z_score']:>8.2f} "
              f"{row['custom_flags_triggered']:>6} "
              f"{risk_icon} {row['overall_risk']}")
    print(f"{'═'*70}\n")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="RedFlagIQ — Financial Statement Red Flag Detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ticker AAPL
  python main.py --ticker MSFT --no-fetch
  python main.py --batch tickers.csv
        """
    )
    parser.add_argument("--ticker",   type=str, help="Single stock ticker (e.g. AAPL)")
    parser.add_argument("--batch",    type=str, help="Path to CSV file with tickers (one per row)")
    parser.add_argument("--no-fetch", action="store_true",
                        help="Use cached data instead of fetching live")

    args = parser.parse_args()

    if not args.ticker and not args.batch:
        parser.print_help()
        print("\n[RedFlagIQ] Error: provide --ticker or --batch")
        sys.exit(1)

    if args.ticker:
        result = run_pipeline(args.ticker, use_cache=args.no_fetch)
        # Single ticker — still export CSV
        df = pd.DataFrame([result])
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        df.to_csv(os.path.join(OUTPUTS_DIR, "results.csv"), index=False)
        print(f"[RedFlagIQ] ✅ Results saved → outputs/results.csv")

    elif args.batch:
        if not os.path.exists(args.batch):
            print(f"[RedFlagIQ] Error: file not found — {args.batch}")
            sys.exit(1)
        tickers_df = pd.read_csv(args.batch, header=None)
        tickers    = tickers_df.iloc[:, 0].str.strip().str.upper().tolist()
        run_batch(tickers, use_cache=args.no_fetch)


if __name__ == "__main__":
    main()