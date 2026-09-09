import { PublicKey } from "@solana/web3.js";
import DLMM from "@meteora-ag/dlmm";

export type PositionObservation = {
  source: "meteora-sdk";
  observed_at: string;
  pool_address: string;
  owner: string;
  position_address: string;
  lower_bin_id: number;
  upper_bin_id: number;
  total_x_amount_raw: string;
  total_y_amount_raw: string;
  fee_x_raw: string;
  fee_y_raw: string;
  total_claimed_fee_x_raw: string;
  total_claimed_fee_y_raw: string;
  token_x_decimals: number | null;
  token_y_decimals: number | null;
};

function asString(value: unknown): string {
  if (value === null || value === undefined) throw new Error("required numeric field is missing");
  return String(value);
}

function asNumber(value: unknown, field: string): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} is missing or invalid`);
  return parsed;
}

/**
 * Read-only position collector. No signer, wallet keypair, transaction builder,
 * claim, swap, or liquidity mutation is used here.
 */
export async function collectPositions(
  connection: ConstructorParameters<typeof DLMM>[0],
  poolAddress: string,
  ownerAddress: string,
): Promise<PositionObservation[]> {
  const pool = await DLMM.create(connection, new PublicKey(poolAddress), {
    cluster: "mainnet-beta",
  });
  const owner = new PublicKey(ownerAddress);
  const result = await pool.getPositionsByUserAndLbPair(owner);
  const observedAt = new Date().toISOString();
  const tokenXDecimals = pool.tokenX.decimal ?? null;
  const tokenYDecimals = pool.tokenY.decimal ?? null;

  return result.userPositions.map((position: any) => {
    const data = position.positionData;
    return {
      source: "meteora-sdk",
      observed_at: observedAt,
      pool_address: poolAddress,
      owner: ownerAddress,
      position_address: position.publicKey.toString(),
      lower_bin_id: asNumber(data.lowerBinId, "lowerBinId"),
      upper_bin_id: asNumber(data.upperBinId, "upperBinId"),
      total_x_amount_raw: asString(data.totalXAmount),
      total_y_amount_raw: asString(data.totalYAmount),
      fee_x_raw: asString(data.feeX),
      fee_y_raw: asString(data.feeY),
      total_claimed_fee_x_raw: asString(data.totalClaimedFeeXAmount),
      total_claimed_fee_y_raw: asString(data.totalClaimedFeeYAmount),
      token_x_decimals: tokenXDecimals,
      token_y_decimals: tokenYDecimals,
    };
  });
}
