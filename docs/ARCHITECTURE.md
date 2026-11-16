# Architecture

```mermaid
flowchart TD
    A[CLI Arabic or English] --> B[Planner: Claude or deterministic mock]
    B --> C[Validated CSV loader]
    C --> D[Incident analyzer]
    D --> E[Naive baseline forecaster]
    E --> F[SDG-tagged recommendation tool]
    F --> G[Pydantic structured report]
    G --> H[Human road-safety analyst]
```

The live planner uses Anthropic tool-use with a strict allowlist and a 12-round cap. Computations and recommendations are derived from local tools, not model-generated numeric claims. The mock route runs deterministically without network or credentials. No tool makes operational or enforcement changes.
