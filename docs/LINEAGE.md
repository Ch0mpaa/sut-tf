# Lineage

## Family tree

```
ashhart/TensorFold                       (upstream, Apache-2.0)
    |
    +-- PR #608                          (CanadaApollo6 kernel work, stacked)
    |
    +-- machinegenieorg/TensorFold       (integration fork)
        |
        +-- PR #3                        (RTX 3090 / Ampere support)
        +-- PR #4                        (qmm_lane.cu matmul,
        |                                 TF_QWEN27_KV_BITS,
        |                                 TF_QWEN27_PROMPT_ROWS,
        |                                 TF_QWEN27_HOST_EMBED;
        |                                 closed in favor of ashhart#836)
        |
        +-- ashhart PR #836              (canonical Qwen CUDA base
                                          — SUT-TF's intended base)
                |
                +-- SUT-TF (this repo)
```

## What "M3TiS" actually is

CanadaApollo6's HF model cards and the above stacked PRs. Not a separate
repository. See `docs/SCOPE.md` for why this matters and `README.md` for the
canonical references.

## Base commit

To be filled in when we import. Will record:

- Upstream source: `machinegenieorg/TensorFold@<commit>` with PR #836 merged in
- Commit hash
- Zig version used to build
- CUDA version used to build
- Driver version on target (ailab RTX 3090)

## Per-file attribution

Modified files will carry a top-of-file notice in the format required by
Apache-2.0 §4(b):

```
// Modified <YYYY-MM-DD> for SUT-TF.
// Original: TensorFold, Apache-2.0.
```

## Attribution not covered here

Weight files (`CanadaApollo6/Qwen3.8-27B-M3TiS-3090`, Vontra's MLX 4-bit
quant of Qwen3.8-27B) are downloaded from Hugging Face by the user and are not
redistributed in this repo. See benchmark harness for how we reference them.
