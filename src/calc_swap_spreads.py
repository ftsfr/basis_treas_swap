"""
Compatibility module mapping old API to calc_treasury_swap_basis.

This stub provides the old function names expected by tests.
"""

import pandas as pd

from settings import config
from pull_bbg_treas_swap import load_syields, load_tyields

DATA_DIR = config("DATA_DIR")


def calc_swap_spreads(treasury_df, swap_df):
    """Combines the treasury and swap data and calculates the spreads.

    :param treasury_df: DataFrame containing the treasury yield data
    :param swap_df: DataFrame containing the swap yield data
    :return: The merged data frame containing the clean and calculated data
    """
    # Flatten MultiIndex columns if present
    if isinstance(treasury_df.columns, pd.MultiIndex):
        treasury_df = treasury_df.copy()
        treasury_df.columns = treasury_df.columns.get_level_values(0)
    if isinstance(swap_df.columns, pd.MultiIndex):
        swap_df = swap_df.copy()
        swap_df.columns = swap_df.columns.get_level_values(0)

    s_years = [1, 2, 3, 5, 10, 20, 30]
    merged_df = pd.merge(
        swap_df, treasury_df, left_index=True, right_index=True, how="inner"
    )
    for i in s_years:
        merged_df[f"Arb_Swap_{i}"] = 100 * (
            -merged_df[f"GT{i} Govt"] + merged_df[f"USSO{i} CMPN Curncy"]
        )
        merged_df[f"tswap_{i}_rf"] = merged_df[f"USSO{i} CMPN Curncy"] * 100

    merged_df["Year"] = pd.to_datetime(merged_df.index).year
    merged_df = merged_df[merged_df["Year"] >= 2000]

    arb_list = [f"Arb_Swap_{x}" for x in s_years]
    tswap_list = [f"tswap_{x}_rf" for x in s_years]
    merged_df = merged_df[arb_list + tswap_list]
    merged_df = merged_df.dropna(how="all")

    return merged_df
