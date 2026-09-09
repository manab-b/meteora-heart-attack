# SDK Read Path

The collector now has a read-only SDK path for Active Bin and nearby Bin state.

Meteora's official TypeScript SDK documents DLMM.create, getActiveBin(), and getBinsAroundActiveBin(). This project uses the SDK only for reads; it does not create transactions or sign wallets.

The Python REST collector remains the low-cost indexed-data path. The SDK path is used when Bin-level state is required.

## Usage

From sdk/ run npm install, then call readPoolBins(rpcUrl, poolAddress, 5, 5) from a Node runner.

RPC URL is supplied at runtime and is never committed to the repository.

## Data policy

Every observation stores source, observed timestamp, active bin, active-bin price, nearby bin id, nearby bin price, raw X amount, and raw Y amount.

No missing field is fabricated.
