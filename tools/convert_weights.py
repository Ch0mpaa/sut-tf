"""Convert a mixed-precision MLX checkpoint into a reference checkpoint's exact tensor layout:
uniform affine 4-bit (group 64) weights and bf16 scales, biases and unquantized tensors.

For every tensor the reference has, the output gets the source's values in the reference's dtype and shape:
- same shape and dtype: copied
- same shape, f16/f32 where the reference has bf16: cast
- a quantized module whose packed width differs (5/6/8-bit in the source): dequantized with the source's
  per-module bits from its config.json, then requantized to 4-bit group 64 (weight, scales and biases together)
Tensors only the source has (for example an MTP head) are dropped. Non-weight files come from the reference.

Usage: convert_weights.py --src SRC_DIR --ref REF_DIR --out OUT_DIR"""
import argparse, glob, json, os, shutil, struct, sys, time
import numpy as np

_ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
_ap.add_argument("--src", required=True, help="source checkpoint directory (mixed-precision MLX safetensors)")
_ap.add_argument("--ref", required=True, help="reference checkpoint directory with the target layout")
_ap.add_argument("--out", required=True, help="output directory")
_args = _ap.parse_args()
SRC, REF, OUT = _args.src, _args.ref, _args.out
CHUNK = 2048

DT = {"F16": np.float16, "BF16": np.uint16, "F32": np.float32, "U32": np.uint32}


