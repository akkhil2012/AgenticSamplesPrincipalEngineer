# Task 44: graphagent knowledge graph vs vector search — Architecture

```mermaid
flowchart LR
 A["Synthetic input"] --> B["graphagent knowledge graph vs vector search"]
 B --> C["Validation and demo logic"]
 C --> D["Result"]
 C -. "Failure / invalid case" .-> E["Reject or handle"]
 D --> F["Tests and expected output"]
```

**Scope:** This shows a logical in-process concept lab, not a deployed enterprise topology.

## Demonstrated behavior

Compare relationship traversal with cosine similarity over fixed example embeddings.

## Limits

Hand-authored vectors demonstrate mechanics only. Similarity is not authorization or relationship proof; use actual embeddings and graph provenance in a real system.

See [the implementation](../concept-lab/main.py) and [tests](../concept-lab/test_main.py) for exact behavior.
