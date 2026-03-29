import streamlit as st
import pandas as pd
from cogito.parser import parse_claim
from cogito.tests.reproducibility import run_reproducibility_test, get_strategy
from cogito.tests.out_of_sample import run_out_of_sample_test
from cogito.tests.random_baseline import run_random_baseline_test
from cogito.tests.buy_and_hold import run_buy_and_hold_test
from cogito.tests.transaction_costs import run_transaction_costs_test
from cogito.report import generate_report

st.set_page_config(page_title="Cogito Strategy Auditor", layout="wide")

st.title("Cogito Strategy Auditor")
st.markdown("Audit natural language trading claims instantly.")

claim = st.text_input("Enter a trading claim", "buy AAPL on monday and sell on friday")

if st.button("Audit Claim"):
    with st.spinner("Executing Audit..."):
        parsed = parse_claim(claim)
        
        st.subheader("Parsed Strategy")
        st.json(parsed)
        
        strategy_func = get_strategy(parsed["entry"], parsed["exit"])
        
        results = {}
        # Run tests
        results["reproducibility"] = run_reproducibility_test(parsed["ticker"], parsed["entry"], parsed["exit"], parsed["start"], parsed["end"])
        results["out_of_sample"] = run_out_of_sample_test(parsed["ticker"], strategy_func, parsed["start"], parsed["end"])
        results["random_baseline"] = run_random_baseline_test(parsed["ticker"], strategy_func, parsed["start"], parsed["end"])
        results["buy_and_hold"] = run_buy_and_hold_test(parsed["ticker"], parsed["start"], parsed["end"])
        results["transaction_costs"] = run_transaction_costs_test(parsed["ticker"], strategy_func, parsed["start"], parsed["end"])
        
        st.subheader("Audit Report")
        report = generate_report(results, claim, parsed)
        st.markdown(report)
        
        st.success("Audit complete!")
