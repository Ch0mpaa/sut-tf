# Recipe

How we built the box in the [README](README.md), step by step. The commands assume Linux, Docker with the NVIDIA
container toolkit, and `huggingface-cli`. Paths are examples; change them to fit your machine.

## 0. Hardware and power

- One RTX 3090 (24 GB). The patch builds for sm_86 only.
- Host RAM for the prompt cache. We pin 48 GiB on a 256 GB box. Size it to what you have (step 5).
- NVIDIA driver 615.71.09 on our box. Anything that runs CUDA 12.4 should work.
- Cap the card at 250 W. Every number in this repo was measured at that cap:

```bash
sudo nvidia-smi -i 0 -pm 1
sudo nvidia-smi -i 0 -pl 250
```

## 1. Engine source plus our patch

The base engine is a Zig/CUDA build with 3090 kernels, 4-bit KV and block-drafter support. Our patch adds the prompt
cache on top of one pinned commit:

```bash
git clone https://github.com/CanadaApollo6/TensorFold engine && cd engine
git checkout c7c3f7c8
git am /path/to/sut-tf/patches/0001-qwen27-CUDA-prompt-cache-with-resumable-prefill-and-.patch
```

What the patch does:

- **Snapshots.** At chosen prompt positions it saves the model state: the recurrent and conv state of all 48
  linear-attention layers, plus the K/V prefix of the 16 full-attention layers.
- **Resumable prefill.** A new request that shares a prefix with a saved snapshot restores it and reads only the new
  tokens. Prefill chunks are anchored to a fixed grid, so a resumed read does the same arithmetic as a cold one.
- **Exactness fix.** Short resumed pieces (192 rows or fewer) used to take the decode matmul path, and that changed
  tokens. The patch forces prompt matmuls during resumed reads (see RESULTS.md, "The bug the benchmark caught").
- **Pinned-RAM tier.** Set `TF_QWEN27_HOST_CACHE_GIB=N` and snapshots live in N GiB of pinned host memory instead of
  leftover VRAM, so a 262K window and a full-size cache fit together.
- **Save points.** The cache saves at the end of the system message. Put the recon dump in the system message and
  every question after it is a cache hit.

## 2. Build

```bash
cd /path/to/sut-tf/docker
docker build -t sut-tf-builder:0.1 -f Dockerfile.builder .
cd /path/to/engine
docker run --rm --gpus all --user "$(id -u):$(id -g)" -e HOME=/tmp -e ZIG_GLOBAL_CACHE_DIR=/src/.zig-global-cache \
  -v "$PWD":/src -w /src sut-tf-builder:0.1 build-sut-tf.sh
```

The binary loads a set of prebuilt sm_86 glue kernels from `../share` next to `bin/`. Take them from the base
engine's 3090 release:

```bash
huggingface-cli download CanadaApollo6/Qwen3.8-27B-M3TiS-3090 --include 'share/*' --local-dir /tmp/rel
cp -r /tmp/rel/share zig-out-host/native/
sudo mkdir -p /opt/sut-tf && sudo cp -r zig-out-host/native/* /opt/sut-tf/
```

The build isn't byte-reproducible: the same commit rebuilt in another checkout gives a different md5, because the
checkout path ends up inside the binary. The md5 in RESULTS.md only identifies the binary we benchmarked. To check
your build, run the benchmark and its exactness gate (step 6).

## 3. Abliterated weights in the engine's layout

The engine's 3090 path loads exactly one tensor layout: uniform affine 4-bit, group 64, bf16 scales and biases. The
abliterated checkpoint we use is mixed precision (some modules at 5 and 6 bits), so we convert it. A stock 4-bit
checkpoint of the same model supplies the target layout:

```bash
huggingface-cli download YCF-AI/Qwen3.8-27B-Huihui-abliterated-oQ4e-MTP-FP16-MLX --local-dir /srv/models/src-ablit
huggingface-cli download Vontra/Qwen3.8-27B-MLX-4bit --local-dir /srv/models/ref-4bit
python3 tools/convert_weights.py --src /srv/models/src-ablit --ref /srv/models/ref-4bit \
  --out /srv/models/qwen38-27b-abliterated-4bit
```

The converter copies tensors that already match. It casts f16/f32 to bf16, and requantizes the 168 mixed-precision
modules to 4-bit g64. It drops the MTP head, which the engine doesn't use. It needs numpy and about 15 GB of free disk.

Then check the result. Every module class should correlate at about 0.98 or better with the stock 4-bit weights; the
abliteration edit is small. A broken conversion shows up as near zero:

```bash
python3 tools/verify_quant_vs_ref.py --converted /srv/models/qwen38-27b-abliterated-4bit --ref /srv/models/ref-4bit
```

Ours: lowest module class 0.985, most at 0.99.

## 4. Drafter

The block drafter makes decoding 2–4× faster and doesn't change the output:

```bash
HF_HOME=/srv/models/huggingface huggingface-cli download z-lab/Qwen3.8-27B-DFlash2
```

## 5. Serve

Use [`configs/offsec.conf`](configs/offsec.conf) as a systemd drop-in, or run the same line by hand:

```bash
TF_QWEN27_KV_BITS=4 TF_QWEN27_HOST_CACHE_GIB=48 HF_HOME=/srv/models/huggingface \
/opt/sut-tf/bin/tensorfold-native serve --host 0.0.0.0 --port 8000 --name redops-abliterated \
  --backend cuda --device 0 --parallel 1 --context 262144 --loop-guard \
  --drafter z-lab/Qwen3.8-27B-DFlash2 --no-thinking --no-update-check /srv/models/qwen38-27b-abliterated-4bit
```

| Setting | Why |
|---|---|
| `TF_QWEN27_KV_BITS=4` | 4-bit K/V is what fits a 262K window next to the model on 24 GB. It's lossy: greedy output differs from 16-bit KV. We accept that. |
| `TF_QWEN27_HOST_CACHE_GIB=48` | Prompt states in pinned RAM. At 262K there's no VRAM left for them. |
| `--context 262144` | The full window. Prompts read in 1024-row chunks at this size (4096 at 131K), about 8% slower on cold reads. |
| `--parallel 1` | A 262K window takes the whole card. |
| `--loop-guard` | Stops repetition loops. Cost nothing measurable. |
| `--drafter …DFlash2` | Lossless speculative decoding. |
| `--no-thinking` | Answers without a reasoning preamble. That's what the benchmark scores. |
| greedy (temperature 0) | Benchmark setting. A temperature of 0.3 was 8% slower with no accuracy gain. |

The server speaks the OpenAI chat API on `/v1`. For agents, send the tool output or recon dump as the **system**
message and the question as the user message. That's where the cache saves.

## 6. Benchmark it

On the GPU host, with nothing else on the card:

```bash
cd benchmarks
BIN=/opt/sut-tf/bin/tensorfold-native MODEL=/srv/models/qwen38-27b-abliterated-4bit GPU=0 ./run_steps.sh
```

The script brings up a fresh server for each step and runs the offsec benchmark against it. It writes JSON receipts,
`tables.md`, and the cache exactness gate result (`exactness_gate.txt`; anything but `GATE PASS` means the cache
changed an answer). A full run takes about 1.5–2 hours. [docs/METHOD.md](docs/METHOD.md) explains what each test does.
