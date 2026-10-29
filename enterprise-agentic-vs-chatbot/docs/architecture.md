# Architecture and boundaries

The baseline has no reference to repositories or tool gateways. It can only call the model interface.

```mermaid
flowchart LR
  User --> API[FastAPI chatbot endpoint] --> Service[ChatbotService] --> Model[ModelGateway: mock or LiteLLM] --> Text[Conversational answer]
```

The enterprise path separates probabilistic interpretation from deterministic authorization and state transitions.

```mermaid
flowchart TD
  UI[Streamlit or API client] --> Auth[Identity, tenant, validation, correlation, rate limit]
  Auth --> Workflow[WorkflowService and transition rules]
  Workflow --> Supervisor[ADK Supervisor]
  Supervisor --> Specialists[ADK specialist agents]
  Specialists --> Gateway[ToolGateway]
  Gateway --> PEP[Policy Enforcement Point]
  PEP --> PDP[Policy Decision Point]
  PEP --> Tools[Local fixture and campaign tools]
  Workflow --> DB[(SQLAlchemy / SQLite)]
  Tools --> DB
  Workflow --> Model[LiteLLM / mock ModelGateway]
  Gateway --> Knowledge[Versioned tenant policies]
  Approval[Independent human approver] --> Workflow
  Gateway --> Evidence[Audit and OpenTelemetry]
```

Tool implementations execute only after gateway authorization. Agent methods receive a scoped helper carrying their fixed agent name; public APIs do not let callers supply agent identity. This is a trusted application boundary, not sandboxing against arbitrary Python execution inside the process.

```mermaid
flowchart LR
  S[Sequential supervisor] --> C[Customer insights]
  C --> P[Parallel analysis]
  P --> E[Engagement]
  P --> O[Offer recommendation]
  E --> M[Mandatory compliance]
  O --> M
  M --> D[Campaign draft and approval request]
```

Parallel agents read the same eligibility results and write disjoint state keys. Compliance depends on their completion; the campaign agent validates all contracts before constructing a payload. The ADK runner is per invocation; SQL checkpoints and audit events are the source of durable business truth.

```mermaid
flowchart TB
  subgraph ControlPlane[Control plane]
    Identity[Identity and roles]
    Policies[Tenant policies and versions]
    Approval[Approval and least agency]
    State[Workflow lifecycle and budgets]
  end
  subgraph ExecutionPlane[Execution plane]
    Agents[ADK agents]
    Models[Model gateway]
    Tooling[Tool gateway and adapters]
  end
  Identity --> Tooling
  Policies --> Tooling
  Approval --> Tooling
  State --> Agents
  Agents --> Models
  Agents --> Tooling
  Tooling --> Audit[Durable audit and tracing]
```

The control plane is a logical boundary in this modular monolith, not a separately deployed service. Policy rules are versioned fixture data while their mandatory enforcement is Python code. The current retrieval service uses lexical search, tenant filtering, current version selection and expiry checks; it can be replaced with a vector store without changing callers. Policy retrieval is not delegated to an LLM. The offer agent augments a model explanation with tenant-scoped policy text and source/version references. This RAG explanation is advisory; offer selection and compliance use deterministic data.

```mermaid
sequenceDiagram
  participant A as Scoped agent
  participant G as Tool gateway
  participant E as PEP
  participant P as PDP
  participant T as Tool implementation
  participant D as SQL evidence
  A->>G: tool, trusted identity, workflow, resource
  G->>E: authorize invocation
  E->>P: subject/action/resource/environment
  P-->>E: ALLOW / DENY / APPROVAL_REQUIRED
  E->>D: decision evidence
  alt ALLOW
    E-->>G: proceed
    G->>T: execute bounded local operation
    T-->>G: result
    G->>D: outcome and latency
  else denied
    E-->>G: PolicyDenied
    G-->>A: safe failure
  end
```

SQL transactions include the simulated side effect and audit/state updates. A unique campaign workflow key prevents duplicate drafts. Replayed completed execution returns the same stored outcome. The original approver's identity is required even on replay. Request keys cannot be reused for a different message.

No network calls occur in mock mode. Dependencies may emit their own deprecation warnings on import. Application telemetry intentionally excludes prompts and raw tool arguments. Production exporters must preserve this redaction boundary.
