import "dotenv/config";
import { Connection, PublicKey } from "@solana/web3.js";
import DLMM from "@meteora-ag/dlmm";

const rpcUrl = process.env.RPC_URL;
if (!rpcUrl) throw new Error("RPC_URL is required");
const pools = process.argv.slice(2);
if (!pools.length) throw new Error("Pass at least one pool address");
const intervalMs = Number(process.env.COLLECT_INTERVAL_MS ?? 30000);
const left = Number(process.env.BINS_LEFT ?? 5);
const right = Number(process.env.BINS_RIGHT ?? 5);

async function collect(poolAddress: string) {
  const connection = new Connection(rpcUrl, "confirmed");
  const pool = await DLMM.create(connection, new PublicKey(poolAddress), { cluster: "mainnet-beta" });
  const active = await pool.getActiveBin();
  const around = await pool.getBinsAroundActiveBin(left, right);
  return {
    source: "meteora-sdk",
    observed_at: new Date().toISOString(),
    pool_address: poolAddress,
    active_bin_id: active.binId,
    active_bin_price: active.price,
    bins: around.bins.map((b: any) => ({
      bin_id: b.binId, price: b.price,
      x_amount: String(b.xAmount ?? "0"), y_amount: String(b.yAmount ?? "0")
    }))
  };
}

async function loop() {
  for (;;) {
    for (const address of pools) {
      try { console.log(JSON.stringify(await collect(address))); }
      catch (error) {
        console.error(JSON.stringify({
          source: "meteora-sdk", observed_at: new Date().toISOString(),
          pool_address: address, error: String(error)
        }));
      }
    }
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }
}
loop().catch(error => { console.error(error); process.exit(1); });
