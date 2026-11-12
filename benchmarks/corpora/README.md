# corpora/

Three synthesizers, three sizes-families. All corpora are generated so runs are
reproducible from a seed. Real-world samples are swapped in later if the
synthetic corpora turn out to be too easy (perfect recall even on stock) or
too hard (zero recall across the board, no signal to attribute).

## Synthesizers

- `generate_http_logs.py` — nginx access + error log lines, realistic timestamps,
  mixed status codes, realistic user agents, with the embedded needle lines
  distributed at the requested depths
- `generate_bundles.py` — a webpack-style minified JS bundle with runtime
  chunks and source map references; needles embedded as variable values and
  string literals
- `generate_apidocs.py` — a mixed Markdown + JSON OpenAPI 3 document;
  needles embedded as endpoint descriptions and example values

## Sizes

Token counts are measured by the Qwen3.8 tokenizer (fallback: GPT-2 BPE).
Targets: 4096, 16384, 65536, 131072, 180000 tokens for the Phase 1 matrix.

A 262144-token tier is added once PR #836 baseline is up and the ceiling is
verified.

## Seeding

Every synthesizer takes `--seed`. The run tag (`-- tag baseline-A`, etc.) is
not the seed — seeds are fixed per corpus in `config.yaml` so stock TF and
SUT-TF see the same corpora byte-for-byte.
