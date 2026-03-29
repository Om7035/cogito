import numpy as np
import pandas as pd
import multiprocessing
import time
from .cache import get_data

def run_backtest_with_timeout(ticker, start, end, strategy_func, transaction_cost=0.0, timeout=30):
    """
    Wrapper for run_backtest with a timeout using multiprocessing.
    """
    with multiprocessing.Pool(processes=1) as pool:
        result = pool.apply_async(run_backtest, (ticker, start, end, strategy_func, transaction_cost))
        try:
            return result.get(timeout=timeout)
        except multiprocessing.TimeoutError:
            print(f"Backtest for {ticker} timed out after {timeout} seconds.")
            return {}, pd.Series(dtype=float)
        except Exception as e:
            print(f"Backtest for {ticker} failed: {e}")
            return {}, pd.Series(dtype=float)

def run_backtest(ticker, start, end, strategy_func, transaction_cost=0.0, verbose=False):
    """
    Fetches daily OHLCV data for `ticker` between `start` and `end`.
    Handles single assets or comma-separated lists for portfolio rebalancing.
    `strategy_func` takes (df) for single asset, or (dfs_dict, closes_df) for portfolios.
    """
    try:
        if verbose:
            print(f"Starting backtest for {ticker} from {start} to {end}...")
            
        tickers = [t.strip() for t in ticker.split(',')] if ',' in ticker else [ticker]
        dfs = {}
        for t in tickers:
            df = get_data(t, start, end)
            if not df.empty:
                if df.index.tz is not None:
                    df.index = df.index.tz_convert(None)
                df.index = pd.to_datetime(df.index)
                dfs[t] = df
            elif verbose:
                print(f"Warning: No data found for {t}")
                
        if not dfs:
            if verbose: print("Aborting: No valid data found.")
            return {}, pd.Series(dtype=float)
            
        # Determine Multi-Asset Portfolio Mode vs Single Asset
        if len(tickers) == 1:
            df = dfs[tickers[0]]
            signals = strategy_func(df)
            
            # Normalize boolean signals to float weights
            df['Signal'] = signals.astype(float)
            df['Position'] = df['Signal'].shift(1).fillna(0.0)
            
            df['Asset_Ret'] = df['Close'].pct_change().fillna(0.0)
            df['Strat_Ret'] = df['Position'] * df['Asset_Ret']
            
            # Transaction costs based on positional change (turnover)
            prev_pos = df['Position'].shift(1).fillna(0.0)
            pos_change = (df['Position'] - prev_pos).abs()
            df['Strat_Ret'] -= pos_change * transaction_cost
            
            strat_rets = df['Strat_Ret']
            trades = (pos_change > 0).sum() / 2.0  # Approx pairs
            
        else:
            # Multi-asset Portfolio
            idx_list = [d.index for d in dfs.values()]
            all_dates = idx_list[0]
            for idx in idx_list[1:]:
                all_dates = all_dates.union(idx)
            all_dates = all_dates.sort_values().drop_duplicates()
            
            closes = pd.DataFrame(index=all_dates)
            for tk, tk_df in dfs.items():
                closes[tk] = tk_df['Close']
                
            closes = closes.ffill()
            asset_rets = closes.pct_change().fillna(0.0)
            
            # Strategy function must return DataFrame of target weights
            try:
                weights = strategy_func(dfs, closes)
            except TypeError:
                if verbose: print("Notice: Strategy doesn't support portfolios natively. Applying equal weight buy-and-hold.")
                weights = pd.DataFrame(1.0 / len(dfs), index=closes.index, columns=closes.columns)
                
            weights = weights.reindex(all_dates).fillna(0.0)
            positions = weights.shift(1).fillna(0.0)
            
            strat_rets = (positions * asset_rets).sum(axis=1)
            
            # Transaction costs from sum of absolute weight changes
            prev_positions = positions.shift(1).fillna(0.0)
            turnover = (positions - prev_positions).abs().sum(axis=1)
            strat_rets -= turnover * transaction_cost
            
            trades = (turnover > 0.01).sum()  # Count substantive rebalance events
            
        # Equity curve
        cum_ret = (1 + strat_rets).cumprod()
        total_return = cum_ret.iloc[-1] - 1.0 if not cum_ret.empty else 0.0
        
        # Sharpe Ratio (annualized)
        mean_ret = strat_rets.mean()
        std_ret = strat_rets.std()
        sharpe = np.sqrt(252) * mean_ret / std_ret if std_ret > 1e-8 else 0.0
            
        # Max Drawdown
        peak = cum_ret.cummax()
        drawdown = (cum_ret - peak) / peak
        max_drawdown = drawdown.min()
        
        metrics = {
            "Total Return": total_return,
            "Sharpe Ratio (Ann.)": sharpe,
            "Max Drawdown": max_drawdown,
            "Number of Trades": int(trades)
        }
        
        if verbose:
            print(f"Backtest complete. Trades: {int(trades)}, Return: {total_return:.2%}")
            
        return metrics, cum_ret
    except Exception as e:
        print(f"Unexpected error in backtest: {e}")
        return {}, pd.Series(dtype=float)
