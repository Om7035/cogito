import numpy as np
import pandas as pd
from cogito.backtest import run_backtest

def month_start_strategy(df, n_days=5):
    """
    Buys on the first trading day of the month and holds for N days.
    """
    signals = pd.Series(False, index=df.index)
    
    # Group by Year and Month to find the first trading day
    df['YearMonth'] = df.index.to_period('M')
    first_days_mask = ~df['YearMonth'].duplicated()
    first_days_indices = np.where(first_days_mask)[0]
    
    for loc in first_days_indices:
        # Set signal = True for the n_days
        end_loc = min(loc + n_days, len(signals))
        signals.iloc[loc:end_loc] = True
        
    return signals

if __name__ == '__main__':
    metrics, equity_curve = run_backtest(
        ticker='AAPL',
        start='2020-01-01',
        end='2023-01-01',
        strategy_func=lambda df: month_start_strategy(df, n_days=5)
    )
    
    print("\n=== Backtest Metrics ===")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k}: {v:.4f}")
        else:
            print(f"{k}: {v}")
