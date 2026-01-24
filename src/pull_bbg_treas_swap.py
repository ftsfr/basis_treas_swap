"""
Compatibility module mapping old API to pull_bbg_treasury_swap.

This stub provides the old function names expected by tests.
"""

from pathlib import Path

import pandas as pd

import chartbook
import pull_bbg_treasury_swap

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"


def pull_raw_tyields(start_date="2000-01-01", end_date=None):
    """Load raw Treasury yields from local data file."""
    df = pd.read_parquet(DATA_DIR / "raw_tyields.parquet")
    return df


def pull_raw_syields(start_date="2000-01-01", end_date=None):
    """Load raw Swap yields from local data file."""
    df = pd.read_parquet(DATA_DIR / "raw_syields.parquet")
    return df


def clean_raw_tyields(raw_df):
    """Clean Treasury yields by coercing numeric dtypes."""
    return raw_df.apply(pd.to_numeric, errors="coerce")


def clean_raw_syields(raw_df):
    """Clean Swap yields by coercing numeric dtypes."""
    return raw_df.apply(pd.to_numeric, errors="coerce")


def load_tyields(data_dir=DATA_DIR):
    """Load cleaned Treasury yields from disk."""
    return pd.read_parquet(data_dir / "tyields.parquet")


def load_syields(data_dir=DATA_DIR):
    """Load cleaned Swap yields from disk."""
    return pd.read_parquet(data_dir / "syields.parquet")
