# Verification record

Verified with Python 3.12 in deterministic mock mode on 29 October 2026.

| Check | Result |
|---|---|
| Editable install of exact project pins | Successful; pip check reports no broken requirements |
| `make seed` | SQLite initialized; both tenants have all current mandatory policies |
| `make test` | 33 passed; upstream ADK/Vertex/Starlette deprecation warnings |
| `make lint` | Ruff lint and format checks pass |
| Docker build | Successful with managed environment CA supplied via optional BuildKit secret |
| Compose startup | API healthy; dashboard running as non-root |
| `python scripts/demo.py` against container API | Chatbot zero actions; draft pending; independent approval; simulated campaign completed for two customers |
| `python scripts/smoke_dashboard.py` | Streamlit comparison and human approval controls pass against live API |
| HTTP endpoints | Swagger and Streamlit health respond 200 |

The managed cloud build used `docker build --secret id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt -t enterprise-agentic-demo:local .` followed by `docker compose -p agenticplatformdemo up -d --no-build --wait`. Ordinary local environments use `docker compose up --build` as documented. The CA mount is optional and is not copied into image layers.

Real model provider calls and real marketing activation were not executed. Provider timeout, retry, schema validation and fallback were tested with controlled test doubles. The limitations and production priorities are documented in the README and interview walkthrough.
