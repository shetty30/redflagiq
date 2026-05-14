"""
data_fetch.py
-------------
Fetches 5 years of financial statements for a given ticker using yfinance.
Saves raw data to data/raw/<TICKER>/

Usage:
    from src.data_fetch import fetch_financials
    data = fetch_financials("AAPL")
"""

import os
import json
import time
import yfinance as yf
import pandas as pd
from datetime import datetime


RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


def fetch_financials(ticker: str, retries: int = 3, delay: int = 5) -> dict:
    """
    Fetch Income Statement, Balance Sheet, and Cash Flow for a ticker.
    Returns a dict with keys: 'income', 'balance', 'cashflow', 'info'
    Saves raw CSVs to data/raw/<TICKER>/
    """
    ticker = ticker.upper().strip()
    print(f"\n[RedFlagIQ] Fetching data for: {ticker}")

    for attempt in range(1, retries + 1):
        try:
            stock = yf.Ticker(ticker)

            income    = stock.financials          # Income Statement (annual)
            balance   = stock.balance_sheet       # Balance Sheet (annual)
            cashflow  = stock.cashflow            # Cash Flow Statement (annual)
            info      = stock.info                # Company metadata

            if income.empty or balance.empty or cashflow.empty:
                raise ValueError(f"No financial data returned for {ticker}. "
                                 f"Check if ticker is valid.")

            # ── Save raw data ───────────────────────────────────────────────
            save_dir = os.path.join(RAW_DIR, ticker)
            os.makedirs(save_dir, exist_ok=True)

            income.to_csv(os.path.join(save_dir, "income_statement.csv"))
            balance.to_csv(os.path.join(save_dir, "balance_sheet.csv"))
            cashflow.to_csv(os.path.join(save_dir, "cash_flow.csv"))

            # Save key info as JSON
            info_subset = {
                "ticker":        ticker,
                "company_name":  info.get("longName", ticker),
                "sector":        info.get("sector", "N/A"),
                "industry":      info.get("industry", "N/A"),
                "market_cap":    info.get("marketCap", None),
                "currency":      info.get("currency", "USD"),
                "fetched_at":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            with open(os.path.join(save_dir, "info.json"), "w") as f:
                json.dump(info_subset, f, indent=2)

            print(f"[RedFlagIQ] ✅ Raw data saved → data/raw/{ticker}/")

            return {
                "income":   income,
                "balance":  balance,
                "cashflow": cashflow,
                "info":     info_subset,
            }

        except Exception as e:
            print(f"[RedFlagIQ] ⚠️  Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                print(f"[RedFlagIQ] Retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise RuntimeError(
                    f"Failed to fetch data for {ticker} after {retries} attempts.\n"
                    f"Error: {e}"
                )


def fetch_batch(tickers: list, delay_between: int = 2) -> dict:
    """
    Fetch financials for multiple tickers.
    Returns dict of {ticker: data} — skips failed tickers with a warning.

    Args:
        tickers: list of ticker strings e.g. ["AAPL", "MSFT", "TSLA"]
        delay_between: seconds to wait between API calls (avoid rate limiting)
    """
    results = {}
    failed  = []

    print(f"\n[RedFlagIQ] Batch fetch starting for {len(tickers)} tickers...")

    for i, ticker in enumerate(tickers, start=1):
        print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
        try:
            results[ticker] = fetch_financials(ticker)
            if i < len(tickers):
                time.sleep(delay_between)   # Rate limit safety
        except Exception as e:
            print(f"[RedFlagIQ] ❌ Skipping {ticker}: {e}")
            failed.append(ticker)

    print(f"\n[RedFlagIQ] Batch complete: {len(results)} succeeded, "
          f"{len(failed)} failed.")
    if failed:
        print(f"[RedFlagIQ] Failed tickers: {failed}")

    return results
