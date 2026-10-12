from pathlib import Path
import hashlib, json, subprocess, sys
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"docs/local-evidence"; OUT.mkdir(parents=True,exist_ok=True)
commands=[[sys.executable,"-m","pytest","-q","--tb=short","-p","no:cacheprovider","--junitxml=docs/local-evidence/pytest.xml"],
 [sys.executable,"-X","utf8","-m","genvm_linter.cli","check","contracts/cost_weave.py"],
 [sys.executable,"-X","utf8","-m","genvm_linter.cli","schema","contracts/cost_weave.py","-o","docs/schema.json"]]
results=[]
for i,cmd in enumerate(commands):
 r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",errors="replace"); log=r.stdout+r.stderr
 (OUT/f"command-{i+1}.txt").write_text(log,encoding="utf-8"); print(log); results.append({"command":cmd,"exit_code":r.returncode})
report={"scope":"LOCAL Direct Mode and SDK schema; not live consensus","checked_at":datetime.now(timezone.utc).isoformat(),
 "source_sha256":hashlib.sha256((ROOT/"contracts/cost_weave.py").read_bytes()).hexdigest(),"commands":results,"live_address":None,"live_transactions":[]}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
raise SystemExit(0 if all(x["exit_code"]==0 for x in results) else 1)
