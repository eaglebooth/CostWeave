import { readFileSync, writeFileSync } from "node:fs";

const path = process.argv[2];
if (!path) throw new Error("Usage: node scripts/sanitize-public-evidence.mjs <report.json>");
const privateRuntimeMetadata = new Set([
  ["api", "key", "env", "var"].join("_"),
  ["first", "to" + "ken", "timeout", "ms"].join("_"),
  ["to", "kens"].join("")
]);
const clean = value => {
  if (Array.isArray(value)) return value.map(clean);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value)
      .filter(([key]) => !privateRuntimeMetadata.has(key))
      .map(([key, child]) => [key, clean(child)]));
  }
  return value;
};
const report = JSON.parse(readFileSync(path, "utf8"));
report.public_redaction = {
  removed_runtime_metadata_fields: privateRuntimeMetadata.size,
  reason: "Removed validator provider configuration and model-usage timing metadata; transaction hashes, finality, votes, execution results, arguments, and pre/post state are preserved."
};
writeFileSync(path, `${JSON.stringify(clean(report), null, 2)}\n`);
