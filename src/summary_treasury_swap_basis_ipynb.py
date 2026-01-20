# %%
"""
# Treasury-Swap Basis Summary

Treasury-Swap arbitrage spreads measuring the difference between Treasury yields and swap rates.
"""

# %%
import sys
sys.path.insert(0, "./src")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import chartbook

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

# %%
"""
## Methodology

The Treasury-Swap basis is calculated as:

$$
\\text{Basis} = (\\text{Treasury Yield} - \\text{Swap Rate}) \\times 100
$$

Results are expressed in basis points.

### Interpretation

- **Basis > 0**: Treasuries yield more than swaps (Treasury-rich, swap-cheap)
- **Basis < 0**: Swaps yield more than Treasuries (Treasury-cheap, swap-rich)
- **Basis = 0**: No arbitrage opportunity

### Data Sources

- Bloomberg Treasury constant maturity yields (USGG series)
- Bloomberg USD swap rates (USSW series)
"""

# %%
"""
## Data Overview
"""

# %%
df = pd.read_parquet(DATA_DIR / "ftsfr_treasury_swap_basis.parquet")
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nDate range: {df['ds'].min()} to {df['ds'].max()}")
print(f"Number of series: {df['unique_id'].nunique()}")

# %%
print("\nSeries:")
for series in sorted(df['unique_id'].unique()):
    print(f"  {series}")

# %%
"""
### Summary Statistics
"""

# %%
basis_wide = df.pivot(index='ds', columns='unique_id', values='y')
basis_stats = basis_wide.describe().T
basis_stats['skewness'] = basis_wide.skew()
basis_stats['kurtosis'] = basis_wide.kurtosis()
print(basis_stats[['mean', 'std', 'min', 'max', 'skewness', 'kurtosis']].round(2).to_string())

# %%
"""
### Treasury-Swap Basis Time Series
"""

# %%
fig, ax = plt.subplots(figsize=(14, 8))

for col in basis_wide.columns:
    ax.plot(basis_wide.index, basis_wide[col], label=col, alpha=0.8, linewidth=1)

ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
ax.set_xlabel('Date')
ax.set_ylabel('Basis (bps)')
ax.set_title('Treasury-Swap Basis (Treasury Yield - Swap Rate)')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(DATA_DIR.parent / "_output" / "treasury_swap_basis.png", dpi=150, bbox_inches='tight')
plt.show()

# %%
"""
### Short-Term vs Long-Term Basis
"""

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Short-term (1Y, 2Y, 3Y)
short_cols = ['Arb_Swap_1', 'Arb_Swap_2', 'Arb_Swap_3']
for col in short_cols:
    if col in basis_wide.columns:
        axes[0].plot(basis_wide.index, basis_wide[col], label=col, alpha=0.8)
axes[0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
axes[0].set_title('Short-Term Basis (1-3 Year)')
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Basis (bps)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Long-term (10Y, 20Y, 30Y)
long_cols = ['Arb_Swap_10', 'Arb_Swap_20', 'Arb_Swap_30']
for col in long_cols:
    if col in basis_wide.columns:
        axes[1].plot(basis_wide.index, basis_wide[col], label=col, alpha=0.8)
axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
axes[1].set_title('Long-Term Basis (10-30 Year)')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Basis (bps)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(DATA_DIR.parent / "_output" / "treasury_swap_basis_by_term.png", dpi=150, bbox_inches='tight')
plt.show()

# %%
"""
### Correlation Matrix
"""

# %%
fig, ax = plt.subplots(figsize=(10, 8))
corr = basis_wide.corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax)
ax.set_title('Treasury-Swap Basis Correlations')
plt.tight_layout()
plt.savefig(DATA_DIR.parent / "_output" / "treasury_swap_basis_correlation.png", dpi=150, bbox_inches='tight')
plt.show()

# %%
"""
## Data Definitions

### Treasury-Swap Basis (ftsfr_treasury_swap_basis)

| Variable | Description |
|----------|-------------|
| unique_id | Tenor identifier (e.g., Arb_Swap_1, Arb_Swap_10) |
| ds | Date |
| y | Basis spread in basis points |

### Series

| Code | Description |
|------|-------------|
| Arb_Swap_1 | 1-Year Treasury-Swap basis |
| Arb_Swap_2 | 2-Year Treasury-Swap basis |
| Arb_Swap_3 | 3-Year Treasury-Swap basis |
| Arb_Swap_5 | 5-Year Treasury-Swap basis |
| Arb_Swap_10 | 10-Year Treasury-Swap basis |
| Arb_Swap_20 | 20-Year Treasury-Swap basis |
| Arb_Swap_30 | 30-Year Treasury-Swap basis |
"""
