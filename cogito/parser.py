import os
import json
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are a quantitative trading auditor. Your goal is to parse a natural language trading claim into a structured JSON dictionary.

Return EXACTLY a pure JSON string with no markdown blocks (no ```json).
The JSON MUST have the following keys:
- "ticker": (string, e.g. "AAPL", "BTC/USDT", or default "SPY" if none given)
- "entry": (string, extract the raw entry condition. e.g., "monday", "first_trading_day_of_month")
- "exit": (string, extract the exit condition. e.g., "friday", "after_5_days")
- "start": (string, YYYY-MM-DD, default "2020-01-01")
- "end": (string, YYYY-MM-DD, default "2023-01-01")

If the user mentions crypto or bitcoin, resolve the ticker to "BTC/USDT".
"""

def parse_claim(claim: str) -> dict:
    """
    Parses a claim string using OpenAI if API key is available.
    Otherwise uses a very simple mock/heuristic fallback parser.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    fallback = {
        "ticker": "AAPL",
        "entry": "first_trading_day_of_month",
        "exit": "after_5_days",
        "start": "2020-01-01",
        "end": "2023-01-01"
    }

    if "crypto" in claim.lower() or "btc" in claim.lower() or "bitcoin" in claim.lower():
        fallback["ticker"] = "BTC/USDT"
    if "monday" in claim.lower():
        fallback["entry"] = "monday"
        fallback["exit"] = "friday"
        
    if not api_key:
        print("Using purely mocked local parse rules: OPENAI_API_KEY not configured.")
        return fallback

    print("Querying OpenAI for structured claim parsing...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": claim}
            ],
            temperature=0.0
        )
        
        result_text = response.choices[0].message.content.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]
            
        parsed = json.loads(result_text)
        
        # Merge dicts to guarantee all keys exist
        for k in fallback:
            if k not in parsed:
                parsed[k] = fallback[k]
                
        return parsed
    except Exception as e:
        print(f"LLM Parsing failed: {e}. Falling back to default heuristics.")
        return fallback
