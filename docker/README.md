# docker/

The CUDA + Zig builder for SUT-TF. Runs on aipwnlocal LXC 110 "dockers"
(192.168.60.37), not on ailab. Keeps ailab's installed toolchain untouched
and lets us pin exact Zig + CUDA versions in a reproducible image.

## Status

- Zig version pinned: **0.17.0** (mirrors TensorFold `.zig-version`)
- CUDA pinned: `nvidia/cuda:12.4.1-devel-ubuntu22.04`
- Build script (`build-sut-tf.sh`): placeholder, fails loudly until the
  engine source is imported into `../engine/`

## When to use this (and when not)

**Not for daily development.** This LXC has no GPU passthrough, so a
container build can never smoke-test the binary against a real 3090. Every
iteration becomes compile-here → `scp` → restart service on ailab → test,
which is a slow loop.

**Daily development happens on ailab directly** (where the 3090 lives). This
Dockerfile exists to give us a reproducible release recipe once the ailab
build is working — a way to pin exact toolchain versions for the article's
reproducibility section and for CI if we ever add it.

Workflow:
1. Iterate the engine source and build on ailab until it compiles and serves
2. Record the exact Zig + CUDA + kernel versions that worked
3. Mirror those into this Dockerfile and verify the container produces a
   byte-equivalent binary
4. The container recipe becomes the "frozen" build for publication; ailab
   stays the dev loop

## Intended workflow (planned)

```sh
# On dockers (192.168.60.37):
docker build -t sut-tf-builder:dev -f docker/Dockerfile.builder docker/
docker run --rm -v /path/to/engine:/work sut-tf-builder:dev
# -> produces engine/zig-out/bin/tensorfold-native
#
# Then scp that binary to ailab:
scp engine/zig-out/bin/tensorfold-native chris@ailab:/home/chris/sut-tf/bin/
```

Deployment on ailab is via a drop-in override to `/etc/systemd/system/
tensorfold-gpu1.service.d/override.conf` that points `ExecStart` at the new
binary. Stock TF stays installed and running on GPU 0 for A/B comparison.
