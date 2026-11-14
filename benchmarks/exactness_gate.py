"""Cache exactness gate: every cached answer's token hash must equal the cold (cache-off) answer's for the same question.
Usage: exactness_gate.py RESULTS_DIR CACHED_TAG COLD_TAG"""
import json, sys

d, cached_tag, cold_tag = sys.argv[1:4]
cached = json.load(open(f"{d}/{cached_tag}.json"))["session"]["rows"]
cold = {r["q"]: r for r in json.load(open(f"{d}/{cold_tag}.json"))["session"]["rows"]}
ok = True
print(f"{'question':10} {'cached tokens':>13} {'cached sha':>14} {'cold sha':>14}  result")
seen = set()
for r in cached:
    if not r["cached"] or r["q"] not in cold:
        continue
    same = r["sha"] == cold[r["q"]]["sha"]
    ok &= same
    tag = (r["q"], r["sha"])
    if tag in seen:
        continue
    seen.add(tag)
    print(f"{r['q']:10} {r['cached']:>13} {r['sha']:>14} {cold[r['q']]['sha']:>14}  {'IDENTICAL' if same else 'DIFFERENT'}")
print(f"GATE {'PASS' if ok else 'FAIL'} ({len(seen)} distinct cached answers checked)")
