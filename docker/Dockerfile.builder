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

# Zig toolchain. Version set once first successful SUT-TF build is reproduced.
# TensorFold README specifies the required Zig version; until we have confirmed
# that from the upstream source, we ship with a placeholder that fails loudly.
ENV ZIG_VERSION=UNPINNED
RUN if [ "$ZIG_VERSION" = "UNPINNED" ]; then \
      echo "ERROR: ZIG_VERSION not set; see docker/Dockerfile.builder header." >&2 ; \
      exit 42 ; \
    fi && \
    curl -fsSL "https://ziglang.org/download/${ZIG_VERSION}/zig-linux-x86_64-${ZIG_VERSION}.tar.xz" \
      | tar -xJ -C /opt && \
    ln -s "/opt/zig-linux-x86_64-${ZIG_VERSION}/zig" /usr/local/bin/zig

WORKDIR /work

# Build script lives alongside this Dockerfile.
COPY build-sut-tf.sh /usr/local/bin/build-sut-tf.sh
RUN chmod +x /usr/local/bin/build-sut-tf.sh

CMD ["/usr/local/bin/build-sut-tf.sh"]
