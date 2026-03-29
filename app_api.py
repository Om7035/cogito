from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import concurrent.futures

from cogito.parser import parse_claim
from cogito.tests.reproducibility import get_strategy, run_reproducibility_test
from cogito.tests.out_of_sample import run_out_of_sample_test
from cogito.tests.random_baseline import run_random_baseline_test
from cogito.tests.buy_and_hold import run_buy_and_hold_test
from cogito.tests.transaction_costs import run_transaction_costs_test
from cogito.report import generate_report
from cogito.db import save_audit
from cogito.config import load_config

app = FastAPI(title="Cogito API", description="Automated Strategy Auditing Service")

class AuditRequest(BaseModel):
    claim: str

@app.post("/audit")
def create_audit(request: AuditRequest):
    try:
        parsed = parse_claim(request.claim)
        strategy_func = get_strategy(parsed["entry"], parsed["exit"])
        
        cfg = load_config()
        max_workers = int(cfg.get("max_workers", 5))
        
        results = {}
        tests_to_run = ["reproducibility", "out_of_sample", "random_baseline", "buy_and_hold", "transaction_costs"]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_test = {}
            for t in tests_to_run:
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
                test_name = future_to_test[future]
                try:
                    results[test_name] = future.result()
                except Exception as exc:
                    results[test_name] = {"passed": False, "error": str(exc)}
        
        report = generate_report(results, request.claim, parsed)
        save_audit(request.claim, parsed, results, "API_RUN")
        
        return {
            "status": "success",
            "parsed": parsed,
            "results": results,
            "markdown_report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
