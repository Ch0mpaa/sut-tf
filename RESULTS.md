# Results — 2026-11-13

**Setup:**

- **Card:** one RTX 3090 at a 250 W cap (driver 615.71.09, PCIe Gen4). Nothing else ran on the card during the
  benchmark.
- **Model:** abliterated Qwen3.8-27B at 4 bits, built as in [RECIPE.md](RECIPE.md) step 3.
- **Engine builds:** S3c_final and G_nocache262 ran on the published patch (md5
  `ea0c7cefc8975ceabe1174366de7daef`). S0–S2b ran on the build before the fix described under "The bug the benchmark
  caught" (`0e208d7a…`). That fix only touches resumed reads, so the cold numbers are unaffected.
- **Decoding:** greedy (temperature 0), thinking off, one stream.
- **Page cache:** dropped before each step, so every server start read the weights from disk.

Raw receipts are in [`benchmarks/results/2026-11-13-offsec-v2/`](benchmarks/results/2026-11-13-offsec-v2/), and
[docs/METHOD.md](docs/METHOD.md) explains what each test does.

## The steps

| Step | What changed | Window |
|---|---|---|
| S0_baseline | 4-bit KV, block drafter, no prompt cache | 262K |
| S1_offsec | 131K window (4096-row prompt chunks instead of 1024), loop guard | 131K |
| S2b_vram_cache | S1 plus our prompt cache in leftover VRAM | 131K |
| **S3c_final** | **262K window, loop guard, prompt cache in 48 GiB of pinned RAM** | **262K** |
| G_nocache262 | S3c with the cache off. These are the cold answers the exactness gate compares against. | 262K |

S0 and S1 are sample runs: one finding and one trap per size, plus a 4-question session. They sent the corpus and the
question in a single message. S2b, S3c and G sent the corpus as the system message (see METHOD.md).

## Speed

Times are seconds to first token. Warm means the corpus prompt state came from the cache. Energy per answer is the
block's average power times the answer's wall time.

| Step | Size | Prompt tokens | Cold TTFT | Warm TTFT | Cached tokens | Decode tok/s | Cold kJ / answer | Warm kJ / answer |
|---|---|---|---|---|---|---|---|---|
| S0_baseline | 32K | 32813 | 27.1 | — | 0 | 112.5 | 6.7 | — |
| S0_baseline | 79K | 78835 | 82.8 | — | 0 | 89.1 | 20.2 | — |
| S0_baseline | 128K | 127057 | 166.5 | — | 0 | 63.6 | 40.4 | — |
| S0_baseline | 240K | 237151 | 443.6 | — | 0 | 34.1 | 107.5 | — |
| S1_offsec | 32K | 32813 | 25.4 | — | 0 | 111.2 | 6.2 | — |
| S1_offsec | 79K | 78835 | 77.2 | — | 0 | 84.5 | 19.0 | — |
| S1_offsec | 128K | 127057 | 152.5 | — | 0 | 61.4 | 37.5 | — |
| S2b_vram_cache | 32K | 32817 | 25.1 | 3.94 | 28672 | 90.2 | 6.1 | 0.98 |
| S2b_vram_cache | 79K | 78839 | 76.1 | 1.84 | 77824 | 83.8 | 18.4 | 0.48 |
| S2b_vram_cache | 128K | 127061 | 149.9 | 1.10 | 126976 | 56.8 | 36.3 | 0.32 |
| **S3c_final** | 32K | 32817 | 28.0 | **2.04** | 31744 | 99.6 | 6.3 | **0.48** |
| **S3c_final** | 79K | 78839 | 84.1 | **1.90** | 77824 | 84.5 | 20.0 | **0.48** |
| **S3c_final** | 128K | 127061 | 170.1 | **1.21** | 126976 | 52.2 | 40.1 | **0.34** |
| **S3c_final** | 240K | 237155 | 447.9 | **3.27** | 236544 | 36.8 | 107.0 | **0.85** |

What the steps show:

- **S0 → S1.** The 131K window reads cold prompts 6–8% faster, because the engine uses bigger prompt chunks below
  128K. The loop guard costs nothing measurable.
- **S1 → S2b.** The prompt cache turns every follow-up from a full re-read into a 1–4 s wait. But leftover VRAM at 131K
  only holds about one 79K prompt state, and at 262K nothing is left over at all.
- **S2b → S3c.** Pinned RAM gives back the full 262K window and the cache at every size, including a 237K-token dump.
  Cold reads cost the 1024-row chunk penalty again. That's the price of the window, paid once per dump.
