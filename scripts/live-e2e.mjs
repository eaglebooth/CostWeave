import { mkdirSync, writeFileSync } from "node:fs";
import { createInterface } from "node:readline";
import { createAccount, createClient } from "../../CalScope/node_modules/genlayer-js/dist/index.js";
import { studionet } from "../../CalScope/node_modules/genlayer-js/dist/chains/index.js";

const CONTRACT = process.argv[2];
if (!/^0x[0-9a-fA-F]{40}$/.test(CONTRACT || "")) throw new Error("Usage: node scripts/live-e2e.mjs <contract-address> [run-id]");
const run = process.argv[3] || Date.now().toString().slice(-10);
const DIGEST = "649504d4ff4c3d1d57893b4fe7b68937239b22f65c16e23c9349c870eee96947";
const DATE = "2026-10-08";

async function readKeys() {
  const rl = createInterface({ input: process.stdin, terminal: false });
  const lines = [];
  return await new Promise((resolve, reject) => {
    rl.on("line", line => {
      const value = line.trim().replace(/^0x/, "");
      if (value) lines.push(value);
      if (lines.length === 2) { rl.close(); resolve(lines); }
    });
    rl.on("close", () => { if (lines.length < 2) reject(new Error("Two auxiliary keys required on stdin")); });
  });
}

const [keyA, keyB] = await readKeys();
const walletA = createAccount(`0x${keyA}`);
const walletB = createAccount(`0x${keyB}`);
const clientA = createClient({ chain: studionet, account: walletA });
const clientB = createClient({ chain: studionet, account: walletB });
const report = { contract: CONTRACT, network: "GenLayer StudioNet 61999", run,
  actors: { owner: walletA.address, reviewer_consumer: walletB.address }, source: { effective_date: DATE, canonical_sha256: DIGEST },
  transactions: [], assertions: [], final: {} };
mkdirSync("docs/live-evidence", { recursive: true });
const path = `docs/live-evidence/studionet-${run}.json`;
const save = () => writeFileSync(path, `${JSON.stringify(report, null, 2)}\n`);
const check = (condition, label, details = {}) => { report.assertions.push({ label, pass: Boolean(condition), details }); save(); if (!condition) throw new Error(`Assertion failed: ${label}`); };
const read = async (method, args = []) => JSON.parse(await clientA.readContract({ address: CONTRACT, functionName: method, args }));
const execution = tx => {
  const validators = tx.consensus_data?.validators || [];
  if (validators.some(v => v.vote === "agree" && v.execution_result === "SUCCESS")) return "SUCCESS";
  if (validators.some(v => v.vote === "agree" && v.execution_result === "ERROR")) return "ERROR";
  const leader = tx.consensus_data?.leader_receipt?.[0]?.genvm_result;
  return leader && !leader.error_code ? "SUCCESS" : leader?.error_code ? "ERROR" : "UNKNOWN";
};
const write = async (label, client, method, args, expected = "SUCCESS", stateId = null) => {
  const before = stateId ? await read("get_batch", [stateId]).catch(() => null) : null;
  const hash = await client.writeContract({ address: CONTRACT, functionName: method, args, value: 0n });
  process.stdout.write(`${label}: ${hash}\n`);
  let tx = {};
  for (let i = 0; i < 360; i++) {
    try { tx = await client.getTransaction({ hash }); } catch { await new Promise(r => setTimeout(r, 2500)); continue; }
    if (["FINALIZED", "CANCELED", "UNDETERMINED"].includes(tx.statusName)) break;
    await new Promise(r => setTimeout(r, 2500));
  }
  const actual = execution(tx);
  const after = stateId ? await read("get_batch", [stateId]).catch(() => null) : null;
  report.transactions.push({ label, method, args, expected, hash, status: tx.statusName || "UNKNOWN", execution: actual, before, after, receipt: tx }); save();
  check(tx.statusName === "FINALIZED" && actual === expected, `${label} finalized with ${expected}`, { hash, status: tx.statusName, execution: actual });
  if (expected === "ERROR" && before !== null) check(JSON.stringify(before) === JSON.stringify(after), `${label} preserves exact state`, { before, after });
  return { hash, before, after };
};

