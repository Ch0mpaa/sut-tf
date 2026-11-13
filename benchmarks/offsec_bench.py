"""offsec-v1: one recon dump, several questions in a row, exact-answer scoring.
Usage: offsec_bench.py PORT TAG [TARGET_TOKENS]"""
import json, random, re, sys, time, urllib.request

PORT, TAG = sys.argv[1], sys.argv[2]
TARGET = int(sys.argv[3]) if len(sys.argv) > 3 else 80_000
URL = f"http://127.0.0.1:{PORT}/v1/chat/completions"
rng = random.Random(4242)


def ip():
    return f"10.{rng.randint(0, 40)}.{rng.randint(0, 255)}.{rng.randint(2, 254)}"


SERVICES = [("22/tcp", "ssh", "OpenSSH 8.9p1 Ubuntu 3ubuntu0.6"), ("80/tcp", "http", "nginx 1.24.0"),
            ("443/tcp", "ssl/http", "nginx 1.24.0"), ("3306/tcp", "mysql", "MySQL 8.0.36"),
            ("8080/tcp", "http", "Apache Tomcat 9.0.85"), ("5432/tcp", "postgresql", "PostgreSQL DB 15.6"),
            ("6379/tcp", "redis", "Redis key-value store 7.2.4"), ("3389/tcp", "ms-wbt-server", "Microsoft Terminal Services")]
PATHS = ["/", "/login", "/api/v1/users", "/api/v1/orders", "/static/app.js", "/favicon.ico", "/health",
         "/api/v1/search?q=test", "/admin", "/robots.txt", "/wp-login.php", "/.env", "/api/v1/export"]

hosts = list(dict.fromkeys(ip() for _ in range(4000)))
key_ip, trav_ip = ip(), ip()
api_key = "sk_live_" + "".join(rng.choices("0123456789abcdef", k=24))
trav_path = "/static/..%2f..%2f..%2f..%2fetc/passwd"

chars, budget = 0, int(TARGET * 1.9)
entries, logs = [], []
for h in hosts:
    if chars > budget * 0.55:
        break
    lines = [f"Nmap scan report for {h}", f"Host is up (0.00{rng.randint(10, 99)}s latency).",
             "PORT      STATE SERVICE       VERSION"]
    for port, svc, ver in rng.sample(SERVICES, rng.randint(2, 4)):
        lines.append(f"{port:<9} open  {svc:<13} {ver}")
    entries.append((h, lines))
    chars += sum(len(x) + 1 for x in lines)
included = [h for h, _ in entries]
apache_host = included[len(included) * 2 // 3]
smb_hosts = sorted(rng.sample(included, 10))
for h, lines in entries:
    if h == apache_host:
        lines.append(f"{'8443/tcp':<9} open  {'http':<13} Apache httpd 2.4.49 ((Unix))")
    if h in smb_hosts:
        lines.append(f"{'445/tcp':<9} open  {'microsoft-ds':<13} Microsoft Windows Server 2019 microsoft-ds")
nmap = ["\n".join(lines) + "\n" for _, lines in entries]


def logline(src, method, path, status):
    return (f'{src} - - [12/Nov/2026:{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d} +0000] '
            f'"{method} {path} HTTP/1.1" {status} {rng.randint(120, 48000)} "-" "Mozilla/5.0 (X11; Linux x86_64)"\n')


while chars < budget:
    r = rng.random()
    if r < 0.01:
        ln = logline(ip(), "GET", "/static/..%2f..%2fetc/shadow", rng.choice([400, 403, 404]))
    else:
        ln = logline(ip(), rng.choice(["GET", "GET", "POST"]), rng.choice(PATHS), rng.choice([200, 200, 200, 301, 404]))
    logs.append(ln)
    chars += len(ln)
logs.insert(len(logs) // 3, logline(key_ip, "GET", f"/api/v1/export?format=csv&token={api_key}", 200))
logs.insert(2 * len(logs) // 3, logline(trav_ip, "GET", trav_path, 200))
dump = "=== nmap -sV results ===\n" + "".join(nmap) + "\n=== web access log (edge-01) ===\n" + "".join(logs)

Q = [
    ("apache", "Which host runs Apache httpd 2.4.49, and on which port? Reply with only JSON {\"ip\": ..., \"port\": ...}.",
     lambda a: apache_host in a and "8443" in a, 120),
    ("apikey", "A request in the access log leaked an API key starting with sk_live_. Reply with only JSON {\"key\": ..., \"ip\": ...}.",
     lambda a: api_key in a and key_ip in a, 120),
    ("traversal", "One path-traversal request (containing ..%2f) got HTTP 200. Reply with only JSON {\"path\": ..., \"ip\": ...}.",
     lambda a: trav_path in a and trav_ip in a, 120),
    ("smb", "List every host with port 445 open. Reply with only a JSON array of IP strings.", None, 400),
]


def ask(question, max_tokens):
    body = json.dumps({"model": "redops-abliterated", "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": dump + "\n\n" + question}]}).encode()
    t0 = time.time()
    with urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=1800) as r:
        d = json.load(r)
    return d, time.time() - t0


res = []
for name, q, check, mt in Q:
    d, wall = ask(q, mt)
    a = d["choices"][0]["message"]["content"]
    tf, u = d.get("tensorfold", {}), d["usage"]
    if name == "smb":
        got = set(re.findall(r"\d+\.\d+\.\d+\.\d+", a))
        tp = len(got & set(smb_hosts))
        score = f"{tp}/{len(smb_hosts)} found, {len(got - set(smb_hosts))} wrong"
        ok = tp == len(smb_hosts) and got <= set(smb_hosts)
    else:
        ok = check(a)
        score = "exact" if ok else "MISS"
    row = dict(q=name, ok=ok, score=score, prompt_tokens=u["prompt_tokens"],
               cached=(u.get("prompt_tokens_details") or {}).get("cached_tokens", 0),
               ttft=tf.get("time_to_first_token"), prefill=tf.get("prefill_seconds"), tps=tf.get("tokens_per_second"),
               out=u["completion_tokens"], wall=wall,
               answer=a[:240].replace(api_key, "sk_live_<planted-key-redacted>"))
    res.append(row)
    print(f"[{TAG}] {name:9} {score:24} prompt={row['prompt_tokens']} cached={row['cached']} "
          f"ttft={row['ttft'] or 0:7.2f}s decode={row['tps'] or 0:6.1f} tok/s out={row['out']} wall={wall:7.1f}s", flush=True)
json.dump(res, open(f"/home/chris/bench-receipts/offsec/{TAG}.json", "w"), indent=1)
print(f"[{TAG}] DONE correct={sum(r['ok'] for r in res)}/{len(res)} total_wall={sum(r['wall'] for r in res):.0f}s", flush=True)