- **Decode speed** comes from the block drafter: 37–100 tok/s here, depending on context length. On a short chat test
  the same day, the drafter took greedy decode from 41 to 107 tok/s on this card with identical output.

### The 20-question session

One 79K-token dump, then 20 questions in random order:

| | Questions | Wall time |
|---|---|---|
| S3c_final (cache) | 20 | **107 s**: the first question cold (86 s), the other 19 at a median 0.78 s to first token |
| G_nocache262 (no cache) | 10 | 843 s, every question a full re-read |

## Accuracy

Findings are scored by exact match, with decoys planted next to each answer. A trap is a question whose answer isn't
in the corpus. It passes only if the reply is NOT_FOUND and contains no IP address or CVE.

| Step | Size | Findings | Traps |
|---|---|---|---|
| **S3c_final** | 32K | 6/6 | 4/4 |
| **S3c_final** | 79K | 6/6 | 4/4 |
| **S3c_final** | 128K | 5/6 | 4/4 |
| **S3c_final** | 240K | 6/6 | 4/4 |
| S2b_vram_cache | 32K / 79K / 128K | 6/6, 6/6, 5/6 | 4/4 each |
| S0, S1 (sampled) | every size | 1/1 each | 1/1 each |

**Total for S3c: 23/24 findings, 16/16 traps.** The model never made up a host, a password, a CVE or an FTP server.

### Drift

Twenty questions on the same 79K dump, each of the 10 asked twice, in shuffled order:

- S3c_final: **18/20**. 9/10 in the first half, 9/10 in the second.
- S2b_vram_cache: 18/20, same split.
- G_nocache262: 9/10, the same SMB miss.

Accuracy didn't fall off as the session went on. Both misses are the same question, answered the same way both times.

### The misses

- **128K, live API key.** The corpus has three keys:
  - the live key, used in a request that got a 200;
  - a near-copy that differs in its last three characters, used in a request that got a 401;
  - a test key.

  At 128K the model returned the near-copy. With the cache off it gives the identical wrong answer, so this is a model
  error, not a cache error.
- **79K, SMB hosts.** Asked for every host with 445/tcp open, the model listed 9 of the 10 and invented none. Six
  hosts in the corpus have only 139/tcp open as decoys, and it skipped all of them. The cache-on and cache-off answers
  are the same.

## Refusals

The model is abliterated. All three pentest asks got working answers: a Python reverse shell, a UNION-based SQL
injection payload, and five XSS filter bypasses. **0/3 refused.**

## Cache exactness

Every cached answer in the S3c session is compared token for token (by hash) against the cold answer to the same
question from G_nocache262:

```
GATE PASS (10 distinct cached answers checked)
```

The full table is in `exactness_gate.txt`.

### The bug the benchmark caught

The first full run failed this gate at 262K: one cached SMB answer differed from the cold one. The engine was handling
a short resumed piece of prompt (78 rows) with its decode matmuls, which it uses for anything up to 192 rows. A cold
read never takes that path for those rows. The arithmetic order changes slightly, and with 4-bit KV that was enough to
flip a token.

With `TF_QWEN27_PROMPT_DENSE_ROWS=0` the answers matched. The patch now forces prompt matmuls during resumed reads.
S3c_final and the gate were then run on the fixed build, and the 10-question gate passed at 262K.

## Power

| Step | Size | Avg W | Peak W | Peak VRAM MiB | Avg SM MHz | Max °C |
|---|---|---|---|---|---|---|
| S0_baseline | 32K–240K | 242–244 | 254 | 16792–20384 | 1522–1626 | 61 |
| S1_offsec | 32K–128K | 245–246 | 254 | 18498–20154 | 1460–1536 | 61 |
| S2b_vram_cache | 32K–128K | 241–243 | 250 | 20826–22538 | 1482–1543 | 61 |
| **S3c_final** | 32K | 223 | 250 | 16808 | 1594 | 51 |
| **S3c_final** | 79K | 237 | 250 | 17626 | 1567 | 59 |
| **S3c_final** | 128K | 236 | 250 | 18488 | 1597 | 59 |
| **S3c_final** | 240K | 239 | 254 | 20440 | 1625 | 61 |

The 250 W cap holds; the 254 W peaks are single 250 ms samples. The S3c blocks average lower because most of their time
is short warm answers instead of long prompt reads. Moving the cache to RAM also frees about 2–4 GB of VRAM compared
with S2b.

## Not measured here

- More than one stream. A 262K window takes the whole card.
- Other GPUs. The patch builds for sm_86 only.
- Real engagement data. The corpora are synthetic, so the planted answers can be checked exactly. See METHOD.md.
