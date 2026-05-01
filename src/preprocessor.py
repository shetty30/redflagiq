import pandas as pd
import os


def clean_statement(file_path: str, statement_type: str):
    df = pd.read_csv(file_path)

    df = df.rename(columns={df.columns[0]: "line_item"})

    df = df.melt(
        id_vars=["line_item"],
        var_name="year",
        value_name="value"
    )

    df["statement_type"] = statement_type
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


def preprocess_company(ticker: str):
    os.makedirs("data/processed", exist_ok=True)

    income = clean_statement(
        f"data/raw/{ticker}_income_statement.csv",
        "income_statement"
    )

    balance = clean_statement(
        f"data/raw/{ticker}_balance_sheet.csv",
        "balance_sheet"
    )

    cashflow = clean_statement(
        f"data/raw/{ticker}_cash_flow.csv",
        "cash_flow"
    )

    final_df = pd.concat([income, balance, cashflow], ignore_index=True)

    output_path = f"data/processed/{ticker}_financials_cleaned.csv"
    final_df.to_csv(output_path, index=False)

    print(f"Cleaned financial data saved: {output_path}")


if __name__ == "__main__":
    ticker = input("Enter ticker symbol: ").upper()
    preprocess_company(ticker)