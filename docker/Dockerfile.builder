# CUDA 12.4 + Zig 0.17.0 builder image for the patched engine (RTX 3090, sm_86).
#   docker build -t sut-tf-builder:0.1 -f Dockerfile.builder .
# These pins are what built the binary in benchmarks/results.
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      curl \
      git \
      pkg-config \
      python3 python3-pip python3-venv \
      xz-utils \
    && rm -rf /var/lib/apt/lists/*

# Zig toolchain. The engine's build refuses any other Zig version, so this must match the
# checkout's .zig-version. SHA from https://ziglang.org/download/index.json.
ENV ZIG_VERSION=0.17.0 \
    ZIG_SHA256=1cbe9df9f27e6b78d14ccbca43b6703a404ef79ef1c463de901d7f088d4e2026
RUN set -eux; \
    tarball="zig-x86_64-linux-${ZIG_VERSION}.tar.xz"; \
    curl -fsSL -o "/tmp/${tarball}" "https://ziglang.org/download/${ZIG_VERSION}/${tarball}"; \
    echo "${ZIG_SHA256}  /tmp/${tarball}" | sha256sum -c -; \
    tar -xJ -C /opt -f "/tmp/${tarball}"; \
    rm "/tmp/${tarball}"; \
    ln -s "/opt/zig-x86_64-linux-${ZIG_VERSION}/zig" /usr/local/bin/zig; \
    zig version

WORKDIR /work

# Build script lives alongside this Dockerfile.
COPY build-sut-tf.sh /usr/local/bin/build-sut-tf.sh
RUN chmod +x /usr/local/bin/build-sut-tf.sh

CMD ["/usr/local/bin/build-sut-tf.sh"]
