# SUT-TF

**Screwed Up Tech's offsec inference recipe:** one RTX 3090 capped at 250 W, running an abliterated 27B model with a
262,144-token window. Recon follow-ups come back in seconds, not minutes, and the model doesn't refuse pentest work.

The point is the agent loop. You dump a big pile of recon (nmap, web logs, JS bundles, API docs) into context and
then ask question after question about it. A stock engine re-reads the whole dump on every question. Ours saves the
model state at the end of the dump into pinned host RAM and resumes from it. The resumed answers are bit-identical to
re-reading the dump.

## Headline numbers

Everything below is one RTX 3090 at a 250 W power cap, one stream, abliterated Qwen3.8-27B at 4 bits, a 262K window,
greedy decoding, and the offsec benchmark in [`benchmarks/`](benchmarks/). Full tables are in [RESULTS.md](RESULTS.md).

| Recon dump | First question (cold) | Every question after (warm) | Energy per follow-up |
|---|---|---|---|
| 32K tokens | 28.0 s | **2.0 s** | 0.48 kJ (cold: 6.3 kJ) |
| 79K tokens | 84.1 s | **1.9 s** | 0.48 kJ (cold: 20.0 kJ) |
| 128K tokens | 170.1 s | **1.2 s** | 0.34 kJ (cold: 40.1 kJ) |
| 237K tokens | 447.9 s | **3.3 s** | 0.85 kJ (cold: 107.0 kJ) |

| Check | Result |
|---|---|
| Find planted evidence among decoys | **23/24** |
| Hallucination traps: asked for things that aren't there | **16/16** answered NOT_FOUND, nothing invented |
| Drift: 20 questions in a row on one 79K dump | **18/20**, 9/10 in the first half and 9/10 in the second (no drift) |
| Cached answer equals cold re-read answer | **10/10** identical token streams |
| Pentest requests refused (reverse shell, SQLi, XSS) | **0/3** |
| Decode speed | 100 / 85 / 52 / 37 tok/s at 32K / 79K / 128K / 237K |
| Power | 223–239 W average, 254 W peak, 61 °C max |

The misses are real model errors and they repeat the same way with the cache on or off. At 128K the model picked a
near-copy of the live API key (the request that got a 401). In the drift session it twice listed 9 of the 10 SMB hosts,
dropping one and inventing none.

## What's in here

| Path | What |
|---|---|
| [RECIPE.md](RECIPE.md) | Build it yourself: engine, patch, weights, config, benchmark |
| [RESULTS.md](RESULTS.md) | Every step, every table, the misses, and the bug we caught |
| [docs/METHOD.md](docs/METHOD.md) | How the benchmark builds its corpora and scores answers |
| [patches/](patches/) | The engine patch: prompt cache, resumable prefill, pinned-RAM tier |
| [configs/offsec.conf](configs/offsec.conf) | The serving config the numbers came from |
| [tools/](tools/) | Weight conversion to the engine's 4-bit layout, plus the check that it worked |
| [benchmarks/](benchmarks/) | Offsec benchmark, step runner, table builder, exactness gate, raw results |
| [docker/](docker/) | Builder image (CUDA 12.4, Zig 0.17.0) |

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
