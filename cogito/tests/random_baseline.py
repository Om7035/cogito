import pandas as pd
import numpy as np
from cogito.backtest import run_backtest
from cogito.tests.reproducibility import get_strategy

def run_random_baseline_test(ticker, strategy_func, start, end):
    actual_metrics, _ = run_backtest(ticker, start, end, strategy_func)
    
    def get_random_strategy():
        def strategy(*args):
            if len(args) == 2:
                dfs, closes = args
                # Multi asset random: generate random weights
                weights = pd.DataFrame(np.random.rand(*closes.shape), index=closes.index, columns=closes.columns)
                weights = weights.div(weights.sum(axis=1), axis=0) # sum to 1
                return weights
                
            df = args[0]
            signals = pd.Series(False, index=df.index)
            
            # Determine number of trades to simulate, roughly 10% of days
            num_days = len(df)
            trade_days = max(1, int(num_days * 0.1))
            
            random_indices = np.random.choice(num_days, size=trade_days, replace=False)
            for loc in random_indices:
                end_loc = min(loc + 5, num_days)
                signals.iloc[loc:end_loc] = True
                
            return signals
        return strategy

    random_strategy = get_random_strategy()
    rand_metrics, _ = run_backtest(ticker, start, end, random_strategy)
    
    rand_return = rand_metrics.get("Total Return", 0.0)
    act_return = actual_metrics.get("Total Return", 0.0)
    passed = float(act_return) > float(rand_return)
    
    return {
        "total_return": float(rand_return),
        "sharpe": float(rand_metrics.get("Sharpe Ratio (Ann.)", 0.0)),
        "max_drawdown": float(rand_metrics.get("Max Drawdown", 0.0)),
        "num_trades": int(rand_metrics.get("Number of Trades", 0)),
        "passed": passed,
    }

if __name__ == "__main__":
    strat = get_strategy('first_trading_day_of_month', 'after_5_days')
    res = run_random_baseline_test('AAPL', strat, '2020-01-01', '2023-01-01')
    print("Random Baseline:", res)
