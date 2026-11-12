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
# When upstream bumps .zig-version, bump this pin to the same value in the
# same commit — never guess, always mirror.
#
# Current pin confirmed 2026-11-11 against:
#   https://raw.githubusercontent.com/ashhart/TensorFold/main/.zig-version
ENV ZIG_VERSION=0.17.0
RUN curl -fsSL "https://ziglang.org/download/${ZIG_VERSION}/zig-linux-x86_64-${ZIG_VERSION}.tar.xz" \
      | tar -xJ -C /opt && \
    ln -s "/opt/zig-linux-x86_64-${ZIG_VERSION}/zig" /usr/local/bin/zig && \
    zig version

WORKDIR /work

# Build script lives alongside this Dockerfile.
COPY build-sut-tf.sh /usr/local/bin/build-sut-tf.sh
RUN chmod +x /usr/local/bin/build-sut-tf.sh

CMD ["/usr/local/bin/build-sut-tf.sh"]
