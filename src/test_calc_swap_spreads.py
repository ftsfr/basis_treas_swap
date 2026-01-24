"""
Tests functions in calc_swap_spreads responsible for calculation and plots.
"""

import pandas as pd

from calc_swap_spreads import calc_swap_spreads
from pull_bbg_treas_swap import (
    pull_raw_syields,
    clean_raw_syields,
    pull_raw_tyields,
    clean_raw_tyields,
)


def test_calc_swap_spreads():
    """Tests calc_swap_spreads to ensure that the output dataframe
    has the correct data in it.
    """

    raw_syields = pull_raw_syields()
    swap_df = clean_raw_syields(raw_syields)

    raw_tyields = pull_raw_tyields()
    treasury_df = clean_raw_tyields(raw_tyields)

    total_list = []
    output = calc_swap_spreads(treasury_df, swap_df)
    years = [1, 2, 3, 5, 10, 20, 30]
    for year in years:
        total_list.append(f"Arb_Swap_{year}")
    for year in years:
        total_list.append(f"tswap_{year}_rf")
    # Handle both MultiIndex columns (from Bloomberg) and single-level columns
    if isinstance(output.columns, pd.MultiIndex):
        actual_cols = [a for a, _ in output.columns]
    else:
        actual_cols = list(output.columns)
    assert actual_cols == total_list
