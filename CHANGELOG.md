# Changelog

Newest first. The engine changes ship as a patch file, and every file the patch adds or modifies carries a change
notice, as Apache-2.0 §4(b) requires.

## 2026-11-13: offsec recipe v1

- **Engine patch** (`patches/0001-…`):
  - Prompt cache with resumable prefill on a fixed chunk grid.
  - Pinned-RAM cache tier (`TF_QWEN27_HOST_CACHE_GIB`).
  - Forced prompt matmuls on resumed reads, so cached answers match cold ones bit for bit.
- **Serving config** (`configs/offsec.conf`): 262K window, 4-bit KV, block drafter, loop guard, 48 GiB RAM cache.
- **Offsec benchmark v2** (`benchmarks/offsec_bench_v2.py`):
  - Planted evidence with decoys, hallucination traps, a 20-question drift session, refusal checks, and power
    sampling.
  - Also in `benchmarks/`: a step runner, a table builder, and a cache exactness gate.
- **Tools** (`tools/`): converter for the abliterated weights into the engine's 4-bit layout, plus a correlation
  check for the conversion.
- **Results** (`benchmarks/results/2026-11-13-offsec-v2/`):
  - Follow-up questions: 1.2–3.3 s instead of 28–448 s.
  - Accuracy: 23/24 findings, 16/16 traps, 18/20 in the drift session.
  - 0/3 refusals.
  - 10/10 cached answers identical to cold.
  - All at 250 W.
