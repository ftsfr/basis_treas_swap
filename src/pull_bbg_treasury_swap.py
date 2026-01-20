"""
Fetches Treasury yields and swap rates from Bloomberg for basis calculations.

This module pulls Treasury constant maturity yields and USD swap rates
to calculate Treasury-Swap arbitrage spreads.
"""

import sys
from pathlib import Path

sys.path.insert(0, "./src")

import pandas as pd

import chartbook

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
END_DATE = pd.Timestamp.today().strftime("%Y-%m-%d")


def pull_treasury_swap_data(start_date="1990-01-01", end_date=END_DATE):
    """
    Fetch historical Treasury yields and swap rates from Bloomberg using xbbg.

    Parameters
    ----------
    start_date : str
        Start date in 'YYYY-MM-DD' format
    end_date : str
        End date in 'YYYY-MM-DD' format

    Returns
    -------
    dict
        Dictionary with two DataFrames:
        - 'treasury_yields': Treasury constant maturity yields
        - 'swap_rates': USD swap rates
    """
    # import here to enhance compatibility with devices that don't support xbbg
    from xbbg import blp

    # Treasury yield tickers (constant maturity)
    treasury_tickers = [
        "USGG1YR Index",   # 1-Year Treasury
        "USGG2YR Index",   # 2-Year Treasury
        "USGG3YR Index",   # 3-Year Treasury
        "USGG5YR Index",   # 5-Year Treasury
        "USGG10YR Index",  # 10-Year Treasury
        "USGG20YR Index",  # 20-Year Treasury
        "USGG30YR Index",  # 30-Year Treasury
    ]

    # USD swap rate tickers
    swap_tickers = [
        "USSW1 Curncy",    # 1-Year Swap
        "USSW2 Curncy",    # 2-Year Swap
        "USSW3 Curncy",    # 3-Year Swap
        "USSW5 Curncy",    # 5-Year Swap
        "USSW10 Curncy",   # 10-Year Swap
        "USSW20 Curncy",   # 20-Year Swap
        "USSW30 Curncy",   # 30-Year Swap
    ]

    fields = ["PX_LAST"]

    # Helper to flatten multi-index columns from xbbg
    def process_bloomberg_df(df):
        if not df.empty and isinstance(df.columns, pd.MultiIndex):
            df.columns = [f"{t[0]}_{t[1]}" for t in df.columns]
            df.reset_index(inplace=True)
        return df

    print(">> Pulling Treasury-Swap data from Bloomberg...")

    # Pull Treasury yields
    print("   Pulling Treasury yields...")
    treasury_df = process_bloomberg_df(
        blp.bdh(
            tickers=treasury_tickers,
            flds=fields,
            start_date=start_date,
            end_date=end_date,
        )
    )

    # Pull swap rates
    print("   Pulling swap rates...")
    swap_df = process_bloomberg_df(
        blp.bdh(
            tickers=swap_tickers,
            flds=fields,
            start_date=start_date,
            end_date=end_date,
        )
    )

    return {
        "treasury_yields": treasury_df,
        "swap_rates": swap_df,
    }


def load_treasury_yields(data_dir=DATA_DIR):
    """Load Treasury yields from parquet file."""
    path = data_dir / "treasury_yields.parquet"
    return pd.read_parquet(path)


def load_swap_rates(data_dir=DATA_DIR):
    """Load swap rates from parquet file."""
    path = data_dir / "swap_rates.parquet"
    return pd.read_parquet(path)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Pull data from source
    data = pull_treasury_swap_data()

    # Save each dataset to parquet
    data["treasury_yields"].to_parquet(DATA_DIR / "treasury_yields.parquet")
    print(f">> Saved treasury_yields.parquet")

    data["swap_rates"].to_parquet(DATA_DIR / "swap_rates.parquet")
    print(f">> Saved swap_rates.parquet")


if __name__ == "__main__":
    main()
