"""Tables for offsec-bench v2 results: accuracy, hallucination traps, drift, refusals, speed, energy.
Usage: summarize_v2.py RESULTS_DIR TAG [TAG ...]"""
import json, statistics, sys

d, tags = sys.argv[1], sys.argv[2:]
R = {t: json.load(open(f"{d}/{t}.json")) for t in tags}


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt(x, nd=1, unit=""):
    return "—" if x is None else f"{x:.{nd}f}{unit}"


print("## Accuracy (exact match; traps pass only on NOT_FOUND with nothing invented)\n")
print("| Step | Size | Findings | Traps | Answers |")
print("|---|---|---|---|---|")
for t, r in R.items():
    for size, b in r["sizes"].items():
        f = [x for x in b["rows"] if x["kind"] == "find"]
        tr = [x for x in b["rows"] if x["kind"] == "trap"]
        print(f"| {t} | {int(size) // 1000}K | {sum(x['ok'] for x in f)}/{len(f)} | {sum(x['ok'] for x in tr)}/{len(tr)} | {len(b['rows'])} |")

print("\n## Speed (time to first token, seconds; decode tok/s; median per block; energy = block average power x answer wall time)\n")
print("| Step | Size | Prompt tokens | Cold TTFT | Warm TTFT | Cached tokens | Decode tok/s | Cold kJ / answer | Warm kJ / answer |")
print("|---|---|---|---|---|---|---|---|---|")
for t, r in R.items():
    for size, b in r["sizes"].items():
        rows = b["rows"]
        cold = [x["ttft"] for x in rows if not x["cached"]]
        warm = [x["ttft"] for x in rows if x["cached"]]
        w = b["power"].get("avg_w")
        kj = lambda xs: None if w is None or not xs else w * med(xs) / 1000
        print(f"| {t} | {int(size) // 1000}K | {rows[0]['prompt']} | {fmt(med(cold))} | {fmt(med(warm), 2)} | "
              f"{max(x['cached'] for x in rows)} | {fmt(med([x['tps'] for x in rows]))} | "
              f"{fmt(kj([x['wall'] for x in rows if not x['cached']]), 1)} | {fmt(kj([x['wall'] for x in rows if x['cached']]), 2)} |")

print("\n## Drift session (same corpus, questions in random order)\n")
for t, r in R.items():
    s = r.get("session")
    if not s:
        continue
    rows = s["rows"]
    half = len(rows) // 2
    first, second = rows[:half], rows[half:]
    print(f"- **{t}** ({s['size'] // 1000}K, {len(rows)} questions): {sum(x['ok'] for x in rows)}/{len(rows)} correct; "
          f"first half {sum(x['ok'] for x in first)}/{len(first)}, second half {sum(x['ok'] for x in second)}/{len(second)}; "
          f"median warm TTFT {fmt(med([x['ttft'] for x in rows if x['cached']]), 2)} s; session wall {sum(x['wall'] for x in rows):.0f} s")

print("\n## Refusals (pentest requests; abliterated model should answer all)\n")
for t, r in R.items():
    if r.get("refusals"):
        print(f"- **{t}**: " + ", ".join(f"{x['q']} {'REFUSED' if x['refused'] else 'answered'}" for x in r["refusals"]))

print("\n## Power (250 W cap)\n")
print("| Step | Size | Avg W | Peak W | Peak VRAM MiB | Avg SM MHz | Max °C |")
print("|---|---|---|---|---|---|---|")
for t, r in R.items():
    for size, b in r["sizes"].items():
        p = b["power"]
        print(f"| {t} | {int(size) // 1000}K | {fmt(p.get('avg_w'), 0)} | {fmt(p.get('peak_w'), 0)} | {fmt(p.get('peak_mib'), 0)} | {fmt(p.get('avg_sm'), 0)} | {fmt(p.get('max_temp'), 0)} |")
