# Task 35: dynamic tool discovery and governance — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["dynamic tool discovery and governance"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Discover only approved tool versions, then recheck revocation at invocation time.

## Limits

In-memory tool metadata. Production needs signed manifests, schema review, tenant allowlists, provenance, and catalog refresh rules.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
