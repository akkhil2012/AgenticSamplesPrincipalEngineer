# Verification

Executed on 29 October 2026 with Python 3.12 in a fresh virtual environment containing only `requirements.txt` dependencies.

| Check | Result |
|---|---|
| `python -m pip install -r requirements.txt` | Successful |
| `python -m pip check` | No broken requirements |
| `python -m pytest -q` | **28 passed**; one upstream Starlette/AnyIO deprecation warning |
| `python demo.py` | All four scenarios passed through FastAPI routes with isolated temporary SQLite state |
| `python main.py` live server | Health and Swagger returned HTTP 200; all four scenarios passed over HTTP |
| Ruff lint and format checks | Passed |
| `git diff --check` | Passed |

The scenarios demonstrated an APPROVE recommendation pending human approval, a blocked disabled agent, a REJECT recommendation after increasing the minimum credit score to 800, and an audited denial of `disburse_loan`.

Tests additionally verified immutable configuration history, exact execution snapshots, restart persistence, policy checks before each action, concurrent configuration-update conflicts, input validation and safe handling of invalid agent output. A test initially matched a credit-score substring inside a timestamp; it was corrected to inspect audit fields and decision text rather than unrelated generated metadata.

No external model, real customer data, final loan approval or loan disbursement was used. Authentication and a final human decision process are deliberately outside this minimal demonstration; see the README for the scope and production discussion.
