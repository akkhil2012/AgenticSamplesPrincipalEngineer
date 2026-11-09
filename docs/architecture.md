# Task 31: secure communication between autonomous agents — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["secure communication between autonomous agents"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Authenticate local agent envelopes with HMAC, bind audience and expiry, and reject replay or tampering.

## Limits

HMAC provides shared-key integrity, not transport confidentiality or independent workload identity. Production needs TLS/mTLS or workload credentials, key rotation, and a durable replay store.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
