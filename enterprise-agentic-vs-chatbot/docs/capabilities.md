# Five logical capabilities

```mermaid
flowchart LR
  I[1 Interaction: identity, tenant, validation, correlation, rate limiting] --> O[2 Orchestration: ADK supervisor and specialists]
  O --> M[3 Model and knowledge: routing, fallback, usage, tenant policy search]
  O --> G[4 Governance and tools: PDP, PEP, scoped tools, human approval]
  I --> R[5 Operational control: SQL state, audit, tracing, retries, idempotency]
  O --> R
  M --> R
  G --> R
```

| Capability | Implemented boundary | Production evolution |
|---|---|---|
| Interaction | FastAPI, fixed demo token lookup, server-derived tenant, Pydantic, process-local rate budget | OIDC gateway, distributed quotas and CSRF/session controls for browser auth |
| Orchestration | ADK SequentialAgent, ParallelAgent and custom typed BaseAgent specialists | Durable queue workers, cancellation signals, resource admission and deadlines |
| Models and knowledge | LiteLLM provider interface, timeout/retries/mock fallback, intent schema, token/cost estimates, lexical policy search | Provider budgets, route health, vector search ACLs, evaluation and policy release process |
| Governance and tools | Tool gateway PEP/PDP, agent allowlists, tenant checks, independent payload-bound expiring approval | Signed service identities, policy engine integration, immutable evidence |
| Operations | SQLite workflow/checkpoints/campaign/audit, local transactional idempotency, OTel spans, bounded retries | PostgreSQL, migrations, outbox, SLOs, central OTLP collector and disaster recovery |

An approver is a human decision maker, not an agent role. Compliance officers inspect same-tenant evidence but cannot start requests or approve campaigns. Managers prepare proposals and can cancel their own nonterminal workflows. Only the independent approver who granted approval may resume that activation.
