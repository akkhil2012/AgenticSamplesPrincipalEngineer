# Workflow and sequence

```mermaid
stateDiagram-v2
  [*] --> CREATED
  CREATED --> RUNNING
  RUNNING --> PENDING_APPROVAL
  RUNNING --> COMPLETED: informational request
  RUNNING --> FAILED
  PENDING_APPROVAL --> APPROVED: independent payload-bound decision
  PENDING_APPROVAL --> REJECTED
  APPROVED --> COMPLETED: simulated activation
  APPROVED --> FAILED
  FAILED --> RUNNING: requester retries analysis
  FAILED --> APPROVED: original approver retries execution
  CREATED --> CANCELLED
  PENDING_APPROVAL --> CANCELLED
  APPROVED --> CANCELLED
  FAILED --> CANCELLED
```

Terminal workflows do not transition. The FAILED recovery edge depends on whether a valid approval exists. Analysis retries are capped at three workflow attempts; execution shares a total attempt cap of six. Each individual tool operation tries at most three times. Provider calls have a configurable timeout and bounded retry count. Local fixture tools are synchronous bounded operations; any remote replacement must enforce its own I/O deadline.

```mermaid
sequenceDiagram
  actor M as Marketing manager
  participant API as FastAPI
  participant DB as SQLite workflow and audit
  participant S as ADK supervisor
  participant C as Customer insights
  participant E as Engagement
  participant O as Offers
  participant G as Governed gateway
  participant X as Compliance and campaign
  actor H as Independent approver
  M->>API: message + bearer + idempotency key
  API->>DB: commit CREATED workflow
  API->>S: run with tenant and identity
  S->>C: retrieve and evaluate eligibility via gateway
  C->>G: profile / eligibility tools
  G-->>C: tenant-scoped records
  par Engagement
    S->>E: engagement analysis via gateway
  and Recommendations
    S->>O: offer selection via gateway
  end
  S->>X: deterministic consent, exclusion and policy checks
  X->>G: draft and submit approval
  G->>DB: draft hash, checkpoints, audit
  API->>DB: commit PENDING_APPROVAL
  API-->>M: reviewable draft and payload hash
  H->>API: approve exact payload hash
  API->>DB: commit APPROVED and expiring approval evidence
  API->>G: simulate activation under approver identity
  G->>G: revalidate approval, current policy and customer consent
  G->>DB: simulated side effect + outcome + audit + COMPLETED
  API-->>H: structured outcome
```

A process crash during analysis rolls back to the prior committed state (normally CREATED). A handled failure commits safe checkpoints and FAILED. A crash after APPROVED commit resumes with `/execute`; activation and COMPLETED commit atomically. External marketing systems are deliberately absent, so local rollback suffices here. A production remote activation needs idempotency keys and an outbox/reconciliation workflow.
