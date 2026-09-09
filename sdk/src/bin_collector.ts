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

const connection = new Connection(rpcUrl, "confirmed");
const observations = await collectBinLiquidity(connection, poolAddress, lowerBinId, upperBinId);
for (const observation of observations) console.log(JSON.stringify(observation));
