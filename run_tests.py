"""Run every case in tests/cases.json through the FULL pipeline and save UNEDITED outputs to outputs/.

python run_tests.py                 # all cases
python run_tests.py --only con-3    # cases whose id contains this text
Outputs: outputs/<id>.md (raw report), outputs/<id>.json (case file + checks), outputs/summary.md
"""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

from src import guard, intake, kb, pipeline

ap = argparse.ArgumentParser()
ap.add_argument("--cases", default="tests/cases.json")
ap.add_argument("--out", default="outputs")
ap.add_argument("--only", default="")
ap.add_argument("--sleep", type=float, default=float(os.getenv("TEST_SLEEP", "2")), help="seconds between cases (free-tier rate limits)")
args = ap.parse_args()

Path(args.out).mkdir(parents=True, exist_ok=True)
entries = kb.load_entries()
verified, total = kb.stats()
cases = [c for c in json.load(open(args.cases, encoding="utf-8")) if args.only in c["id"]]
rows = []

for n, c in enumerate(cases):
    print(f"[{n + 1}/{len(cases)}] {c['id']} ...", flush=True)
    t0 = time.time()
    lang = intake.detect_language(c["story"])
    try:
        res = pipeline.analyze([{"role": "user", "content": c["story"]}], lang, entries)
        err = None
    except Exception as e:  # keep going; record the failure
        res, err = None, f"{type(e).__name__}: {e}"
    secs = round(time.time() - t0, 1)

    if res is None:
        Path(args.out, f"{c['id']}.md").write_text(f"RUN FAILED\n\n{err}\n", encoding="utf-8")
        rows.append(f"| {c['id']} | {c['expect_topic']} | ERROR | {lang} | - | - | - | - | FAIL (error) | {err[:80]} |")
        continue

    md = res["markdown"]
    Path(args.out, f"{c['id']}.md").write_text(md, encoding="utf-8")   # raw, unedited
    final_scan = guard.check(md, res["retrieved"])["flags"]            # sanity: nothing unsupported left in what the user sees
    flag_types = sorted({f["type"] for f in res["guard_flags"]})
    checks = {
        "topic_correct": res["case"]["topic"] == c["expect_topic"],
        "expected_risk_flags_fired": set(c["expect_risk"]) <= set(res["risk_ids"]),
        "no_unsupported_refs_in_final_text": not final_scan,
        "no_case_law_in_final_text": not any(f["type"] == "case" for f in final_scan),
    }
    Path(args.out, f"{c['id']}.json").write_text(json.dumps({
        "id": c["id"], "language_detected": lang, "seconds": secs, "case_file": res["case"], "risk_ids": res["risk_ids"],
        "confidence": res["confidence"], "kb_gap": res["kb_gap"], "kb_retrieved": res["retrieved_ids"], "kb_cited": res["cited_ids"],
        "guard_flags_removed": res["guard_flags"], "checks": checks}, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = all(checks.values())
    rows.append(f"| {c['id']} | {c['expect_topic']} | {res['case']['topic']} | {lang} | {', '.join(res['risk_ids']) or '-'} | "
                f"{len(res['retrieved_ids'])}/{len(res['cited_ids'])} | {len(res['guard_flags'])} ({', '.join(flag_types) or '-'}) | "
                f"{res['confidence']} | {'PASS' if ok else 'CHECK'} | {', '.join(k for k, v in checks.items() if not v)} |")
    time.sleep(args.sleep)

header = f"""# Test run summary
- Run at: {datetime.now():%Y-%m-%d %H:%M}
- Provider / model: {os.getenv('LLM_PROVIDER', 'gemini')} / {os.getenv('LLM_MODEL') or 'default'}
- Knowledge base: **{verified} of {total} entries verified** (dev mode: {kb.dev_mode()})
- Outputs in this folder are raw model output (not edited by hand). PASS only means the automatic checks passed; read the files.

| case | expected topic | got topic | language | lawyer-needed flags | KB retrieved/cited | guard removed (types) | confidence | auto-checks | failed checks |
|---|---|---|---|---|---|---|---|---|---|
"""
Path(args.out, "summary.md").write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
print(f"\nDone. See {args.out}/summary.md")
if verified == 0:
    print("NOTE: 0 verified KB entries, so every answer says 'not sure about the exact provision'. Verify the KB, then rerun.")
