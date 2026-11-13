import glob, json, struct, re, collections
import numpy as np

def index(snap):
    t = {}
    for f in sorted(glob.glob(snap + "/model-*.safetensors")):
        with open(f, "rb") as fh:
            n = struct.unpack("<Q", fh.read(8))[0]
            h = json.loads(fh.read(n))
        h.pop("__metadata__", None)
        for k, v in h.items():
            t[k] = (f, 8 + n, v)
    return t

def raw(e, rows=None):
    f, base, v = e
    s, x = v["data_offsets"]
    a = np.memmap(f, dtype=np.uint8, mode="r", offset=base + s, shape=(x - s,))
    dt = {"BF16": np.uint16, "F16": np.float16, "U32": np.uint32, "F32": np.float32}[v["dtype"]]
    a = a.view(dt).reshape(v["shape"])
    a = a[:rows] if rows else a
    if v["dtype"] == "BF16":
        return (a.astype(np.uint32) << 16).view(np.float32)
    return a

def deq4(w, s, b):
    rows = w.shape[0]
    q = np.stack([(w >> (4 * j)) & 0xF for j in range(8)], axis=-1).reshape(rows, -1).astype(np.float32)
    q = q.reshape(rows, s.shape[1], -1)
    return (q * s[:, :, None].astype(np.float32) + b[:, :, None].astype(np.float32)).reshape(rows, -1)

new = index("/home/chris/models/qwen38-27b-ablit-m3tis")
ref = index(glob.glob("/srv/models/huggingface/hub/models--Vontra--*/snapshots/*")[0])
groups = collections.defaultdict(list)
for k in ref:
    if not k.endswith(".scales"):
        continue
    m = k[:-7]
    a = deq4(raw(new[m + ".weight"], 256), raw(new[m + ".scales"], 256), raw(new[m + ".biases"], 256))
    b = deq4(raw(ref[m + ".weight"], 256), raw(ref[m + ".scales"], 256), raw(ref[m + ".biases"], 256))
    da, db = a.ravel() - a.mean(), b.ravel() - b.mean()
    c = float(da @ db / np.sqrt((da @ da) * (db @ db)))
    groups[re.sub(r"\.\d+\.", ".N.", m)].append(c)

for cls, cs in sorted(groups.items(), key=lambda kv: min(kv[1])):
    print(f"min={min(cs):7.4f} mean={np.mean(cs):7.4f} n={len(cs):3d} {cls}")
