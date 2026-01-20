"""
Calculate Treasury-Swap basis (arbitrage spreads).

The Treasury-Swap basis is calculated as:
    Basis = Treasury Yield - Swap Rate

This spread measures the relative value between Treasury securities and
interest rate swaps at various maturities. Positive values indicate
Treasuries yield more than swaps, negative values indicate swaps yield more.

Data Sources:
    - Bloomberg Treasury constant maturity yields
    - Bloomberg USD swap rates
"""

import sys
from pathlib import Path

sys.path.insert(0, "./src")

import pandas as pd
import numpy as np

import chartbook
import pull_bbg_treasury_swap

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

# Mapping from Bloomberg tickers to tenor names
TREASURY_MAPPING = {
    "USGG1YR": "1Y",
    "USGG2YR": "2Y",
    "USGG3YR": "3Y",
    "USGG5YR": "5Y",
    "USGG10YR": "10Y",
    "USGG20YR": "20Y",
    "USGG30YR": "30Y",
}

SWAP_MAPPING = {
    "USSW1": "1Y",
    "USSW2": "2Y",
    "USSW3": "3Y",
    "USSW5": "5Y",
    "USSW10": "10Y",
    "USSW20": "20Y",
    "USSW30": "30Y",
}

# Output column names (in basis points)
OUTPUT_COLUMNS = {
    "1Y": "Arb_Swap_1",
    "2Y": "Arb_Swap_2",
    "3Y": "Arb_Swap_3",
    "5Y": "Arb_Swap_5",
    "10Y": "Arb_Swap_10",
    "20Y": "Arb_Swap_20",
    "30Y": "Arb_Swap_30",
}


def prepare_data(treasury_df, swap_df):
    """
    Prepare Treasury and swap data for basis calculations.

    Parameters
    ----------
    treasury_df : pd.DataFrame
        Treasury yields from Bloomberg
    swap_df : pd.DataFrame
        Swap rates from Bloomberg

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with standardized column names
    """
    # Set Date as index
    treasury_df = (
        treasury_df.set_index("index") if "index" in treasury_df.columns else treasury_df
    )
    swap_df = (
        swap_df.set_index("index") if "index" in swap_df.columns else swap_df
    )

    # Clean up column names - extract ticker from Bloomberg format
    def clean_columns(df, mapping, suffix):
        new_cols = {}
        for col in df.columns:
            if "_PX_LAST" in col:
                ticker = col.split()[0]
                if ticker in mapping:
                    new_cols[col] = f"{mapping[ticker]}_{suffix}"
        df = df.rename(columns=new_cols)
        return df

    treasury_df = clean_columns(treasury_df, TREASURY_MAPPING, "Treasury")
    swap_df = clean_columns(swap_df, SWAP_MAPPING, "Swap")

    # Merge dataframes
    df_merged = treasury_df.merge(
        swap_df, left_index=True, right_index=True, how="inner"
    )

    return df_merged


def compute_treasury_swap_basis(df_merged):
    """
    Compute Treasury-Swap basis in basis points.

    The basis is calculated as: (Treasury Yield - Swap Rate) * 100
    to convert from percentage to basis points.

    Parameters
    ----------
    df_merged : pd.DataFrame
        DataFrame with Treasury yields and swap rates

    Returns
    -------
    pd.DataFrame
        DataFrame with basis spreads for each tenor
    """
    tenors = ["1Y", "2Y", "3Y", "5Y", "10Y", "20Y", "30Y"]

    for tenor in tenors:
        treas_col = f"{tenor}_Treasury"
        swap_col = f"{tenor}_Swap"
        output_col = OUTPUT_COLUMNS[tenor]

        if treas_col in df_merged.columns and swap_col in df_merged.columns:
            # Basis = Treasury - Swap, converted to basis points
            df_merged[output_col] = (df_merged[treas_col] - df_merged[swap_col]) * 100

    return df_merged


def calculate_treasury_swap_basis(end_date=None, data_dir=DATA_DIR):
    """
    Calculate Treasury-Swap basis spreads.

    Parameters
    ----------
    end_date : str, optional
        End date for the data
    data_dir : Path
        Directory containing the data files

    Returns
    -------
    pd.DataFrame
        DataFrame with basis spreads in basis points
    """
    data_dir = Path(data_dir)

    print(">> Calculating Treasury-Swap basis...")

    # Load data
    treasury_df = pull_bbg_treasury_swap.load_treasury_yields(data_dir=data_dir)
    swap_df = pull_bbg_treasury_swap.load_swap_rates(data_dir=data_dir)

    # Prepare data
    df_merged = prepare_data(treasury_df, swap_df)

    # Filter by end date if specified
    if end_date:
        date = pd.Timestamp(end_date).date()
        df_merged = df_merged.loc[:date]

    # Compute basis
    df_merged = compute_treasury_swap_basis(df_merged)

    # Extract just the basis columns
    basis_cols = [col for col in OUTPUT_COLUMNS.values() if col in df_merged.columns]
    basis_df = df_merged[basis_cols].copy()

    # Forward fill missing values
    basis_df = basis_df.ffill()

    print(f">> Records: {len(basis_df):,}")
    return basis_df


def load_treasury_swap_basis(data_dir=DATA_DIR):
    """Load calculated Treasury-Swap basis from parquet file."""
    path = data_dir / "treasury_swap_basis.parquet"
    return pd.read_parquet(path)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    basis_df = calculate_treasury_swap_basis(data_dir=DATA_DIR)
    basis_df.to_parquet(DATA_DIR / "treasury_swap_basis.parquet")
    print(">> Saved treasury_swap_basis.parquet")


if __name__ == "__main__":
    main()
