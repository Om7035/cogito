from cogito.backtest import run_backtest
from cogito.tests.reproducibility import get_strategy

def run_transaction_costs_test(ticker, strategy_func, start, end):
    # Base strategy with zero costs already computed typically, but let's compare internally
    no_cost_metrics, _ = run_backtest(ticker, start, end, strategy_func, transaction_cost=0.0)
    cost_metrics, _ = run_backtest(ticker, start, end, strategy_func, transaction_cost=0.001)

    net_return = cost_metrics.get("Total Return", 0.0)
    passed = float(net_return) > 0
    
    return {
        "total_return": float(net_return),
        "sharpe": float(cost_metrics.get("Sharpe Ratio (Ann.)", 0.0)),
        "max_drawdown": float(cost_metrics.get("Max Drawdown", 0.0)),
        "num_trades": int(cost_metrics.get("Number of Trades", 0)),
        "passed": passed
    }

if __name__ == "__main__":
    strat = get_strategy('first_trading_day_of_month', 'after_5_days')
    res = run_transaction_costs_test('AAPL', strat, '2020-01-01', '2023-01-01')
    print("Transaction Costs:", res)
