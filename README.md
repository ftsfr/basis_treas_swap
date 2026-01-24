# Treasury-Swap Basis

Treasury-Swap arbitrage spreads measuring the difference between Treasury yields and swap rates.

## Overview

This pipeline calculates Treasury-Swap basis:

```
Basis = (Treasury Yield - Swap Rate) * 100
```

Results are in basis points.

## Interpretation

- **Basis > 0**: Treasuries yield more than swaps (Treasury-rich, swap-cheap)
- **Basis < 0**: Swaps yield more than Treasuries (Treasury-cheap, swap-rich)

## Series

- Arb_Swap_1: 1-Year basis
- Arb_Swap_2: 2-Year basis
- Arb_Swap_3: 3-Year basis
- Arb_Swap_5: 5-Year basis
- Arb_Swap_10: 10-Year basis
- Arb_Swap_20: 20-Year basis
- Arb_Swap_30: 30-Year basis

## Data Sources

- **Bloomberg**: Treasury constant maturity yields (USGG series)
- **Bloomberg**: USD swap rates (USSW series)

## Outputs

- `ftsfr_treasury_swap_basis.parquet`: Daily Treasury-Swap basis for all tenors

## Requirements

- Bloomberg Terminal running
- Python 3.10+
- xbbg package

## Setup

1. Ensure Bloomberg Terminal is running
2. Install dependencies: `pip install -r requirements.txt`
3. Run pipeline: `doit`

## Academic References

### Primary Papers

- **Du, Hebert, and Li (2023)** - "Intermediary Balance Sheets and the Treasury Yield Curve"
  - Documents regime change in Treasury-swap spreads post-GFC

- **Jermann (2020)** - "Negative Swap Spreads and Limited Arbitrage"
  - Review of Financial Studies
  - Explains negative swap spreads since 2008

- **Siriwardane, Sunderam, and Wallen** - "Segmented Arbitrage"
  - Provides data and analysis of Treasury-swap spreads

### Key Findings

- 30-year swap spreads have been negative since October 2008
- Regulatory changes increased cost of Treasury holdings
- Balance sheet constraints limit arbitrage
