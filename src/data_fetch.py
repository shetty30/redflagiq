import yfinance as yf
import pandas as pd
import os


def fetch_financial_statements(ticker: str):
    company = yf.Ticker(ticker)

    os.makedirs("data/raw", exist_ok=True)

    income_statement = company.financials
    balance_sheet = company.balance_sheet
    cash_flow = company.cashflow

    income_statement.to_csv(f"data/raw/{ticker}_income_statement.csv")
    balance_sheet.to_csv(f"data/raw/{ticker}_balance_sheet.csv")
    cash_flow.to_csv(f"data/raw/{ticker}_cash_flow.csv")

    print(f"Raw financial statements saved for {ticker}")


if __name__ == "__main__":
    ticker = input("Enter ticker symbol: ").upper()
    fetch_financial_statements(ticker)