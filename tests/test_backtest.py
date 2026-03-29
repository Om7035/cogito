import pytest
import pandas as pd
import numpy as np
from cogito.backtest import run_backtest

def test_run_backtest_basic():
    # Simple data
    dates = pd.date_range('2020-01-01', periods=5)
    df = pd.DataFrame({
        'Open': [100, 101, 102, 103, 104],
        'High': [105, 106, 107, 108, 109],
        'Low': [95, 96, 97, 98, 99],
        'Close': [100, 101, 102, 103, 104],
        'Volume': [1000] * 5
    }, index=dates)
    
    # Mock cache to return this df
    import cogito.backtest
    old_get_data = cogito.backtest.get_data
    cogito.backtest.get_data = lambda t, s, e: df
    
    def simple_strat(df):
        return pd.Series([True] * len(df), index=df.index)
        
    metrics, equity = run_backtest('TEST', '2020-01-01', '2020-01-05', simple_strat)
    
    cogito.backtest.get_data = old_get_data
    
    assert 'Total Return' in metrics
    assert metrics['Number of Trades'] == 1
    assert len(equity) == 5

def test_backtest_no_data():
    import cogito.backtest
    old_get_data = cogito.backtest.get_data
    cogito.backtest.get_data = lambda t, s, e: pd.DataFrame()
    
    metrics, equity = run_backtest('EMPTY', '2020-01-01', '2020-01-05', lambda df: pd.Series())
    
    cogito.backtest.get_data = old_get_data
    assert metrics == {}
    assert equity.empty
