# Comparison matrix

| Dimension | Conversational baseline | Enterprise workflow |
|---|---|---|
|Primary objective|Answer a question|Achieve a governed business outcome|
|Behavior|Conversational advice|Goal-directed workflow|
|Reasoning and planning|Prompt-based answer|Intent classification plus explicit deterministic plan|
|Agent orchestration|None|ADK sequential and parallel specialists|
|Tool invocation|None|PDP/PEP before every business tool|
|Knowledge retrieval|No enterprise retrieval|Tenant-scoped current policy search|
|Business execution|Zero actions|Draft and simulated activation|
|Persistence|No business state|SQL workflow, checkpoints, approvals and campaigns|
|Authentication and authorization|Public synthetic advisory endpoint|Server-derived identity/tenant, RBAC, least privilege|
|Human approval|Advice to obtain approval|Independent payload-bound expiring approval|
|Observability|Model usage and latency|Model/tool/agent spans plus durable audit timeline|
|Error recovery|Model retries/fallback|Bounded tool and workflow retries with checkpoint recovery|
|Scalability|Stateless service path|Single-node SQLite writer serialization in demo|
|Cost management|Estimated tokens and model cost|Model cost evidence and bounded execution budgets|
|Governance and accountability|No delegated authority|Explicit human approver and tool decision evidence|

These are implementation choices. Chatbots may implement retrieval, tools, authentication and durable workflows; agentic systems may omit them. Multiple agents introduce coordination and operational overhead, so use them for independent capabilities, ownership boundaries or useful parallel work. This small domain could also be implemented with one deterministic workflow service. The educational ADK decomposition makes delegation, state contracts and permission boundaries visible.

“Agentic” does not make an LLM a policy authority. Business checks remain deterministic regardless of provider output, user instructions or model confidence. The demo's specialist calculations intentionally use fixtures and rules; the model is an interchangeable reasoning/advisory component rather than a prerequisite for safety.
