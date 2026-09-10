import "dotenv/config";
import { Connection } from "@solana/web3.js";
import { collectBinLiquidity } from "./bin_liquidity.js";

const rpcUrl = process.env.RPC_URL;
const poolAddress = process.env.POOL_ADDRESS;
const lowerBinId = Number(process.env.LOWER_BIN_ID);
const upperBinId = Number(process.env.UPPER_BIN_ID);

if (!rpcUrl || !poolAddress || !Number.isInteger(lowerBinId) || !Number.isInteger(upperBinId)) {
  throw new Error("RPC_URL, POOL_ADDRESS, LOWER_BIN_ID, and UPPER_BIN_ID are required");
}

const once = process.argv.includes("--once");
const intervalMs = Number(process.env.COLLECT_INTERVAL_MS ?? 30000);
if (!Number.isFinite(intervalMs) || intervalMs <= 0) {
  throw new Error("COLLECT_INTERVAL_MS must be a positive number");
}

const connection = new Connection(rpcUrl, "confirmed");

async function collect() {
  try {
    const observations = await collectBinLiquidity(
      connection,
      poolAddress,
      lowerBinId,
      upperBinId,
    );
    for (const observation of observations) console.log(JSON.stringify(observation));
  } catch (error) {
    console.error(JSON.stringify({
      source: "meteora-sdk",
      observed_at: new Date().toISOString(),
      pool_address: poolAddress,
      lower_bin_id: lowerBinId,
      upper_bin_id: upperBinId,
      error: String(error),
    }));
  }
}

async function loop() {
  await collect();
  if (once) return;
  for (;;) {
    await new Promise(resolve => setTimeout(resolve, intervalMs));
    await collect();
  }
}

loop().catch(error => {
  console.error(error);
  process.exit(1);
});
