# Task 36: protecting agents from malicious tool responses — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["protecting agents from malicious tool responses"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Accept only structured tool data and prevent returned text from becoming executable instructions.

## Limits

Strict structured outputs reduce this attack surface; this does not detect all prompt injection in free text or validate the truth of returned data.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
