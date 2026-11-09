# Task 50: leastagency least privilege and least agency enforcement — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["leastagency least privilege and least agency enforcement"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Enforce a per-run action allowance independently of available tools and cap cumulative side effects.

## Limits

Local single-worker counters; production needs atomic reservations, durable accounting, authenticated scopes, and idempotent tool dispatch.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
