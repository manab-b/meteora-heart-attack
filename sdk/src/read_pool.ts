import DLMM from "@meteora-ag/dlmm";
import { Connection, PublicKey } from "@solana/web3.js";

export type BinSnapshot = {
  poolAddress: string;
  activeBinId: number;
  activeBinPrice: number;
  bins: Array<{
    binId: number;
    price: number;
    xAmount: string;
    yAmount: string;
  }>;
};

export async function readPoolBins(
  rpcUrl: string,
  poolAddress: string,
  left = 5,
  right = 5,
): Promise<BinSnapshot> {
  const connection = new Connection(rpcUrl, "confirmed");
  const pool = await DLMM.create(connection, new PublicKey(poolAddress), {
    cluster: "mainnet-beta",
  });

  const active = await pool.getActiveBin();
  const around = await pool.getBinsAroundActiveBin(left, right);

  return {
    poolAddress,
    activeBinId: active.binId,
    activeBinPrice: active.price,
    bins: around.bins.map((bin: any) => ({
      binId: bin.binId,
      price: bin.price,
      xAmount: String(bin.xAmount ?? "0"),
      yAmount: String(bin.yAmount ?? "0"),
    })),
  };
}
