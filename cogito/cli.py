import os
import time
import click  # type: ignore
from cogito.logger import AuditLogger  # type: ignore

# Import tests
from cogito.tests.reproducibility import run_reproducibility_test, get_strategy  # type: ignore
from cogito.tests.out_of_sample import run_out_of_sample_test  # type: ignore
from cogito.tests.random_baseline import run_random_baseline_test  # type: ignore
from cogito.tests.buy_and_hold import run_buy_and_hold_test  # type: ignore
from cogito.tests.transaction_costs import run_transaction_costs_test  # type: ignore
from cogito.report import generate_report  # type: ignore
from cogito.cache import clear_cache  # type: ignore
from cogito.parser import parse_claim  # type: ignore
from cogito.agent import reflect_and_improve  # type: ignore
from cogito.db import save_audit  # type: ignore
from cogito.config import load_config, save_config  # type: ignore
import concurrent.futures

@click.group()
def cli():
    """Cogito CLI tool."""
    pass

@cli.command()
@click.argument('claim', type=str)
@click.option('--non-interactive', is_flag=True, help="Run all tests without prompting.")
@click.option('--verbose', is_flag=True, help="Show detailed logs.")
@click.option('--clear-cache', 'clear_cache_flag', is_flag=True, help="Clear the data cache before starting.")
@click.option('--agentic', is_flag=True, help="Enable adversarial agent to propose improvements.")
def audit(claim, non_interactive, verbose, clear_cache_flag, agentic):
    """Audit a financial claim."""
    if clear_cache_flag:
        clear_cache()
        
    os.makedirs('audits', exist_ok=True)
    log_file = os.path.join('audits', f"audit_{int(time.time())}.jsonl")
    logger = AuditLogger(log_file)
    
    click.echo(f"Starting audit for claim: {claim}")
    logger.log("audit_start", {"claim": claim})
    
    # 1. Parse claim
    parsed = parse_claim(claim)
    click.echo(f"Parsed claim: {parsed}")
    logger.log("parsed_claim", parsed)
    
    tests_available = {
        "reproducibility": run_reproducibility_test,
        "out_of_sample": run_out_of_sample_test,
        "random_baseline": run_random_baseline_test,
        "buy_and_hold": run_buy_and_hold_test,
        "transaction_costs": run_transaction_costs_test
    }
    
    tests_to_run = []
    
    # 2. Select tests
    if non_interactive:
        tests_to_run = list(tests_available.keys())
    else:
        click.echo("\nAvailable tests:")
        for t in tests_available.keys():
            if click.confirm(f"Do you want to run the '{t}' test?", default=True):
                tests_to_run.append(t)
                
    logger.log("tests_selected", {"tests": tests_to_run})
    
    # 3. Run selected tests
    results = {}
    strategy_func = get_strategy(parsed["entry"], parsed["exit"])
    
    click.echo("\nExecuting tests in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_test = {}
        for t in tests_to_run:
            logger.log("test_start", {"test": t})
            if t == "reproducibility":
                future = executor.submit(run_reproducibility_test, parsed["ticker"], parsed["entry"], parsed["exit"], parsed["start"], parsed["end"])
            elif t == "out_of_sample":
                future = executor.submit(run_out_of_sample_test, parsed["ticker"], strategy_func, parsed["start"], parsed["end"])
            elif t == "random_baseline":
                future = executor.submit(run_random_baseline_test, parsed["ticker"], strategy_func, parsed["start"], parsed["end"])
            elif t == "buy_and_hold":
                future = executor.submit(run_buy_and_hold_test, parsed["ticker"], parsed["start"], parsed["end"])
            elif t == "transaction_costs":
                future = executor.submit(run_transaction_costs_test, parsed["ticker"], strategy_func, parsed["start"], parsed["end"])
            future_to_test[future] = t
            
        for future in concurrent.futures.as_completed(future_to_test):
            t = future_to_test[future]
            try:
                res = future.result()
                results[t] = res
                logger.log("test_result", {"test": t, "result": res})
                if verbose:
                    click.echo(f"  [+] Finished {t}")
            except Exception as e:
                click.echo(f"  [!] Error running {t}: {e}")
                logger.log("test_error", {"test": t, "error": str(e)})
            
    # 4. Generate & Print Report
    report = generate_report(results, claim, parsed)
    logger.log("report_generated", {"report": report})
    
    click.echo("\n" + "="*50 + "\n")
    click.echo(report)
    click.echo("="*50 + "\n")
    click.echo(f"Detailed logs saved to {log_file}")
    
    # Save to SQLite Database
    save_audit(claim, parsed, results)
    click.echo("Audit archived in local SQLite database (audits/cogito.db).")
    
    if agentic:
        click.echo("\n" + "*"*50)
        click.echo("AGENTIC MODE: Analyzing results and generating improvements...")
        agent_response = reflect_and_improve(claim, results)
        if agent_response:
            click.echo(f"\n💡 Reflection:\n{agent_response.get('reflection', '')}")
            click.echo(f"\n🚀 New Hypothesis:\n{agent_response.get('new_hypothesis', '')}")
            
            click.echo("\nExecuting newly generated strategy...")
            code = agent_response.get("code", "")
            
            local_vars = {}
            try:
                exec(code, globals(), local_vars)
                refined_strategy = local_vars.get("refined_strategy")
                
                if refined_strategy:
                    from cogito.backtest import run_backtest  # type: ignore
                    new_results = {}
                    for t in tests_to_run:
                        if t == "reproducibility":
                            new_results[t], _ = run_backtest(parsed["ticker"], parsed["start"], parsed["end"], refined_strategy)
                        elif t == "out_of_sample":
                            new_results[t] = run_out_of_sample_test(parsed["ticker"], refined_strategy, parsed["start"], parsed["end"])
                        elif t == "random_baseline":
                            new_results[t] = run_random_baseline_test(parsed["ticker"], refined_strategy, parsed["start"], parsed["end"])
                        elif t == "buy_and_hold":
                            new_results[t] = run_buy_and_hold_test(parsed["ticker"], parsed["start"], parsed["end"])
                        elif t == "transaction_costs":
                            new_results[t] = run_transaction_costs_test(parsed["ticker"], refined_strategy, parsed["start"], parsed["end"])
                            
                    new_report = generate_report(new_results, f"{claim} (AI Refined)", parsed)
                    click.echo("\n" + "="*50 + "\n")
                    click.echo("🤖 AGENTIC REFINED REPORT:")
                    click.echo(new_report)
                    click.echo("="*50 + "\n")
            except Exception as e:
                click.echo(f"Failed to execute agent's code: {e}")

@cli.group()
def config():
    """Manage Cogito configurations."""
    pass

@config.command("set")
@click.argument('key')
@click.argument('value')
def set_config(key, value):
    """Set a configuration variable (e.g., config set cache_dir /tmp/cache)"""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    click.echo(f"[+] Config updated: {key} = {value}")

@config.command("get")
@click.argument('key', required=False)
def get_config(key):
    """Get a configuration variable or display all."""
    cfg = load_config()
    if key:
        click.echo(f"{key}: {cfg.get(key, 'Not Set')}")
    else:
        for k, v in cfg.items():
            click.echo(f"{k} = {v}")

if __name__ == "__main__":
    cli()