const version = await read("get_version");
check(version.name === "CostWeave" && version.version === 1 && version.max_lines === 6, "deployed CostWeave V1 identity", version);
const happyLocal = `happy-${run}`;
const happyId = `${walletA.address.toLowerCase()}:${happyLocal}`;
const happyLines = [
  { line_id: "travel", amount: 100, description: "The declared USD 100 travel cost is necessary and reasonable for performance of the Federal award and is allocable only to that award." },
  { line_id: "admin", amount: 40, description: "The declared USD 40 administrative cost is consistent with policies that apply uniformly to federally-financed and other activities." }
];
await write("wallet A creates denomination-bound batch", clientA, "create_batch", [happyLocal, walletB.address, walletB.address, DATE, "USD_CENTS", JSON.stringify(happyLines)]);
let happy = await read("get_batch", [happyId]);
check(happy.owner === walletA.address.toLowerCase() && happy.denomination === "USD_CENTS" && happy.total === 140, "batch identity, denomination and total", happy);
await write("reject owner acting as reviewer", clientA, "accept_batch", [happyId, happy.snapshot_digest], "ERROR", happyId);
await write("reject wrong snapshot", clientB, "accept_batch", [happyId, "0".repeat(64)], "ERROR", happyId);
await write("wallet B accepts exact snapshot", clientB, "accept_batch", [happyId, happy.snapshot_digest], "SUCCESS", happyId);
await write("reject changed source digest", clientA, "compile_allocation", [happyId, 0, "0".repeat(64)], "ERROR", happyId);
await write("compile happy allocation", clientA, "compile_allocation", [happyId, 0, DIGEST], "SUCCESS", happyId);
happy = await read("get_batch", [happyId]);
check(happy.status === "COMPILED" && happy.source_digest === DIGEST && happy.allowable_total + happy.unallowable_total + happy.review_total === happy.total, "compiled vector conserves total", happy);
await write("reject compile generation replay", clientA, "compile_allocation", [happyId, 0, DIGEST], "ERROR", happyId);
await write("reject owner consuming reviewer capability", clientA, "consume_compilation", [happyId, 1], "ERROR", happyId);
await write("wallet B consumes compilation", clientB, "consume_compilation", [happyId, 1], "SUCCESS", happyId);
await write("reject double consumption", clientB, "consume_compilation", [happyId, 1], "ERROR", happyId);
happy = await read("get_batch", [happyId]);
check(happy.status === "CONSUMED" && happy.consumed, "single-use compilation consumed", happy);

const reviewLocal = `review-${run}`;
const reviewId = `${walletA.address.toLowerCase()}:${reviewLocal}`;
const reviewLines = [{ line_id: "unknown", amount: 25, description: "The project team entered this administrative item without further supporting facts or award-specific documentation." }];
await write("wallet A creates insufficient-evidence batch", clientA, "create_batch", [reviewLocal, walletB.address, walletB.address, DATE, "USD_CENTS", JSON.stringify(reviewLines)]);
let review = await read("get_batch", [reviewId]);
await write("wallet B accepts review batch", clientB, "accept_batch", [reviewId, review.snapshot_digest], "SUCCESS", reviewId);
await write("compile insufficient evidence", clientA, "compile_allocation", [reviewId, 0, DIGEST], "SUCCESS", reviewId);
review = await read("get_batch", [reviewId]);
check(review.status === "REVIEW_REQUIRED" && review.review_total === review.total && !review.consumed, "insufficient evidence cannot become consumable", review);
await write("reject consuming review-required result", clientB, "consume_compilation", [reviewId, 1], "ERROR", reviewId);
report.final = { version, happy, review };
save();
process.stdout.write(`Evidence: ${path}\n`);
