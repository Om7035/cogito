import pandas as pd
from cogito.backtest import run_backtest
from cogito.cache import get_data
from cogito.tests.reproducibility import get_strategy

def run_out_of_sample_test(ticker, strategy_func, start, end):
    df = get_data(ticker, start, end)
    if len(df) == 0:
        return {}
    
    split_idx = int(len(df) * 0.7)
    split_date = df.index[split_idx]
    
    is_metrics, _ = run_backtest(ticker, start, str(split_date.date()), strategy_func)
    oos_metrics, _ = run_backtest(ticker, str(split_date.date()), end, strategy_func)
    
    oos_sharpe = float(oos_metrics.get("Sharpe Ratio (Ann.)", 0.0))
    passed = oos_sharpe > 0
    
    return {
        "total_return": float(oos_metrics.get("Total Return", 0.0)),
        "sharpe": oos_sharpe,
        "max_drawdown": float(oos_metrics.get("Max Drawdown", 0.0)),
        "num_trades": int(oos_metrics.get("Number of Trades", 0)),
        "passed": passed,
    }

if __name__ == "__main__":
    strat = get_strategy('first_trading_day_of_month', 'after_5_days')
    res = run_out_of_sample_test('AAPL', strat, '2020-01-01', '2023-01-01')
    print("Out of Sample:", res)
