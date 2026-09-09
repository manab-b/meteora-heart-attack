# Data flow

External Meteora adapters produce normalized snapshots. CollectorPipeline validates timestamps and persists observations.

The normalized storage layer is intentionally independent of HTTP clients and SDK objects. This makes historical replay deterministic and keeps the strategy layer testable without network access.

The live adapter should be added only after its exact current response schema is verified against Meteora's official API/SDK documentation.
