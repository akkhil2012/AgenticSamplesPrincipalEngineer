# Task 32: confused deputy problem in agentic ai — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["confused deputy problem in agentic ai"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Prevent a privileged deputy from acting outside the original user tenant, resource, and scopes.

## Limits

Trusted identity dictionaries stand in for verified delegation tokens. Never accept caller-supplied scopes as proof in a real gateway.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
