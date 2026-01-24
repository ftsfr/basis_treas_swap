"""
Compatibility module for supplementary functions.

This stub provides the old function names expected by tests.
"""

import os
from pathlib import Path

import pandas as pd

from settings import config
from pull_bbg_treas_swap import (
    pull_raw_syields,
    pull_raw_tyields,
    clean_raw_syields,
    clean_raw_tyields,
    load_syields,
    load_tyields,
)
from calc_swap_spreads import calc_swap_spreads

DATA_DIR = config("DATA_DIR")
output_dir = config("OUTPUT_DIR")


def replication_df(treasury_df, swap_df):
    """Creates a merged DataFrame of the treasury and swap yields.

    :param treasury_df: DataFrame containing the treasury yield data
    :param swap_df: DataFrame containing the swap yield data
    :return: The merged data frame
    """
    years = [1, 2, 3, 5, 10, 20, 30]
    t_list = [f"GT{year} Govt" for year in years]
    s_list = [f"USSO{year} CMPN Curncy" for year in years]
    return pd.merge(
        treasury_df[t_list].loc[pd.Timestamp("2010").date() :],
        swap_df[s_list].loc[pd.Timestamp("2010").date() :],
        left_index=True,
        right_index=True,
        how="inner",
    )


def sup_table(calc_df, file_name="table.txt"):
    """Creates the table of means for spreads. Also saves the LaTeX table to a text file.

    :param calc_df: DataFrame containing the swap yield data
    :param file_name: name of the text file to save LaTeX table to
    :return: The data frame containing means
    """
    years = [1, 2, 3, 5, 10, 20, 30]
    df = calc_df[[f"Arb_Swap_{year}" for year in years]]
    for year in years:
        df = df.rename(columns={f"Arb_Swap_{year}": f"Arb Swap {year}"})
    means = df.mean()
    means.rename()
    means_str = pd.DataFrame(means, columns=["Mean(bps)"]).to_latex()
    file = DATA_DIR / file_name if not os.path.isabs(file_name) else Path(file_name)
    with open(file, "w") as table:
        table.write(means_str)
    return means


def supplementary_main(data_dir=DATA_DIR):
    """Load inputs from disk, save the table, and return replication DataFrame."""
    swap_df = load_syields(data_dir=data_dir)
    treasury_df = load_tyields(data_dir=data_dir)
    sup_table(calc_swap_spreads(treasury_df, swap_df))
    return replication_df(treasury_df, swap_df)
