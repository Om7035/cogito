import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

AGENT_PROMPT = """
You are an AI Quantitative Researcher. 
You are given the backtest performance of a trading strategy.
Your task:
1. Reflect on the results. Why did it fail or succeed?
2. Propose a refined version of the strategy to improve performance or robustness (e.g., adding a volatility filter, RSI, or better holding logic).
3. Write a Python function named `refined_strategy(df)` that implements this new logic using pandas. The DataFrame `df` has columns Open, High, Low, Close, Volume. Return a boolean pandas Series `signals`.

Output exactly in JSON format:
{
  "reflection": "Your analysis...",
  "new_hypothesis": "What you are changing...",
  "code": "def refined_strategy(df):\\n    import pandas as pd\\n    import numpy as np\\n    signals = pd.Series(False, index=df.index)\\n    # Your logic here\\n    return signals"
}
"""

def reflect_and_improve(original_claim, results):
    base_url = os.getenv("OPENAI_BASE_URL") # e.g. http://localhost:11434/v1 for Ollama
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = "dummy-key-for-local"
    model = os.getenv("AGENT_MODEL", "gpt-4")
    
    print("Agent is reflecting on results to propose an improvement...")
    try:
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)
            
        user_msg = f"Original Claim: {original_claim}\nResults: {json.dumps(results)}\nReflect and propose code."
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": AGENT_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        return json.loads(content)
    except Exception as e:
        print(f"Agent failed to reflect: {e}")
        return None
