# Task 15: graceful degradation and recoverability — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["graceful degradation and recoverability"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Open a circuit after transient failures and recover through a single half-open probe.

## Limits

Single-threaded circuit and fixed sample cache; production needs freshness metadata, concurrent probe control, and restrictions on degraded high-risk actions.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
