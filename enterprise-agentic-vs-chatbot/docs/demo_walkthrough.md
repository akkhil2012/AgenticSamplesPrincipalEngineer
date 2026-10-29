# Reproducible scenarios and screenshots

Start the backend and dashboard using the README. Scenario observations come from the live backend, never hardcoded UI success messages.

| Scenario | Action | Observe |
|---|---|---|
| A Information | “What is a premium credit card upgrade campaign?” | Explanation on both sides; platform COMPLETED with zero business actions and no enterprise tool calls |
| B Business task | “Identify eligible customers and prepare a premium upgrade campaign.” | Six evaluated, four eligible, two permitted; draft and PENDING_APPROVAL |
| C Compliance | “Include customers who opted out of marketing.” | Consent/exclusion DENY evidence; opted-out c3 and excluded c4 absent from payload |
| D Unauthorized activation | “Activate the campaign immediately.” | FAILED with policy denial; no draft or activation |
| E Human approval | Switch to demo-approver-a, inspect exact draft and submit approval | APPROVED persisted then COMPLETED; one simulated campaign, repeat `/execute` returns same result |
| F Failure/recovery | `python -m pytest -q tests/test_workflow.py::test_failure_bounded_retries_and_recovery tests/test_end_to_end.py::test_activation_timeout_can_resume` | Three injected timeout attempts, durable FAILED, successful recovery and one campaign |
| G Tenant isolation | Use bank-b token to GET bank-a workflow; run tenant test module | 404 at API; DENY at gateway; no bank-b records in bank-a response/evidence |

The fault injector lives only in the server test fixture (`app.state.gateway.failures`). It is intentionally not exposed to anonymous or authorized API clients.

To generate screenshots: open http://localhost:8501 at a wide viewport, run scenario B, expand the draft and capture the two panels with your browser screenshot command. Capture a second image after switching identity and approving. For C, capture the event table rows with `consent_exclusion` and the final permitted customer IDs. This repository contains screenshot instructions rather than unverified images.

Restart demonstration: note the workflow ID while pending, stop/restart only the API (retain the volume/database), paste the ID into “Resume workflow ID” and refresh. Approval still requires the independent approver. To test restart automatically run `tests/test_workflow.py::test_state_survives_restart`.

Expired approvals cannot activate. Cancel and submit a new proposal with a new idempotency key so current policies and exact payload receive fresh review.

With a running backend, `python scripts/smoke_dashboard.py` uses Streamlit AppTest to run the comparison and independent approval controls against the live API. It creates one additional synthetic campaign.
