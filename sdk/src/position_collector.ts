import "dotenv/config";
import { Connection } from "@solana/web3.js";
import { collectPositions } from "./positions.js";

const rpcUrl = process.env.RPC_URL;
const ownerAddress = process.env.POSITION_OWNER;
if (!rpcUrl) throw new Error("RPC_URL is required");
if (!ownerAddress) throw new Error("POSITION_OWNER is required");

const once = process.argv.includes("--once");
const pools = process.argv.slice(2).filter(x => x !== "--once");
if (!pools.length) throw new Error("Pass at least one pool address");

const intervalMs = Number(process.env.COLLECT_INTERVAL_MS ?? 30000);
const connection = new Connection(rpcUrl, "confirmed");

async function collectAll() {
  for (const poolAddress of pools) {
    try {
      const positions = await collectPositions(connection, poolAddress, ownerAddress);
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
