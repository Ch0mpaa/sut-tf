# SUT-TF

TensorFold fork for long-context retrieval accuracy on a single 24 GB GPU.

Phase 1 of the broader **ScrewDrive** engine project. SUT-TF is the fork;
ScrewDrive is the eventual standalone multi-backend engine that will replace it.
They are separate deliverables and will not be conflated.

## Scope (Phase 1)

> Measure context capacity, throughput, VRAM, and accuracy when retrieving
> specific evidence from long HTTP logs, JavaScript bundles, and API
> documentation. Then test one KV-cache modification. If it produces a
> measurable improvement, publish the findings. If it doesn't, publish what we
> learned.

Verbatim from the project owner. See `docs/SCOPE.md`.

Until we've built something that demonstrably improves performance or accuracy,
we haven't earned the right to call it a better engine.

## Lineage

- Upstream: [`ashhart/TensorFold`](https://github.com/ashhart/TensorFold) (Apache-2.0)
- Immediate base: `machinegenieorg/TensorFold` with PR #836 (canonical Qwen CUDA
  base, incorporates CanadaApollo6's 3090 kernel stack formerly branded "M3TiS")
- License: Apache-2.0 inherited

See `docs/LINEAGE.md` for exact commits and attribution.

## Status

Scaffolding only. No source code imported yet, no modifications made, no
benchmarks run. Nothing here is faster or more accurate than upstream TensorFold.

## Repo layout

```
docs/          Scope, lineage, measurement protocol, baseline numbers
benchmarks/    Test harness, corpora generators, needle definitions, results
docker/        CUDA + Zig dev container (built on aipwnlocal LXC 110)
engine/        Reserved for the imported + patched TF source
```

## Reproducing anything here

Instructions will land as each stage ships. Nothing to reproduce yet.
