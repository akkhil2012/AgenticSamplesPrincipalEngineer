# Task 23: reflection pattern in production — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["reflection pattern in production"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Use bounded critique and revision, then apply an independent final acceptance check.

## Limits

The acceptance rule checks a format, not factual correctness. Use external evidence and held-out evaluation before enabling reflection in production.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
