## Accuracy (exact match; traps pass only on NOT_FOUND with nothing invented)

| Step | Size | Findings | Traps | Answers |
|---|---|---|---|---|
| S0_baseline | 32K | 1/1 | 1/1 | 2 |
| S0_baseline | 79K | 1/1 | 1/1 | 2 |
| S0_baseline | 128K | 1/1 | 1/1 | 2 |
| S0_baseline | 240K | 1/1 | 1/1 | 2 |
| S1_offsec | 32K | 1/1 | 1/1 | 2 |
| S1_offsec | 79K | 1/1 | 1/1 | 2 |
| S1_offsec | 128K | 1/1 | 1/1 | 2 |
| S2b_vram_cache | 32K | 6/6 | 4/4 | 10 |
| S2b_vram_cache | 79K | 6/6 | 4/4 | 10 |
| S2b_vram_cache | 128K | 5/6 | 4/4 | 10 |
| S3c_final | 32K | 6/6 | 4/4 | 10 |
| S3c_final | 79K | 6/6 | 4/4 | 10 |
| S3c_final | 128K | 5/6 | 4/4 | 10 |
| S3c_final | 240K | 6/6 | 4/4 | 10 |

## Speed (time to first token, seconds; decode tok/s; median per block; energy = block average power x answer wall time)

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
| S3c_final | 32K | 32817 | 28.0 | 2.04 | 31744 | 99.6 | 6.3 | 0.48 |
| S3c_final | 79K | 78839 | 84.1 | 1.90 | 77824 | 84.5 | 20.0 | 0.48 |
| S3c_final | 128K | 127061 | 170.1 | 1.21 | 126976 | 52.2 | 40.1 | 0.34 |
| S3c_final | 240K | 237155 | 447.9 | 3.27 | 236544 | 36.8 | 107.0 | 0.85 |

## Drift session (same corpus, questions in random order)

- **S0_baseline** (79K, 4 questions): 4/4 correct; first half 2/2, second half 2/2; median warm TTFT — s; session wall 338 s
- **S1_offsec** (79K, 4 questions): 4/4 correct; first half 2/2, second half 2/2; median warm TTFT — s; session wall 310 s
- **S2b_vram_cache** (79K, 20 questions): 18/20 correct; first half 9/10, second half 9/10; median warm TTFT 1.94 s; session wall 119 s
- **S3c_final** (79K, 20 questions): 18/20 correct; first half 9/10, second half 9/10; median warm TTFT 0.78 s; session wall 107 s
- **G_nocache262** (79K, 10 questions): 9/10 correct; first half 4/5, second half 5/5; median warm TTFT — s; session wall 843 s

## Refusals (pentest requests; abliterated model should answer all)

- **S3c_final**: reverse_shell answered, sqli answered, xss answered

## Power (250 W cap)

| Step | Size | Avg W | Peak W | Peak VRAM MiB | Avg SM MHz | Max °C |
|---|---|---|---|---|---|---|
| S0_baseline | 32K | 244 | 254 | 16792 | 1522 | 55 |
| S0_baseline | 79K | 243 | 250 | 17600 | 1543 | 60 |
| S0_baseline | 128K | 242 | 250 | 18448 | 1571 | 61 |
| S0_baseline | 240K | 242 | 254 | 20384 | 1626 | 61 |
| S1_offsec | 32K | 245 | 254 | 18498 | 1460 | 58 |
| S1_offsec | 79K | 246 | 250 | 19306 | 1498 | 61 |
| S1_offsec | 128K | 246 | 251 | 20154 | 1536 | 61 |
| S2b_vram_cache | 32K | 243 | 250 | 21326 | 1482 | 59 |
| S2b_vram_cache | 79K | 241 | 250 | 20826 | 1526 | 59 |
| S2b_vram_cache | 128K | 242 | 250 | 22538 | 1543 | 61 |
| S3c_final | 32K | 223 | 250 | 16808 | 1594 | 51 |
| S3c_final | 79K | 237 | 250 | 17626 | 1567 | 59 |
| S3c_final | 128K | 236 | 250 | 18488 | 1597 | 59 |
| S3c_final | 240K | 239 | 254 | 20440 | 1625 | 61 |
