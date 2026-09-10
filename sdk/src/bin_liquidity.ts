import { Connection, PublicKey } from "@solana/web3.js";
import { DLMM } from "./meteora_dlmm.js";

export type BinLiquidityObservation = {
  source: "meteora-sdk";
  observed_at: string;
  pool_address: string;
  active_bin_id: number;
  bin_id: number;
  price: string;
  x_amount_raw: string;
  y_amount_raw: string;
};

function asString(value: unknown, field: string): string {
  if (value === null || value === undefined) throw new Error(`${field} is missing`);
  return String(value);
}

function asNumber(value: unknown, field: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} is missing or invalid`);
  return parsed;
}

function entries(value: unknown): unknown[] {
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object") return Object.values(value as Record<string, unknown>);
  return [];
}

function normalizeBin(bin: any, observedAt: string, poolAddress: string, activeBinId: number): BinLiquidityObservation {
  const data = bin?.binData ?? bin;
  return {
    source: "meteora-sdk",
    observed_at: observedAt,
    pool_address: poolAddress,
    active_bin_id: activeBinId,
    bin_id: asNumber(data?.binId ?? data?.bin_id, "binId"),
    price: asString(data?.price, "price"),
    x_amount_raw: asString(data?.xAmount ?? data?.x_amount ?? data?.xAmountRaw, "xAmount"),
    y_amount_raw: asString(data?.yAmount ?? data?.y_amount ?? data?.yAmountRaw, "yAmount"),
  };
}

/**
 * Read-only bin liquidity collector. It only calls SDK read methods and emits
 * raw token amounts; no swap, add/remove liquidity, claim, signer, or tx path exists.
 */
export async function collectBinLiquidity(
  connection: Connection,
  poolAddress: string,
  lowerBinId: number,
  upperBinId: number,
): Promise<BinLiquidityObservation[]> {
  if (lowerBinId > upperBinId) throw new Error("lowerBinId must be <= upperBinId");
  const pool = await DLMM.create(connection, new PublicKey(poolAddress), {
    cluster: "mainnet-beta",
  });
  const activeBin = await pool.getActiveBin();
  const observedAt = new Date().toISOString();
  const bins = await pool.getBinsBetweenLowerAndUpperBound(lowerBinId, upperBinId);
  return entries(bins).map((bin) => normalizeBin(bin, observedAt, poolAddress, asNumber(activeBin.binId, "activeBin.binId")));
}
