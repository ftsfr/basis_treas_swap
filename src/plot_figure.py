"""
Plot Treasury-Swap Figures.

Utilities to create and save the replicated, updated, and supplementary plots.
"""

import os
from pathlib import Path
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from settings import config
from supplementary import supplementary_main

# Defaults for plotting windows
DEFAULT_START_DATE = pd.Timestamp("1998-01-01").date()
DEFAULT_END_DATE = None  # None means use full available range

# Specific cut-off used for the replicated figure
REPLICATION_END_DATE = pd.Timestamp("2025-08-01").date()

DATA_DIR = config("DATA_DIR")
output_dir = config("OUTPUT_DIR")


def plot_figure(
    arb_df,
    save_path,
    start_date=DEFAULT_START_DATE,
    end_date=DEFAULT_END_DATE,
):
    """
    Create and save the primary Treasury-Swap arbitrage plot.

    Parameters
    - arb_df: DataFrame with arbitrage spreads by tenor
    - save_path: File path for the saved plot image
    - start_date: Start date for the plot window
    - end_date: End date for the plot window
    """
    start_dt = pd.to_datetime(start_date).date() if start_date is not None else None
    end_dt = pd.to_datetime(end_date).date() if end_date is not None else None

    for year in [1, 20, 2, 30, 3, 5, 10]:
        label = f"{year}Y"
        series = arb_df[f"Arb_Swap_{year}"]
        if start_dt is not None and end_dt is not None:
            plt.plot(series.loc[start_dt:end_dt].dropna(), label=label)
        elif start_dt is not None:
            plt.plot(series.loc[start_dt:].dropna(), label=label)
        else:
            plt.plot(series.dropna(), label=label)

    plt.title("Treasury-Swap")
    plt.xlabel("Dates")
    plt.ylabel("Arbitrage Spread (bps)")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=5)
    plt.grid(axis="y")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()


def plot_supplementary(
    replication_df,
    save_path,
    start_date=DEFAULT_START_DATE,
    end_date=DEFAULT_END_DATE,
):
    """
    Create and save supplementary plots of log Treasury and Swap rates.

    Parameters
    - replication_df: DataFrame with cleaned Treasury and Swap series
    - save_path: Base file path; one file per tenor will be saved
    - start_date: Start date for the plot window
    - end_date: End date for the plot window
    """
    start_dt = pd.to_datetime(start_date).date() if start_date is not None else None
    end_dt = pd.to_datetime(end_date).date() if end_date is not None else None

    base_path = Path(save_path)

    for year in [1, 20, 2, 30, 3, 5, 10]:
        trea = replication_df[f"GT{year} Govt"]
        swap = replication_df[f"USSO{year} CMPN Curncy"]

        if start_dt is not None and end_dt is not None:
            trea = trea.loc[start_dt:end_dt]
            swap = swap.loc[start_dt:end_dt]
        elif start_dt is not None:
            trea = trea.loc[start_dt:]
            swap = swap.loc[start_dt:]

        # Drop non-positive values before taking logs to avoid RuntimeWarning
        trea_plot = trea.dropna()
        trea_plot = trea_plot[trea_plot > 0]
        swap_plot = swap.dropna()
        swap_plot = swap_plot[swap_plot > 0]

        plt.plot(np.log(100 * trea_plot), label=f"{year}Y Treasury", linewidth=1)
        plt.plot(np.log(100 * swap_plot), label=f"{year}Y Swap", linewidth=1)

        plt.title("Treasury and Swap Rates")
        plt.xlabel("Dates")
        plt.ylabel("Log Rates")
        plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=5)
        plt.grid(axis="y")

        year_path = base_path.with_name(f"{base_path.stem}{year}{base_path.suffix}")
        plt.savefig(year_path, bbox_inches="tight")
        plt.close()


def plot_main(data_dir=DATA_DIR):
    """
    Create and save the replicated, updated, and supplementary plots.

    - Replicated plot uses REPLICATION_END_DATE.
    - Updated plot uses full available range (no end date cap).
    - Supplementary plots use full available range.
    """
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    file = data_dir / "swap_spreads.parquet"
    # Load precomputed arbitrage spreads created in format step
    arb_df = pd.read_parquet(file)

    rep_df = supplementary_main(data_dir=data_dir)

    plot_figure(
        arb_df,
        out_dir / "replicated_swap_spread_arb_figure.png",
        start_date=DEFAULT_START_DATE,
        end_date=REPLICATION_END_DATE,
    )

    plot_figure(
        arb_df,
        out_dir / "updated_swap_spread_arb_figure.png",
        start_date=DEFAULT_START_DATE,
        end_date=None,  # show full available range
    )

    plot_supplementary(
        rep_df,
        out_dir / "replication_figure.png",
        start_date=DEFAULT_START_DATE,
        end_date=None,
    )


if __name__ == "__main__":
    plot_main(data_dir=DATA_DIR)
