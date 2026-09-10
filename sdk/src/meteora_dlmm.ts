import { createRequire } from "node:module";

// @meteora-ag/dlmm currently exposes its runtime class through the CommonJS
// entry point. Loading it via createRequire avoids Node 20 ESM resolution of
// Anchor's CommonJS directory imports while preserving the SDK API.
const require = createRequire(import.meta.url);

export const DLMM = require("@meteora-ag/dlmm");
