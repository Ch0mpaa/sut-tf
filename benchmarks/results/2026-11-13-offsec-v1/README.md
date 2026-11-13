# offsec-v1 — 2026-11-13

One synthetic recon dump (~79K tokens: `nmap -sV` output for 328 hosts + an nginx access log), four
questions asked one after another, each request carrying the full dump. Planted findings: a host running
Apache httpd 2.4.49, a leaked `sk_live_` API key, a `..%2f` traversal that got HTTP 200, and ten hosts
with 445/tcp open. Scored by exact string match (IP list: precision and recall). Generator and scorer:
`benchmarks/offsec_bench.py`, seed 4242.

All four configs ran on the same card (ailab GPU 0, RTX 3090 capped at 250 W) with the same binary (our
source build of M3TiS, `CanadaApollo6/TensorFold@c7c3f7c8`, token-identical to the release), 4-bit KV,
DFlash2 drafter, `--parallel 1`, `--no-thinking`, abliterated Qwen3.8-27B converted by
`tools/ablit_to_m3tis.py`. Requests set no temperature, so each server's default applies.

| Config | Correct | Session wall | Prompt read / question | Decode tok/s |
|---|---|---|---|---|
| M3TiS defaults (`--context 262144`) | 4/4 | 365 s | ~84 s | 124–166 |
| **sut-offsec** (`--context 131072`) | 4/4 | **318 s** | ~77 s | 128–162 |
| sut-offsec + `--loop-guard` | 4/4 | 319 s | ~77 s | 127–162 |
| sut-offsec + `--temperature 0.3` | 4/4 | 339 s | ~77 s | 121–149 |

## Findings

- Below 128K the engine reads prompts in 4096-row chunks instead of 1024, about 8% faster per prompt.
- `--loop-guard` cost nothing measurable, so the profile keeps it.
- Temperature 0.3 decoded ~8% slower and fixed nothing (1.0 was already exact), so it is out.
- **No config got a single prompt-cache hit.** This engine logs `no prompt cache` at start: the M3TiS
  qwen27 CUDA path keeps no prompt states, so every question re-reads the whole dump. That is the
  next thing to build, not to configure.

## Caveats

- One session per config. Two time-to-first-token outliers (84 s, 104 s) are most likely other clients
  on port 8000 during the run.
- sut-offsec caps context at 131K; the 262K window stays available on GPU 1.

Profile: `configs/offsec.conf`.
