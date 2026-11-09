# Task 20: preventing infinite loops between agents — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["preventing infinite loops between agents"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Stop repeated agent/state visits and enforce an independent hop ceiling.

## Limits

Uses agent identity as the visit key. Real workflows should include normalized task/state fingerprints and durable global budgets.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
