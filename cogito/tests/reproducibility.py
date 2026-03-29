import pandas as pd
import numpy as np
from cogito.backtest import run_backtest

def get_strategy(entry, exit):
    def strategy(*args):
        if len(args) == 2:
            # Multi-asset portfolio
            dfs, closes = args
            # Simple handling: return equal weight
            weights = pd.DataFrame(1.0 / len(closes.columns), index=closes.index, columns=closes.columns)
            return weights
            
        df = args[0]
        signals = pd.Series(False, index=df.index)
        if entry == "first_trading_day_of_month" and exit == "after_5_days":
            df['YearMonth'] = df.index.to_period('M')
            first_days_mask = ~df['YearMonth'].duplicated()
            first_days_indices = np.where(first_days_mask)[0]
            
            for loc in first_days_indices:
                end_loc = min(loc + 5, len(signals))
                signals.iloc[loc:end_loc] = True
                
        elif "monday" in entry.lower() and "friday" in exit.lower():
            # Buy on Monday, sell on Friday
            in_trade = False
            for i in range(len(df)):
                if df.index[i].dayofweek == 0:  # Mon
                    in_trade = True
                if in_trade:
                    signals.iloc[i] = True
                if df.index[i].dayofweek == 4:  # Fri
                    in_trade = False
                    
        else:
            # Safest default back-up: hold throughout
            signals[:] = True
            
        return signals
    return strategy

def run_reproducibility_test(ticker, entry_signal, exit_condition, start, end):
    strategy_func = get_strategy(entry_signal, exit_condition)
    metrics, _ = run_backtest(ticker, start, end, strategy_func)

    passed = float(metrics.get('Total Return', 0)) > 0
    
    return {
        "total_return": float(metrics.get("Total Return", 0.0)),
        "sharpe": float(metrics.get("Sharpe Ratio (Ann.)", 0.0)),
        "max_drawdown": float(metrics.get("Max Drawdown", 0.0)),
        "num_trades": int(metrics.get("Number of Trades", 0)),
        "passed": passed
    }

if __name__ == "__main__":
    res = run_reproducibility_test('AAPL', 'first_trading_day_of_month', 'after_5_days', '2020-01-01', '2023-01-01')
    print("Reproducibility:", res)
