import "dotenv/config";
import { Connection } from "@solana/web3.js";
import { collectPositions, discoverPositionPools } from "./positions.js";

const rpcUrl = process.env.RPC_URL;
const ownerAddress = process.env.POSITION_OWNER;
if (!rpcUrl) throw new Error("RPC_URL is required");
if (!ownerAddress) throw new Error("POSITION_OWNER is required");

const cliArgs = process.argv.slice(2);
const once = cliArgs.includes("--once") || process.env.COLLECT_ONCE === "1";
// tsx may consume unknown long options before forwarding argv to the script.
// Keep discovery available through an environment flag so the one-shot Python
// wrapper can invoke the same collector without relying on tsx argument parsing.
const discoverOwnerPositions =
  cliArgs.includes("--discover-owner-positions") || process.env.DISCOVER_OWNER_POSITIONS === "1";
const pools = cliArgs.filter(
  (x) => x !== "--" && x !== "--once" && x !== "--discover-owner-positions",
);
if (discoverOwnerPositions && pools.length) {
  throw new Error("--discover-owner-positions cannot be combined with pool addresses");
}
if (!discoverOwnerPositions && !pools.length) throw new Error("Pass at least one pool address or use --discover-owner-positions");

const intervalMs = Number(process.env.COLLECT_INTERVAL_MS ?? 30000);
const connection = new Connection(rpcUrl, "confirmed");

async function collectAll() {
  const targetPools = discoverOwnerPositions
    ? await discoverPositionPools(connection, ownerAddress)
    : pools;

  if (discoverOwnerPositions && targetPools.length === 0) {
    console.error(JSON.stringify({
      source: "meteora-sdk",
      observed_at: new Date().toISOString(),
      owner: ownerAddress,
      positions_found: 0,
      error: "no Meteora PositionV2 accounts found for owner",
    }));
    return;
  }

  for (const poolAddress of targetPools) {
    try {
      const positions = await collectPositions(connection, poolAddress, ownerAddress);
      if (positions.length === 0) {
        console.error(JSON.stringify({
          source: "meteora-sdk",
          observed_at: new Date().toISOString(),
          pool_address: poolAddress,
          owner: ownerAddress,
          positions_found: 0,
          error: "no Meteora positions found for owner in requested pool",
        }));
        continue;
      }
      for (const position of positions) console.log(JSON.stringify(position));
    } catch (error) {
      console.error(JSON.stringify({
        source: "meteora-sdk",
        observed_at: new Date().toISOString(),
        pool_address: poolAddress,
        owner: ownerAddress,
        error: String(error),
      }));
    }
  }
}

async function loop() {
  await collectAll();
  if (once) return;
  for (;;) {
    await new Promise(resolve => setTimeout(resolve, intervalMs));
    await collectAll();
  }
}

loop().catch(error => {
  console.error(error);
  process.exit(1);
});
