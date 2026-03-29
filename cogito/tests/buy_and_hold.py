import pandas as pd
from cogito.backtest import run_backtest

def get_buy_and_hold():
    def strategy(*args):
        if len(args) == 2:
            dfs, closes = args
            weights = pd.DataFrame(1.0 / len(closes.columns), index=closes.index, columns=closes.columns)
            return weights
        df = args[0]
        return pd.Series(True, index=df.index)
    return strategy

def run_buy_and_hold_test(ticker, start, end):
    strategy_func = get_buy_and_hold()
    metrics, _ = run_backtest(ticker, start, end, strategy_func)
    
    return {
        "total_return": float(metrics.get("Total Return", 0.0)),
        "sharpe": float(metrics.get("Sharpe Ratio (Ann.)", 0.0)),
        "max_drawdown": float(metrics.get("Max Drawdown", 0.0)),
        "num_trades": int(metrics.get("Number of Trades", 0)),
        "passed": True
    }

if __name__ == "__main__":
    res = run_buy_and_hold_test('AAPL', '2020-01-01', '2023-01-01')
    print("Buy and Hold:", res)