def read_header(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        h = json.loads(f.read(n))
    return h, 8 + n


def index_tensors(snap):
    tensors, meta = {}, {}
    for f in sorted(glob.glob(snap + "/model-*.safetensors")):
        h, base = read_header(f)
        meta[os.path.basename(f)] = h.pop("__metadata__", None)
        for k, v in h.items():
            tensors[k] = (f, base, v)
    return tensors, meta


def load(entry):
    f, base, v = entry
    s, e = v["data_offsets"]
    arr = np.memmap(f, dtype=np.uint8, mode="r", offset=base + s, shape=(e - s,))
    return arr.view(DT[v["dtype"]]).reshape(v["shape"]), v["dtype"]


def to_f32(arr, dtype):
    if dtype == "BF16":
        return (arr.astype(np.uint32) << 16).view(np.float32)
    return arr.astype(np.float32)


def f32_to_bf16(x):
    u = np.ascontiguousarray(x, dtype=np.float32).view(np.uint32)
    return ((u + 0x7FFF + ((u >> 16) & 1)) >> 16).astype(np.uint16)


def unpack(words, bits):
    rows = words.shape[0]
    b = np.unpackbits(np.ascontiguousarray(words).view(np.uint8).reshape(rows, -1), axis=1, bitorder="little")
    b = b.reshape(rows, -1, bits).astype(np.uint8)
    q = np.zeros(b.shape[:2], dtype=np.uint8)
    for k in range(bits):
        q |= b[:, :, k] << k
    return q


def pack4(q):
    q = q.astype(np.uint32).reshape(q.shape[0], -1, 8)
    w = np.zeros(q.shape[:2], dtype=np.uint32)
    for j in range(8):
        w |= q[:, :, j] << (4 * j)
    return w


def dequant(w, s, b, bits, group):
    q = unpack(w, bits).astype(np.float32)
    rows, n = q.shape
    q = q.reshape(rows, n // group, group)
    return (q * s[:, :, None] + b[:, :, None]).reshape(rows, n)


def requant4(x, group=64):
    rows, n = x.shape
    g = x.reshape(rows, n // group, group)
    lo, hi = g.min(axis=2), g.max(axis=2)
    scale = np.maximum((hi - lo) / 15.0, 1e-8)
    s16, b16 = f32_to_bf16(scale), f32_to_bf16(lo)
    s, b = to_f32(s16, "BF16"), to_f32(b16, "BF16")
    q = np.clip(np.rint((g - b[:, :, None]) / s[:, :, None]), 0, 15).astype(np.uint8)
    return pack4(q.reshape(rows, n)), s16, b16


def corr(a, b):
    a, b = a.ravel() - a.mean(), b.ravel() - b.mean()
    return float((a @ b) / (np.sqrt((a @ a) * (b @ b)) + 1e-12))


def main():
    t0 = time.time()
    src, _ = index_tensors(SRC)
    ref, ref_meta = index_tensors(REF)
    qcfg = json.load(open(SRC + "/config.json")).get("quantization", {})
    default_bits, default_group = qcfg.get("bits", 4), qcfg.get("group_size", 64)

    def qparams(module):
        o = qcfg.get(module)
        if isinstance(o, dict):
            return o.get("bits", default_bits), o.get("group_size", default_group)
        return default_bits, default_group

    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(REF):
        if not name.endswith(".safetensors"):
            p = os.path.join(REF, name)
            if os.path.isfile(p):
                shutil.copyfile(os.path.realpath(p), os.path.join(OUT, name))

    shards = {}
    for k, (f, _, _) in ref.items():
        shards.setdefault(os.path.basename(f), []).append(k)

    stats = {"copied": 0, "cast": 0, "requant": 0}
    worst = []
    done_requant = set()
    for shard in sorted(shards):
        names = sorted(shards[shard])
        payload, header, off = [], {}, 0
        for k in names:
            rv = ref[k][2]
            if k not in src:
                sys.exit(f"missing in source: {k}")
            sarr, sdt = load(src[k])
            rshape, rdt = tuple(rv["shape"]), rv["dtype"]
            module, _, leaf = k.rpartition(".")
            needs_requant = (
                leaf in ("weight", "scales", "biases")
                and module + ".scales" in src
                and tuple(src[module + ".weight"][2]["shape"]) != tuple(ref[module + ".weight"][2]["shape"])
            )
            if needs_requant:
                if module not in done_requant:
                    bits, group = qparams(module)
                    w, _ = load(src[module + ".weight"])
                    s, sd = load(src[module + ".scales"])
                    b, bd = load(src[module + ".biases"])
                    ow, os_, ob = [], [], []
                    sample_x = None
                    for r in range(0, w.shape[0], CHUNK):
                        x = dequant(w[r:r + CHUNK], to_f32(s[r:r + CHUNK], sd), to_f32(b[r:r + CHUNK], bd), bits, group)
                        qw, qs, qb = requant4(x)
                        ow.append(qw); os_.append(qs); ob.append(qb)
                        if sample_x is None:
                            sample_x = (x, dequant(qw, to_f32(qs, "BF16"), to_f32(qb, "BF16"), 4, 64))
                    conv = {"weight": np.concatenate(ow), "scales": np.concatenate(os_), "biases": np.concatenate(ob)}
                    rw, _ = load(ref[module + ".weight"])
                    rs, rsd = load(ref[module + ".scales"])
                    rb, rbd = load(ref[module + ".biases"])
                    n = min(CHUNK, rw.shape[0])
                    rx = dequant(rw[:n], to_f32(rs[:n], rsd), to_f32(rb[:n], rbd), 4, 64)
                    c_ref = corr(sample_x[1], rx)
                    c_self = corr(sample_x[1], sample_x[0])
                    worst.append((c_ref, c_self, module, bits))
                    print(f"  requant {module} {bits}b->4b corr(vs ref)={c_ref:.4f} corr(vs src)={c_self:.5f}", flush=True)
                    done_requant.add(module)
                    globals().setdefault("_conv", {})[module] = conv
                data = globals()["_conv"][module][leaf]
                if tuple(data.shape) != rshape:
                    sys.exit(f"shape mismatch after requant {k}: {data.shape} vs {rshape}")
                stats["requant"] += 1
            elif tuple(sarr.shape) == rshape and sdt == rdt:
                data = np.ascontiguousarray(sarr)
                stats["copied"] += 1
            elif tuple(sarr.shape) == rshape and rdt == "BF16" and sdt in ("F16", "F32"):
                data = f32_to_bf16(sarr.astype(np.float32))
                stats["cast"] += 1
            else:
                sys.exit(f"unhandled tensor {k}: src {sdt}{tuple(sarr.shape)} ref {rdt}{rshape}")
            raw = np.ascontiguousarray(data).view(np.uint8).ravel()
            header[k] = {"dtype": rdt, "shape": list(rshape), "data_offsets": [off, off + raw.size]}
            payload.append(raw)
            off += raw.size
        if ref_meta.get(shard):
            header["__metadata__"] = ref_meta[shard]
        hb = json.dumps(header, separators=(",", ":")).encode()
        hb += b" " * (-len(hb) % 8)
        with open(os.path.join(OUT, shard), "wb") as fh:
            fh.write(struct.pack("<Q", len(hb)))
            fh.write(hb)
            for raw in payload:
                fh.write(raw.tobytes())
        print(f"wrote {shard} ({off / 1e9:.2f} GB) t={time.time() - t0:.0f}s", flush=True)

    print("stats", stats)
    worst.sort()
    print("lowest corr vs ref:")
    for c_ref, c_self, m, bits in worst[:8]:
        print(f"  {c_ref:.4f} (self {c_self:.5f}) {bits}b {m}")
    print(f"done in {time.time() - t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main()
