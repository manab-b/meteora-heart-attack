# Live collector

The live collector uses Meteora's production DLMM Data API as the indexed discovery layer. Meteora documents a 30 RPS limit, so this project deliberately targets a lower request rate and applies retry/backoff for transient failures.

Current live layer:
- resilient HTTP JSON client
- conservative rate limiter
- paginated pool discovery contract
- normalized snapshot pipeline
- SQLite persistence

The API client is read-only. No private key, signer, transaction builder, or execution path is present.

Position-level fee truth should come from authoritative position data rather than estimating fees from pool-wide volume. Meteora's current SDK/documentation exposes position reads and unclaimed fee information, so the next adapter should normalize that exact response into `PositionSnapshot` after schema verification.
