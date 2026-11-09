# Task 17: human accountability for consequential decisions — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["human accountability for consequential decisions"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Bind accountable human approval to an exact action digest with expiry and separation of duties.

## Limits

Approval records are trusted local objects; production requires authenticated reviewers, durable signatures, one-time consumption, and revocation.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
