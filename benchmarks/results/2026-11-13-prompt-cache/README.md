# Prompt cache for the qwen27 CUDA engine — 2026-11-13

Patch: `patches/0001-qwen27-CUDA-keep-and-resume-prompt-states-in-the-sha.patch`, against
`CanadaApollo6/TensorFold@c7c3f7c8` (M3TiS). Engine commit on our branch: `dab915a3`.

M3TiS's qwen27 CUDA path declared no snapshot functions, so its server ran with no prompt cache and
re-read the whole prompt on every request. The patch adds them (`families/qwen27/cuda/reuse.zig`), lets a
prompt pass resume from a kept state and stop at the cache's marks on the zero-anchored grid, and makes
`native/cuda.zig` use each family's own snapshot table. Cache-off passes take the original path.

Setup: ailab GPU 0 (RTX 3090, 250 W cap), `configs/offsec.conf` flags (131K window, loop guard, 4-bit KV,
DFlash2), abliterated Qwen3.8-27B. The server reported `a 2.9 GiB prompt cache`. Workload: offsec-v1
(`benchmarks/offsec_bench.py`, seed 4242), a ~79K-token recon dump and four questions in a row.

## Correctness gate (temperature 0)

| Question | Cache on | Cache off | |
|---|---|---|---|
| apache | `560e3525e752` (cold) | `560e3525e752` | identical |
| apikey | `6ef9ce282928` (77,824 cached) | `6ef9ce282928` | identical |
| traversal | `091d5a2969f3` (77,824 cached) | `091d5a2969f3` | identical |
| smb | `a8de0f34a25b` (77,824 cached) | `a8de0f34a25b` | identical |

Answers resumed from a kept state are token-identical to answers from a full read.

## Speed (default temperature)

| Engine / config | Correct | Session | Follow-up question |
|---|---|---|---|
| M3TiS defaults, 262K (offsec-v1, earlier run) | 4/4 | 365 s | ~84 s |
| sut-offsec v1, no cache (earlier run) | 4/4 | 318 s | ~77 s |
| **sut-offsec + prompt cache** | **4/4** | **83 s** | **1.7–2.1 s** |

The first question still reads the whole dump (~76 s); the next three resume at 77,824 tokens and read
only the last partial chunk plus the question.

## Limits

- The cache lives in leftover VRAM: 2.9 GiB at a 131K window holds about one 79K-token dump's state
  (~1.6 GB). At 262K there is too little room; a host-RAM tier is the next step.
- One session per config.
