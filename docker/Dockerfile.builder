# CUDA + Zig builder image for SUT-TF.
#
# Built and run on aipwnlocal LXC 110 ("dockers", 192.168.60.37).
# Produces a tensorfold-native binary targeted at RTX 3090 (sm_86).
#
# Not final. The CUDA / Zig versions get pinned once the first successful
# build is made; the comment next to each pin records the commit hash of the
# TensorFold source they built.
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

# Zig toolchain.
#
# Pinned to match ashhart/TensorFold's own .zig-version file. Their build.zig
# has a compile-time check that @compileErrors if Zig doesn't exactly match.
# When upstream bumps .zig-version, bump this pin AND the SHA below to the
# same values in the same commit — never guess, always mirror.
#
# Values confirmed 2026-11-11 against:
#   https://ziglang.org/download/index.json  -> 0.17.0 -> x86_64-linux
#
# Note: Zig flipped its tarball naming from `zig-linux-x86_64-...` to
# `zig-x86_64-linux-...` recently; mirror whatever the index says.
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
