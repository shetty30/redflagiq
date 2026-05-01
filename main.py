from src.data_fetch import fetch_financial_statements
from src.preprocessor import preprocess_company


def main():
    ticker = input("Enter stock ticker: ").upper()

    print("Fetching financial statements...")
    fetch_financial_statements(ticker)

    print("Cleaning financial data...")
    preprocess_company(ticker)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()