import os
import json
from dotenv import load_dotenv

# We'll use this if an OpenAI key is present, otherwise fallback to Rule-Based
load_dotenv()

SYSTEM_PROMPT = """
You are a Research Auditor for financial strategies.
Your goal is to evaluate a strategy claim based on backtest results.
Be objective, skeptical, and thorough. 
Assess strictly whether the claim's results are reproducible, robust to out-of-sample data, better than random chance, and profitable after transaction costs.
"""

def generate_report(results, claim, parsed_claim):
    """
    Generates a Markdown report summarizing the audit outcomes.
    Uses Rule-Based logic for now, with structure for OpenAI integration.
    """

    # 1. Determine Verdict (Rule-Based for Now)
    passed_tests = [t for t, res in results.items() if res.get('passed')]
    total_tests = len(results)
    
    # Key reliability checks
    oos_passed = results.get('out_of_sample', {}).get('passed', False)
    random_passed = results.get('random_baseline', {}).get('passed', False)
    costs_passed = results.get('transaction_costs', {}).get('passed', False)
    
    if oos_passed and random_passed and costs_passed:
        verdict = "HIGH CONFIDENCE"
        recommendation = "The strategy shows strong robustness across all core validation tests."
    elif oos_passed or random_passed:
        verdict = "MEDIUM CONFIDENCE"
        recommendation = "The strategy shows some merit but fails key robustness or baseline checks. Exercise caution."
    else:
        verdict = "LOW CONFIDENCE"
        recommendation = "The strategy failed fundamental robustness tests (Out-of-Sample or Random Baseline). It is likely overfit or statistically insignificant."

    # 2. Build Markdown Sections
    report = []
    report.append(f"# Audit Report: {verdict}")
    report.append(f"**Original Claim**: `{claim}`")
    report.append(f"**Strategy**: {parsed_claim.get('entry')} / {parsed_claim.get('exit')} on {parsed_claim.get('ticker')}")
    report.append("")
    
    report.append("## Summary Verdict")
    report.append(f"> **Verdict**: {verdict}")
    report.append(f"> **Recommendation**: {recommendation}")
    report.append("")

    report.append("## Test Results Table")
    report.append("| Test Name | Total Return | Sharpe | Max DD | Trades | Passed |")
    report.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    
    for test, res in results.items():
        name = test.replace('_', ' ').title()
        ret = f"{res.get('total_return', 0):.2%}"
        sharpe = f"{res.get('sharpe', 0):.2f}"
        dd = f"{res.get('max_drawdown', 0):.2%}"
        trades = res.get('num_trades', 0)
        status = "✅" if res.get('passed') else "❌"
        report.append(f"| {name} | {ret} | {sharpe} | {dd} | {trades} | {status} |")
    
    report.append("")
    report.append("## Evidence & Analysis")
    if oos_passed:
        report.append("- ✅ **Out-of-Sample Robustness**: Strategy maintained performance on unseen data.")
    else:
        report.append("- ❌ **Out-of-Sample Failure**: Strategy significantly underperformed or lost money on the 30% hold-out set, suggesting overfitting.")
        
    if random_passed:
        report.append("- ✅ **Statistical Edge**: Strategy outperformed random entry/exit points with similar trade counts.")
    else:
        report.append("- ❌ **No Statistical Edge**: A random baseline performed better, suggesting the observed returns may be coincidental.")

    if costs_passed:
        report.append("- ✅ **Economic Viability**: Strategy remains profitable after accounting for 0.1% transaction costs.")
    else:
        report.append("- ❌ **Cost Sensitivity**: Transaction costs (0.1%) wipe out the strategy's alpha.")

    # 3. OpenAI Integration Structure (Commented Out for Future)
    """
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        client = OpenAI()
        
        prompt = f'''
        Audit the following backtest results for the claim: "{claim}".
        Parsed parameters: {json.dumps(parsed_claim)}
        Results: {json.dumps(results)}
        
        Write a professional auditor's report in Markdown.
        Include a verdict (High, Medium, Low), detailed evidence bullets, and a conclusion.
        '''
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    """

    return "\n".join(report)
