import os
import shutil
import yfinance as yf
import pandas as pd
import time

CACHE_DIR = "cache"

def get_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    os.makedirs(CACHE_DIR, exist_ok=True)
    filename = f"{ticker}_{start}_{end}.parquet"
    filepath = os.path.join(CACHE_DIR, filename)

    if os.path.exists(filepath):
        try:
            df = pd.read_parquet(filepath)
            if not df.empty:
                return df
        except Exception as e:
            print(f"Error reading cache for {ticker}: {e}. Fetching fresh data...")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Fetching {ticker} from {start} to {end} (Attempt {attempt+1})...")
            t = yf.Ticker(ticker)
            df = t.history(start=start, end=end)
            
            if df.empty:
                print(f"No data found for {ticker} in range {start} to {end}.")
                return pd.DataFrame()
                
            df.to_parquet(filepath)
            return df
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return pd.DataFrame()

def clear_cache():
    if os.path.exists(CACHE_DIR):
        print(f"Clearing cache directory: {CACHE_DIR}")
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR)
