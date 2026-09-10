-- Phase 2 verification report.
-- Run against the SQLite database produced by the read-only collectors.
-- No values are inferred; all counts come directly from persisted tables.

.headers on
.mode column

SELECT 'positions' AS dataset, COUNT(*) AS rows FROM position_snapshots;
SELECT 'bin_liquidity_snapshots' AS dataset, COUNT(*) AS rows FROM bin_liquidity_snapshots;
SELECT 'raw_snapshots' AS dataset, COUNT(*) AS rows FROM raw_snapshots;
SELECT 'drain_events' AS dataset, COUNT(*) AS rows FROM bin_drain_events;
SELECT 'paper_trades' AS dataset, COUNT(*) AS rows FROM paper_trades;

SELECT
  pool_address,
  COUNT(*) AS bin_rows,
  MIN(observed_at) AS first_observed_at,
  MAX(observed_at) AS last_observed_at,
  COUNT(DISTINCT bin_id) AS distinct_bins
FROM bin_liquidity_snapshots
GROUP BY pool_address
ORDER BY pool_address;

SELECT
  pool_address,
  COUNT(*) AS position_rows,
  COUNT(DISTINCT position_address) AS positions,
  MIN(observed_at) AS first_observed_at,
  MAX(observed_at) AS last_observed_at
FROM position_snapshots
GROUP BY pool_address
ORDER BY pool_address;

SELECT
  pool_address,
  COUNT(*) AS drain_rows,
  MIN(observed_at) AS first_observed_at,
  MAX(observed_at) AS last_observed_at
FROM bin_drain_events
GROUP BY pool_address
ORDER BY pool_address;

SELECT
  COUNT(*) AS closed_paper_trades,
  SUM(CASE WHEN net_pnl_sol IS NOT NULL THEN 1 ELSE 0 END) AS trades_with_net_pnl
FROM paper_trades;
