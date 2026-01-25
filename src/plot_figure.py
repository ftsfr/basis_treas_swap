"""
Plot Treasury-Swap Figures.

Utilities to create and save the replicated, updated, and supplementary plots using Plotly.
"""

from pathlib import Path
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from settings import config
from supplementary import supplementary_main

# Defaults for plotting windows
DEFAULT_START_DATE = pd.Timestamp("1998-01-01").date()
DEFAULT_END_DATE = None  # None means use full available range

# Specific cut-off used for the replicated figure
REPLICATION_END_DATE = pd.Timestamp("2025-08-01").date()

DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")


def plot_figure(
    arb_df: pd.DataFrame,
    save_path: str | Path,
    start_date: Optional[date | pd.Timestamp] = DEFAULT_START_DATE,
    end_date: Optional[date | pd.Timestamp] = DEFAULT_END_DATE,
) -> go.Figure:
    """
    Create and save the primary Treasury-Swap arbitrage plot using Plotly.

    Parameters
    - arb_df: DataFrame with arbitrage spreads by tenor
    - save_path: File path for the saved plot (HTML)
    - start_date: Start date for the plot window
    - end_date: End date for the plot window

    Returns
    - Plotly Figure object
    """
    start_dt = pd.to_datetime(start_date).date() if start_date is not None else None
    end_dt = pd.to_datetime(end_date).date() if end_date is not None else None

    fig = go.Figure()

    for year in [1, 2, 3, 5, 10, 20, 30]:
        col_name = f"Arb_Swap_{year}"
        if col_name not in arb_df.columns:
            continue
        series = arb_df[col_name]
        if start_dt is not None and end_dt is not None:
            series = series.loc[start_dt:end_dt].dropna()
        elif start_dt is not None:
            series = series.loc[start_dt:].dropna()
        else:
            series = series.dropna()

        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name=f"{year}Y",
            )
        )

    fig.update_layout(
        title="Treasury-Swap Arbitrage Spreads",
        xaxis_title="Date",
        yaxis_title="Arbitrage Spread (bps)",
    )

    fig.write_html(save_path)
    return fig


def plot_supplementary(
    replication_df: pd.DataFrame,
    save_path: str | Path,
    start_date: Optional[date | pd.Timestamp] = DEFAULT_START_DATE,
    end_date: Optional[date | pd.Timestamp] = DEFAULT_END_DATE,
) -> None:
    """
    Create and save supplementary plots of log Treasury and Swap rates using Plotly.

    Parameters
    - replication_df: DataFrame with cleaned Treasury and Swap series
    - save_path: Base file path; one file per tenor will be saved
    - start_date: Start date for the plot window
    - end_date: End date for the plot window
    """
    start_dt = pd.to_datetime(start_date).date() if start_date is not None else None
    end_dt = pd.to_datetime(end_date).date() if end_date is not None else None

    base_path = Path(save_path)

    for year in [1, 2, 3, 5, 10, 20, 30]:
        trea_col = f"GT{year} Govt"
        swap_col = f"USSO{year} CMPN Curncy"

        if trea_col not in replication_df.columns or swap_col not in replication_df.columns:
            continue

        trea = replication_df[trea_col]
        swap = replication_df[swap_col]

        if start_dt is not None and end_dt is not None:
            trea = trea.loc[start_dt:end_dt]
            swap = swap.loc[start_dt:end_dt]
        elif start_dt is not None:
            trea = trea.loc[start_dt:]
            swap = swap.loc[start_dt:]

        # Drop non-positive values before taking logs
        trea_plot = trea.dropna()
        trea_plot = trea_plot[trea_plot > 0]
        swap_plot = swap.dropna()
        swap_plot = swap_plot[swap_plot > 0]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=trea_plot.index,
                y=np.log(100 * trea_plot),
                mode="lines",
                name=f"{year}Y Treasury",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=swap_plot.index,
                y=np.log(100 * swap_plot),
                mode="lines",
                name=f"{year}Y Swap",
            )
        )

        fig.update_layout(
            title="Treasury and Swap Rates",
            xaxis_title="Date",
            yaxis_title="Log Rates",
        )

        year_path = base_path.with_name(f"{base_path.stem}{year}{base_path.suffix}")
        fig.write_html(year_path)


def plot_main(data_dir: Path = DATA_DIR) -> None:
    """
    Create and save the replicated, updated, and supplementary plots.

    - Replicated plot uses REPLICATION_END_DATE.
    - Updated plot uses full available range (no end date cap).
    - Supplementary plots use full available range.
    """
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    file = data_dir / "swap_spreads.parquet"
    # Load precomputed arbitrage spreads created in format step
    arb_df = pd.read_parquet(file)

    rep_df = supplementary_main(data_dir=data_dir)

    plot_figure(
        arb_df,
        out_dir / "replicated_swap_spread_arb_figure.html",
        start_date=DEFAULT_START_DATE,
        end_date=REPLICATION_END_DATE,
    )

    plot_figure(
        arb_df,
        out_dir / "updated_swap_spread_arb_figure.html",
        start_date=DEFAULT_START_DATE,
        end_date=None,  # show full available range
    )

    plot_supplementary(
        rep_df,
        out_dir / "replication_figure.html",
        start_date=DEFAULT_START_DATE,
        end_date=None,
    )


if __name__ == "__main__":
    plot_main(data_dir=DATA_DIR)
