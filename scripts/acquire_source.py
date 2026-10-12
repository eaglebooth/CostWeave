from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, requests

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts/cost_weave.py"
tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
safe_imports = {"html", "json", "re", "typing"}
keep = [n for n in tree.body if (isinstance(n, ast.Import) and any(a.name in safe_imports for a in n.names)) or
        (isinstance(n, ast.FunctionDef) and n.name in {"canonical", "strip_xml", "parse_ecfr"})]
ns = {}; exec(compile(ast.Module(body=keep, type_ignores=[]), str(SOURCE), "exec"), ns)
date = "2026-10-08"
url = f"https://www.ecfr.gov/api/versioner/v1/full/{date}/title-2.xml?part=200&section=200.403"
response = requests.get(url, timeout=30, allow_redirects=False, headers={"User-Agent": "CostWeave-evidence/1"})
response.raise_for_status()
if response.url != url: raise SystemExit("redirect rejected")
if "xml" not in response.headers.get("Content-Type", "").lower(): raise SystemExit("non-XML content type rejected")
record = ns["parse_ecfr"](response.content)
out = ROOT / "samples/ecfr"; out.mkdir(parents=True, exist_ok=True)
(out / "2-CFR-200.403-2026-10-08.xml").write_bytes(response.content)
(out / "2-CFR-200.403-2026-10-08.canonical.json").write_text(ns["canonical"](record) + "\n", encoding="utf-8")
manifest = {"resource_id":"ecfr-2-cfr-200-403-2026-10-08","purpose_class":"positive_authoritative_source",
 "purpose":"Point-in-time general cost declaration criteria","canonical_origin":"https://www.ecfr.gov",
 "authoritative_owner":"Office of the Federal Register / eCFR","authority":"Electronic Code of Federal Regulations (authoritative but unofficial)",
 "repository_and_object_id":"ecfr.gov API; title 2; part 200; section 200.403","object_id":"2 CFR 200.403",
 "source_revision":"2026-10-08","url":url,"content_type":response.headers.get("Content-Type"),
 "retrieved_at":datetime.now(timezone.utc).isoformat(),"availability_checked_at":datetime.now(timezone.utc).isoformat(),
 "mutability":"point-in-time dated endpoint","digest_algorithm":"SHA-256 over raw bytes and SHA-256 over canonical ASCII JSON",
 "raw_sha256":hashlib.sha256(response.content).hexdigest(),
 "canonical_sha256":hashlib.sha256(ns["canonical"](record).encode()).hexdigest(),
 "predeclared_facts":{"citation":"2 CFR 200.403","criteria_keys":list("abcdefgh")},
 "expected_result":"parser accepts exact section and eight criteria",
 "cannot_prove":["actual expense facts","award-specific restrictions","accounting records","legal allowability","payment"]}
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs/TEST_RESOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2)+"\n",encoding="utf-8")
print(json.dumps(manifest, indent=2))

