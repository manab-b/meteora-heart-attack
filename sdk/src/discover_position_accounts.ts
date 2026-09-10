import { Connection, PublicKey } from "@solana/web3.js";

const DLMM_PROGRAM_ID = new PublicKey("LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo");
const POSITION_V2_DISCRIMINATOR = Buffer.from([
  117, 176, 212, 199,
  245, 180, 133, 182,
]);
const POSITION_V2_OWNER_OFFSET = 8 + 32;
const POSITION_V2_LB_PAIR_OFFSET = 8;
const POSITION_V2_HEADER_BYTES = 8 + 32 + 32;
const BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

type PositionAccount = {
  position_address: string;
  owner: string;
  pool_address: string;
};

function encodeBase58(bytes: Uint8Array): string {
  let value = BigInt(`0x${Buffer.from(bytes).toString("hex")}`);
  const digits: string[] = [];
  while (value > 0n) {
    const remainder = Number(value % 58n);
    digits.push(BASE58_ALPHABET[remainder]);
    value /= 58n;
  }
  let leadingZeros = 0;
  while (leadingZeros < bytes.length && bytes[leadingZeros] === 0) leadingZeros += 1;
  return "1".repeat(leadingZeros) + (digits.reverse().join("") || (leadingZeros ? "" : "1"));
}

function parseArgs(argv: string[]) {
  let rpcUrl = process.env.RPC_URL;
  let owner: string | undefined;
  let limit = 100;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--rpc-url") rpcUrl = argv[++i];
    else if (arg === "--owner") owner = argv[++i];
    else if (arg === "--limit") limit = Number(argv[++i]);
    else if (arg === "--once") continue;
    else throw new Error(`unknown argument: ${arg}`);
  }

  if (!rpcUrl) throw new Error("RPC_URL or --rpc-url is required");
  if (!Number.isInteger(limit) || limit < 1) throw new Error("--limit must be a positive integer");
  if (owner) new PublicKey(owner);
  return { rpcUrl, owner, limit };
}

async function main() {
  const { rpcUrl, owner, limit } = parseArgs(process.argv.slice(2));
  const connection = new Connection(rpcUrl, "confirmed");
  const filters: any[] = [
    { memcmp: { offset: 0, bytes: encodeBase58(POSITION_V2_DISCRIMINATOR) } },
  ];
  if (owner) {
    filters.push({ memcmp: { offset: POSITION_V2_OWNER_OFFSET, bytes: owner } });
  }

  const accounts = await connection.getProgramAccounts(DLMM_PROGRAM_ID, {
    filters,
    dataSlice: { offset: 0, length: POSITION_V2_HEADER_BYTES },
  });

  const positions: PositionAccount[] = [];
  for (const account of accounts.slice(0, limit)) {
    const data = Buffer.from(account.account.data);
    if (data.length < POSITION_V2_HEADER_BYTES) continue;
    const poolAddress = new PublicKey(data.subarray(POSITION_V2_LB_PAIR_OFFSET, POSITION_V2_OWNER_OFFSET)).toBase58();
    const ownerAddress = new PublicKey(data.subarray(POSITION_V2_OWNER_OFFSET, POSITION_V2_HEADER_BYTES)).toBase58();
    positions.push({
      position_address: account.pubkey.toBase58(),
      owner: ownerAddress,
      pool_address: poolAddress,
    });
  }

  const ownerCounts = new Map<string, number>();
  for (const position of positions) ownerCounts.set(position.owner, (ownerCounts.get(position.owner) ?? 0) + 1);

  console.log(JSON.stringify({
    source: "solana-rpc",
    observed_at: new Date().toISOString(),
    program_id: DLMM_PROGRAM_ID.toBase58(),
    position_accounts_found: accounts.length,
    positions_returned: positions.length,
    owner_filter: owner ?? null,
    owners: Array.from(ownerCounts.entries()).map(([wallet, position_count]) => ({ wallet, position_count })),
    positions,
  }));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
