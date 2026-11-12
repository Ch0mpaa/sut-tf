# benchmarks/

The measurement harness and its inputs.

## Layout

```
harness.py              CLI runner: hits OpenAI-compatible endpoints,
                        records tok/s, prefill, VRAM, needle accuracy
config.example.yaml     Example run config (copy to config.yaml)
needles/
  types.py              Needle generators per type (IP, CVE, port, ...)
  verify.py             Exact-match scoring + Wilson CI
corpora/
  README.md             How to produce each corpus size
  generate_http_logs.py Synthesizer for nginx-style corpora
  generate_bundles.py   Synthesizer for JS bundle corpora
  generate_apidocs.py   Synthesizer for OpenAPI corpora
results/                Per-run outputs (gitignored; commit specific runs
                        explicitly via git add -f)
```

## Running a measurement

Not usable yet. Scaffolding only. Will land as:

```
python benchmarks/harness.py --config benchmarks/config.yaml --tag baseline-A
```

See `docs/MEASUREMENT_PROTOCOL.md` for what the numbers mean.
