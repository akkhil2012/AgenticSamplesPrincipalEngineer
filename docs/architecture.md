# Task 51: identitychain propagating user identity across multiple agents — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["identitychain propagating user identity across multiple agents"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Preserve original subject and tenant while attenuating delegated scopes at each hop.

## Limits

Immutable local identity chain only; production requires signed token exchange, audience/expiry binding, issuer verification, and delegation depth limits.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
