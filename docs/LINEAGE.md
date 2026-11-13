# Lineage

## Family tree

```
ashhart/TensorFold                          upstream, Apache-2.0
    |
    +-- PR #608 (closed, unmerged)          "Qwen3.8-27B on CUDA: the qwen27 family's engine
    |                                        for NVIDIA GPUs, every stream drafted"
    |                                        head: machinegenieorg/TensorFold see-4347-qwen27-cuda
    |
    +-- CanadaApollo6/TensorFold
            branch m3tis-qwen27-3090 @ c7c3f7c8   = M3TiS (the 3090 stack on top of #608)
                |
                +-- SUT-TF (this repo)
```

Key M3TiS commits on that branch:

| Commit | What it adds |
|---|---|
| `dd06e939` | opt-in 4-bit attention cache (`TF_QWEN27_KV_BITS=4`): `kv4.cu`, `attn4` |
| `abca8c96` | one segmented launch for weights that share an input |
| `8944e7aa` | buffers sized by stream count, 262K on 24 GB, decode matmuls for short prompts |
| `c7c3f7c8` | weight tensors packed into 128 MiB blocks (~1.1 GB back) |

## What "M3TiS" is

A branch of CanadaApollo6's TensorFold fork plus a Hugging Face release
(`CanadaApollo6/Qwen3.8-27B-M3TiS-3090`) that ships a prebuilt binary, the captured sm_86 Triton glue
kernels and a launcher. The release's `SOURCE.md` names the commit above. An earlier version of this file
pointed at `ashhart` PR #836; that PR is the Windows CUDA server, not the 3090 stack.

## Base commit

- Source: `https://github.com/CanadaApollo6/TensorFold` @ `c7c3f7c8`
- Build: `zig build native -Dcpu=x86_64_v3 -Dnvcc=/usr/local/cuda/bin/nvcc -Dsm=86` in
  `docker/Dockerfile.builder` (Zig 0.17.0, CUDA 12.4.1; M3TiS's release used CUDA 13.4)
- Runtime: the release's `share/tensorfold/cuda/sm86/` glue kernels beside the binary
- Target: ailab RTX 3090, driver 615.71.09
- Parity (2026-11-13): our build and the release produced token-identical output on all 20
  community-v2 samples (greedy and sampled), with the same VRAM, and the same speed on the same card
  (chat greedy 124.9 vs 124.5 tok/s)

## Per-file attribution

Modified files will carry a top-of-file notice in the format required by Apache-2.0 §4(b):

```
// Modified <YYYY-MM-DD> for SUT-TF.
// Original: TensorFold, Apache-2.0.
```

## Not redistributed here

Weights (huihui-ai's abliteration via `YCF-AI/Qwen3.8-27B-Huihui-abliterated-oQ4e-MTP-FP16-MLX`,
`Vontra/Qwen3.8-27B-MLX-4bit`, `z-lab/Qwen3.8-27B-DFlash2`) and the M3TiS release are downloaded by the
user. `tools/ablit_to_m3tis.py` converts the abliterated checkpoint into the layout the engine loads.
