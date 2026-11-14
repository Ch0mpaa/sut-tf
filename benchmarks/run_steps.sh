#!/usr/bin/env bash
# Run the offsec benchmark once per build step on one GPU, starting a fresh server for each step.
# Run it on the GPU host, with nothing else on that GPU. Set BIN, MODEL and GPU first.
#   BIN=/opt/sut-tf/bin/tensorfold-native MODEL=/srv/models/qwen38-27b-abliterated-4bit GPU=0 ./run_steps.sh
# Steps:
#   S0_baseline     4-bit KV + drafter, 262K window, no prompt cache
#   S1_offsec       131K window (larger prompt chunks) + loop guard, no prompt cache
#   S2b_vram_cache  S1 + prompt cache in leftover VRAM
#   S3c_final       262K window + loop guard + 48 GiB pinned-RAM prompt cache
#   G_nocache262    S3c with the cache off: the cold answers the exactness gate compares against
# Dropping the page cache between steps needs root; set DROP_CACHES=1 to have it run `sudo` for that.
set -euo pipefail
: "${BIN:?set BIN}" "${MODEL:?set MODEL}"
GPU=${GPU:-0}
PORT=${PORT:-8010}
OUT=${OUT:-results/$(date +%F)-offsec-v2}
HERE=$(cd "$(dirname "$0")" && pwd)
BASE="--host 127.0.0.1 --port $PORT --name redops-abliterated --backend cuda --parallel 1 --drafter z-lab/Qwen3.8-27B-DFlash2 --no-thinking --no-update-check"
mkdir -p "$OUT"
md5sum "$BIN" | awk '{print $1 "  tensorfold-native"}' > "$OUT/binary.md5"
nvidia-smi -i "$GPU" --query-gpu=name,power.limit,driver_version,pcie.link.gen.max --format=csv,noheader | tee "$OUT/gpu.txt"

step() {  # tag env flags bench-args
  local tag=$1 env=$2 flags=$3 bench=$4
  echo "##### $tag  [$env $flags]  $(date +%T)"
  [ "${DROP_CACHES:-0}" = 1 ] && { sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null; }
  env CUDA_VISIBLE_DEVICES="$GPU" TF_QWEN27_KV_BITS=4 $env "$BIN" serve $BASE $flags "$MODEL" > "$OUT/$tag.serve.log" 2>&1 &
  local pid=$!
  for _ in $(seq 1 100); do curl -sf -m 2 -o /dev/null "http://127.0.0.1:$PORT/v1/models" && break; sleep 3; done
  eval python3 -u "$HERE/offsec_bench_v2.py" "$PORT" "$tag" --gpu "$GPU" --out "$OUT" $bench
  kill "$pid"; wait "$pid" 2>/dev/null || true
}

SAMPLE="--pick apache,jenkins --session-len 4 --no-refusals"
step S0_baseline    ""                            "--context 262144 --prompt-cache-gib 0"              "--sizes 32000,79000,128000,240000 $SAMPLE"
step S1_offsec      ""                            "--context 131072 --loop-guard --prompt-cache-gib 0" "--sizes 32000,79000,128000 $SAMPLE"
step S2b_vram_cache ""                            "--context 131072 --loop-guard"                      "--sizes 32000,79000,128000 --no-refusals"
step S3c_final      "TF_QWEN27_HOST_CACHE_GIB=48" "--context 262144 --loop-guard"                      "--sizes 32000,79000,128000,240000"
step G_nocache262   ""                            "--context 262144 --loop-guard --prompt-cache-gib 0" "--sizes '' --session 79000 --session-len 10 --no-refusals"

python3 "$HERE/summarize_v2.py" "$OUT" S0_baseline S1_offsec S2b_vram_cache S3c_final G_nocache262 | tee "$OUT/tables.md"
python3 "$HERE/exactness_gate.py" "$OUT" S3c_final G_nocache262 | tee "$OUT/exactness_gate.txt"
