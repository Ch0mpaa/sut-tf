# Changelog

All notable SUT-TF changes land here, newest first. Apache-2.0 §4(b) requires
modified-file notices; this changelog tracks the per-release view.

## Unreleased

- `patches/0001-qwen27-CUDA-keep-and-resume-prompt-states-in-the-sha.patch`: prompt cache for the qwen27
  CUDA engine (M3TiS has none). Follow-up questions on a 79K-token dump answer in 1.7–2.1 s instead of
  ~77 s; a four-question offsec-v1 session takes 83 s versus 365 s for M3TiS defaults. Greedy answers are
  token-identical with the cache on and off. Results: `benchmarks/results/2026-11-13-prompt-cache/`.
- `benchmarks/offsec_bench.py`: `OFFSEC_TEMPERATURE` for greedy runs, token hashes recorded.

- `configs/offsec.conf`: the sut-offsec serving profile (131K window, 4096-row prompt chunks, loop
  guard, 4-bit KV, DFlash2). 13% less session time than M3TiS's defaults on offsec-v1, same accuracy.
  Results: `benchmarks/results/2026-11-13-offsec-v1/`.
- `benchmarks/offsec_bench.py`: offsec-v1, one recon dump and four exact-answer questions.
- `tools/ablit_to_m3tis.py`: converts YCF-AI's abliterated oQ4e MLX weights to the Vontra layout
  (f16 to bf16, 168 mixed 5/6-bit modules requantized to 4-bit g64); `tools/verify_quant_vs_ref.py`
  checks every quantized module against the reference.
- `docs/LINEAGE.md`: base is `CanadaApollo6/TensorFold@c7c3f7c8`, the M3TiS source; parity verified.

- Repository scaffold: README, LICENSE, NOTICE, SCOPE, LINEAGE, BASELINE,
  MEASUREMENT_PROTOCOL, benchmark harness skeleton, Docker builder skeleton.
- No engine source imported yet.
- No modifications yet.
- No measurements yet.
