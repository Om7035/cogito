# Contributing to Cogito

First off, thank you for considering contributing to Cogito! 🎉
It's people like you that make Cogito such a great tool for the quantitative research community.

## 🧠 How Can I Contribute?

Cogito is built explicitly to be extended. We welcome contributions in all forms:
- **New Validation Tests**: Submit new statistical, adversarial, or out-of-sample algorithms to `cogito/tests/`.
- **New Asset Classes**: Add integrations for new APIs (Options, Commodities, DeFi) in `cogito/cache.py`.
- **Bug Fixes**: Resolve open issues on GitHub.
- **Reporting Enhancements**: Improve the LLM system prompts or formatting in `cogito/report.py`.

## 🛠️ Local Development Setup

1. Fork and clone the repository.
2. Create your virtual environment: `python -m venv .venv`
3. Install in editable mode: `pip install -e .`
4. Make sure to set your `.env` variables if you are working on the LLM functions!

## 📜 Pull Request Guidelines

1. **Test Your Code:** Ensure `pytest tests/` passes before submitting your PR.
2. **Document Changes:** If you add a new test, document it in the README so users know it exists.
3. **Commit Messages:** Keep your commit messages clear and descriptive.

Let's build the ultimate open-source financial auditor together!
