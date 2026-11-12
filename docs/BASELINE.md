# Baseline measurements

Empty. No baseline has been run.

When populated, this file holds the "floor" numbers against which any SUT-TF
modification is measured. Two baseline configs:

## Baseline A — stock TensorFold native

| Field | Value |
|---|---|
| Binary | `tensorfold-native 1.1.6` |
| Model | Qwen3.8-27B MLX 4-bit (MTP draft head) |
| Hardware | RTX 3090 24 GB, driver 615.71.09, CUDA 13.4 UMD |
| Host | ailab 192.168.60.222, GPU 0 |
| KV precision | fp8 |
| Max context | 180 000 tokens @ parallel=1 (empirical, 2026-11-11, with reserve=0.5 GiB) |
| Tok/s (decode) | 43.85 at 24-token prompt (anecdotal, pre-benchmark) |

## Baseline B — TensorFold + PR #836 ("M3TiS parity")

| Field | Value |
|---|---|
| Binary | Built from `machinegenieorg/TensorFold` + PR #836 |
| Model | Same |
| Hardware | Same card, different GPU index (GPU 1 on ailab) |
| KV precision | 4-bit default (`TF_QWEN27_KV_BITS=4`, M3TiS default) |
| Max context | Expected ~262K per CanadaApollo6 HF card; to be verified |
| Tok/s (decode) | Expected ~200 per PR #4 numbers; to be verified |
| Prefill at 192K | Expected `TF_QWEN27_PROMPT_ROWS=1024` + `TF_QWEN27_HOST_EMBED=1` behavior |

## Measurement run status

- [ ] A: stock TF baseline collected
- [ ] B: PR #836 build complete
- [ ] B: PR #836 baseline collected
- [ ] One KV modification designed
- [ ] One KV modification implemented
- [ ] Post-mod run against the same corpus matrix
- [ ] Publish
