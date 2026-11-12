# docker/

The CUDA + Zig builder for SUT-TF. Runs on aipwnlocal LXC 110 "dockers"
(192.168.60.37), not on ailab. Keeps ailab's installed toolchain untouched
and lets us pin exact Zig + CUDA versions in a reproducible image.

## Not ready

Zig version in `Dockerfile.builder` is unset. The container will fail to
build until we confirm the required Zig version from the upstream TensorFold
source. See `docs/LINEAGE.md`.

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
