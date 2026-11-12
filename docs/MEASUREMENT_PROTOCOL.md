# Measurement protocol

What we measure, why, and how. If this document is wrong, the benchmark harness
is wrong. If this document is incomplete, numbers in `benchmarks/results/` are
not comparable across runs.

## The four metrics

### 1. Context capacity

The largest `--context` value the engine will accept without exiting on the
"CUDA memory budget" error, holding `parallel=1`. Reported in tokens. Determined
empirically by binary search around the reserve-adjusted ceiling the engine
reports in its OOM message.

### 2. Throughput

Two numbers, both measured on the same completion:

- **Prefill time (s):** wall-clock from request send to first token.
  `tensorfold` exposes `prefill_seconds` in the response payload — we use that
  as the ground truth and cross-check with HTTP timing.
- **Decode throughput (tok/s):** `tokens_per_second` from the response payload.

Both measured at a set of prompt sizes: 1k, 4k, 16k, 64k, 128k, max-context.

### 3. VRAM

- **Idle VRAM after weight load (MiB):** `nvidia-smi` sampled 10 seconds after
  `serving` is logged, with no active requests.
- **Peak VRAM during a max-context prefill (MiB):** `nvidia-smi dmon` sampled
  at 500 ms intervals for the duration of the longest prompt in the run.

Reported per endpoint. Attributable to weights + KV + scratch.

### 4. Accuracy

The core Phase 1 metric. Needle-in-haystack retention across three corpora.

For each (corpus, context_size, needle_type, needle_position) cell:

1. A corpus is generated with embedded "needles" — specific tokens whose exact
   values we'll ask the model to retrieve.
2. The prompt wraps the corpus with an instruction: "The following log/bundle/
   doc contains a request from IP address X. State X exactly." (Phrasing
   varies by needle type.)
3. The model's response is parsed for the needle value.
4. **Score:** exact-match (1 or 0) per attempt. Report accuracy as mean across
   `N` trials per cell, with 95% CI (Wilson binomial).

### Needle types

- **IP address** (`10.42.7.113`) — looks like infra tokens
- **CVE identifier** (`CVE-2024-38063`) — fixed shape, numeric heavy
- **Port number** (`:49651`) — short, bare integer
- **Cookie / session ID** (`session=f7c3a8d1e2b94f`) — hex blob
- **HTTP header value** (`X-Request-ID: 8f2a-9c1e-...`) — structured string
- **File path** (`/var/log/auth.log.2026-11-04.gz`) — path separators, dates
- **API endpoint** (`POST /v2/users/{id}/permissions`) — method + URL + templating

### Needle positions

Within each context size, needles are placed at `{10%, 50%, 90%}` depth.
Position matters: blanket KV quantization tends to degrade middle-depth recall
more than ends.

## Corpora

Three, per owner scope:

1. **HTTP logs** — nginx-style access + error logs, mixed 2xx/4xx/5xx
2. **JavaScript bundles** — a representative webpack output: minified code,
   source map references, runtime chunks
3. **API documentation** — OpenAPI 3 / Swagger JSON, mixed with Markdown prose

Each corpus comes in multiple sizes: 4k, 16k, 64k, 128k, 180k, 262k tokens.
See `benchmarks/corpora/README.md` for how we generate / source them.

## Reporting

Each measurement run writes two artifacts under `benchmarks/results/<date>-<tag>/`:

- `run.json` — one JSON object per (endpoint, corpus, context_size, needle,
  position) trial, with the metric values and the full response payload's
  telemetry
- `report.md` — human-readable summary with tables and inline charts

Both get committed. The raw `nvidia-smi` dmon samples go under
`benchmarks/results/<date>-<tag>/vram/` as CSV.
