# Phase 1 Scope

## Verbatim, from the project owner (2026-11-11)

> Measure context capacity, throughput, VRAM, and accuracy when retrieving
> specific evidence from long HTTP logs, JavaScript bundles, and API
> documentation.
>
> Then test one KV-cache modification.
>
> If it produces a measurable improvement, publish the findings. If it
> doesn't, publish what we learned.

> I don't want ScrewDrive permanently dependent on TensorFold, CUDA, or NVIDIA.
> Our long-term engine should support:
>   NVIDIA CUDA
>   AMD ROCm
>   Qualcomm QNN
>   Apple Metal
>   ARM/CPU, including Raspberry Pi
> But none of those additional backends belongs in our first deliverable.

> My decision: Level 1 now, Level 3 eventually. Level 2 only when the
> benchmarks justify it.
>
> And until we've built something that demonstrably improves performance or
> accuracy, we haven't earned the right to call it a better engine.

## What this means for this repo

- **This repo (SUT-TF) is Level 1 only.** CUDA 3090 single-backend. No ROCm,
  QNN, Metal, or CPU in this codebase. Those belong to a future ScrewDrive
  repo.
- **One** KV-cache modification. Not two, not a suite — one, so the signal is
  attributable.
- **Publish either way.** Negative results are a deliverable. A honest "this
  modification did not improve retrieval" write-up is in scope.
- **No performance claims in README, blog post, or benchmarks dir until the
  numbers exist to back them.** Until then, status is "scaffolding" or
  "measurement in progress."

## Out of scope for Phase 1

- Any additional backend (ROCm, QNN, Metal, CPU)
- Attention kernel changes
- Weight quantization changes
- Multi-model support — one model, Qwen3.8-27B MLX 4-bit
- Multi-GPU support
- Serving features (dashboard, learn/recall, voice, drafter changes)
- Marketing language in commits, PR titles, or docs that claims improvement
  before measurement
