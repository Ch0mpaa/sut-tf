# benchmarks/

| File | What |
|---|---|
| `offsec_bench_v2.py` | The offsec benchmark: planted evidence with decoys, hallucination traps, drift session, refusals, power. See [../docs/METHOD.md](../docs/METHOD.md). |
| `run_steps.sh` | Runs the benchmark once per build step, each on a fresh server, then builds the tables and runs the exactness gate |
| `summarize_v2.py` | JSON receipts → markdown tables |
| `exactness_gate.py` | Fails if any cached answer differs from the cold answer to the same question |
| `results/2026-11-13-offsec-v2/` | The receipts behind [../RESULTS.md](../RESULTS.md) |

Run one benchmark against a server that's already up (on the same host, so `nvidia-smi` sees its GPU):

```bash
python3 offsec_bench_v2.py 8000 mytag --gpu 0 --out results/mine
python3 summarize_v2.py results/mine mytag
```

Python 3.10+ with the standard library only. `nvidia-smi` must be on PATH.
