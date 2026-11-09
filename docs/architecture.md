# Task 06: deterministic workflow vs autonomous planning — Architecture

This diagram describes the **logical teaching flow**, not independently deployed services.

```mermaid
flowchart LR
 A["Synthetic example input"] --> B["Demonstrate deterministic workflow vs autonomous planning"]
 B --> C["Apply the example's checks"]
 C --> D["Produce demo result"]
 C -. "Invalid or rejected case" .-> E["Error / safe failure"]
 D --> F["Compare with expected_output.json"]
```

## What the demo demonstrates

Select a fixed workflow for known work and validate a bounded proposed plan for novel work.

The code and tests are in [concept-lab](../concept-lab/). The architecture above is deliberately conceptual; the actual implementation may be a single in-process Python program.

## What is missing for production

Planning is injected and scripted; production plans need typed arguments, authorization, and side-effect safeguards.
