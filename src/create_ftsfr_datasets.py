"""
Create FTSFR standardized datasets for Treasury-Swap basis.

Outputs:
- ftsfr_treasury_swap_basis.parquet: Treasury-Swap arbitrage spreads in basis points
"""

import sys
from pathlib import Path

sys.path.insert(0, "./src")

import pandas as pd

import chartbook
import calc_treasury_swap_basis

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(">> Creating ftsfr_treasury_swap_basis...")

    output_path = DATA_DIR / "ftsfr_treasury_swap_basis.parquet"

    # Check if a valid ftsfr file already exists
    if output_path.exists():
        try:
            df_existing = pd.read_parquet(output_path)
            if (
                set(df_existing.columns) == {"unique_id", "ds", "y"}
                and len(df_existing) > 0
            ):
                print(f"   Using existing: {output_path.name}")
                print(f"   Records: {len(df_existing):,}")
                print(f"   Series: {df_existing['unique_id'].nunique()}")
                return
        except Exception:
            pass  # File exists but can't be read, regenerate it

    # Calculate basis spreads
    df_all = calc_treasury_swap_basis.calculate_treasury_swap_basis(data_dir=DATA_DIR)

    # Check if we got valid data
    if df_all.empty or len(df_all.columns) == 0:
        print("   Warning: No data from calculation, skipping ftsfr generation")
        return

    # Convert from wide to long format
    df_stacked = df_all.stack(future_stack=True).reset_index()
    df_stacked.columns = ["ds", "unique_id", "y"]

    # Reorder columns to FTSFR standard: unique_id, ds, y
    df_stacked = df_stacked[["unique_id", "ds", "y"]]
    df_stacked["ds"] = pd.to_datetime(df_stacked["ds"])

    # Clean up
    df_stacked = df_stacked.dropna()
    df_stacked = df_stacked.sort_values(by=["unique_id", "ds"]).reset_index(drop=True)

    # Save
    df_stacked.to_parquet(output_path, index=False)
    print(f"   Saved: {output_path.name}")
    print(f"   Records: {len(df_stacked):,}")
    print(f"   Series: {df_stacked['unique_id'].nunique()}")


if __name__ == "__main__":
    main()
