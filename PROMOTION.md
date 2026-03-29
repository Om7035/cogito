# Social Media Promotion Drafts for Cogito

### 🚀 Reddit (r/algotrading, r/quant, r/MachineLearning)
**Title:** I built an open-source "Adversarial AI Auditor" for trading strategies. It automatically backtests and deconstructs natural language claims.

**Body:**
Hey everyone,

I've been frustrated by the sheer amount of "guaranteed strategy" noise on YouTube and Twitter (e.g., "Buy BTC on RSI crossovers for 500% returns"). To combat this, I built **Cogito**, an open-source command-line quantitative auditor.

Instead of writing custom Python code to verify every claim:
1. You literally type natural language into the CLI: `cogito audit "buy AAPL, MSFT on mondays and sell fridays"`.
2. It uses an LLM (OpenAI or local Ollama) to parse the target logic.
3. The engine automatically fetches cross-asset data (YFinance, CCXT) and runs a rigorous 5-step parallel validation suite: Reproducibility, Out-of-Sample variance, Random Baseline comparisons, Buy & Hold benchmarks, and 0.1% Transaction Costs analysis.
4. **But it doesn't stop there**: It has an `--agentic` mode where the LLM self-reflects on exactly why the strategy failed, writes a new Python hypothesis (e.g. "Adding a volatility filter"), injects it, and re-runs the 5 tests against it dynamically.

Everything is logged to a local SQLite database for scaling.

It's completely free and open-source under the MIT license. I'm looking for contributors to help add new data connectors, options chains, or custom strategy parsing!
[Link to Repository]

---

### 🐦 Twitter/X
Tired of fake trading "gurus"? Let AI disprove them. 

I just open-sourced **Cogito**: An adversarial multi-asset backtester.
Type "buy crypto when RSI > 70" into your terminal. Cogito:
1️⃣ Parses your English to code
2️⃣ Backtests it against 5 empirical friction tests
3️⃣ Re-writes the code if it fails 🤖

We parse data natively via CCXT + YFinance. Help me build the ultimate open-source financial auditor! 👇
[Link to Repo] #Algotrading #Quant #Python #OpenSource #OpenAI

---

### 👔 LinkedIn
The gap between qualitative financial assumptions and quantitative reality is massive. 

Today I'm releasing **Cogito**, an open-source financial library that acts as a bridge. Cogito is an intelligent, agent-driven CLI that directly ingests natural language hypotheses and dynamically subjects them to automated backtesting suites—testing for out-of-sample variance, transaction cost erosion, and random baseline clustering. 

Built on Python, Pandas, and FastAPI, Cogito allows researchers to focus on hypothesis generation rather than repetitive scaffolding. We warmly welcome open-source contributions from the data science and quantitative finance communities to expand our API integrations and validation environments.

Check out the repository here: [Link to Repo]
