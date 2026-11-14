#!/usr/bin/env bash
# Build the patched engine inside the builder image. Run from the engine checkout:
#   docker run --rm --gpus all --user "$(id -u):$(id -g)" -e HOME=/tmp -e ZIG_GLOBAL_CACHE_DIR=/src/.zig-global-cache \
#     -v "$PWD":/src -w /src sut-tf-builder:0.1 build-sut-tf.sh
# Output: zig-out-host/native/bin/tensorfold-native for RTX 30-series (sm_86).
set -euo pipefail

zig build native -Dcpu=x86_64_v3 -Dnvcc=/usr/local/cuda/bin/nvcc -Dsm=86 --prefix /src/zig-out-host
ls -la /src/zig-out-host/native/bin/tensorfold-native
