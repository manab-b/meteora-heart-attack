import "dotenv/config";
import { Connection, PublicKey } from "@solana/web3.js";
import { DLMM } from "./meteora_dlmm.js";

const rpcUrl = process.env.RPC_URL;
if (!rpcUrl) throw new Error("RPC_URL is required");
const pools = process.argv.slice(2).filter(x => x !== "--once");
const once = process.argv.includes("--once");
if (!pools.length) throw new Error("Pass at least one pool address");
const intervalMs = Number(process.env.COLLECT_INTERVAL_MS ?? 30000);
const left = Number(process.env.BINS_LEFT ?? 5);
const right = Number(process.env.BINS_RIGHT ?? 5);
const connection = new Connection(rpcUrl, "confirmed");

async function collect(poolAddress: string) {
  const pool = await DLMM.create(connection, new PublicKey(poolAddress), { cluster: "mainnet-beta" });
  const active = await pool.getActiveBin();
  const around = await pool.getBinsAroundActiveBin(left, right);
  const observedAt = new Date().toISOString();
  for (const b of around.bins as any[]) {
    console.log(JSON.stringify({
      source: "meteora-sdk", observed_at: observedAt, pool_address: poolAddress,
      active_bin_id: active.binId, active_bin_price: String(active.price),
      bin_id: b.binId, price: String(b.price),
      x_amount_raw: String(b.xAmount ?? "0"), y_amount_raw: String(b.yAmount ?? "0")
    }));
  }
}

async function run() {
  for (const address of pools) {
    try { await collect(address); }
    catch (error) { console.error(JSON.stringify({ source:"meteora-sdk", observed_at:new Date().toISOString(), pool_address:address, error:String(error) })); }
  }
  if (once) return;
  for (;;) {
    await new Promise(resolve => setTimeout(resolve, intervalMs));
    for (const address of pools) {
      try { await collect(address); }
      catch (error) { console.error(JSON.stringify({ source:"meteora-sdk", observed_at:new Date().toISOString(), pool_address:address, error:String(error) })); }
    }
  }
}
run().catch(error => { console.error(error); process.exit(1); });
