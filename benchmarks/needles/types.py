"""
Needle generators. One function per needle type. Each returns:

  (plain_value: str, prompt_question: str)

`plain_value` is the exact string the model must emit. `prompt_question` is the
retrieval question we embed above the corpus.

Scaffolding only.
"""
from __future__ import annotations

import random


def ip(rng: random.Random) -> tuple[str, str]:
    value = f"{rng.randint(10, 199)}.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    return value, "What IP address made the authenticated request flagged as suspicious in the above log? Answer with only the IP."


def cve(rng: random.Random) -> tuple[str, str]:
    value = f"CVE-{rng.randint(2018, 2026)}-{rng.randint(1000, 48000)}"
    return value, "Which CVE identifier is referenced in the above content? Answer with only the CVE-ID."


def port(rng: random.Random) -> tuple[str, str]:
    value = str(rng.choice([22, 80, 443, 3306, 5432, 6379, 8080, 8443, 9200, 11211, 27017, 49651, 55222]))
    return value, "Which port number was the anomalous connection to? Answer with only the integer."


def cookie(rng: random.Random) -> tuple[str, str]:
    body = "".join(rng.choices("0123456789abcdef", k=16))
    value = f"session={body}"
    return value, "What was the value of the `session` cookie in the suspicious request? Answer with only `session=<value>`."


def http_header(rng: random.Random) -> tuple[str, str]:
    rid = "-".join(["".join(rng.choices("0123456789abcdef", k=4)) for _ in range(4)])
    value = f"X-Request-ID: {rid}"
    return value, "What X-Request-ID did the failing request carry? Answer with only the full header (name and value)."


def file_path(rng: random.Random) -> tuple[str, str]:
    year = rng.randint(2024, 2026)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    name = rng.choice(["auth.log", "nginx-access.log", "app.log", "audit.log"])
    value = f"/var/log/{name}.{year}-{month:02d}-{day:02d}.gz"
    return value, "Which archived log file is the quoted entry from? Answer with only the full path."


def api_endpoint(rng: random.Random) -> tuple[str, str]:
    method = rng.choice(["GET", "POST", "PUT", "DELETE", "PATCH"])
    resource = rng.choice(["users", "orders", "sessions", "keys", "permissions"])
    value = f"{method} /v2/{resource}/{{id}}/permissions"
    return value, "Which API endpoint does the spec describe for managing permissions? Answer with method and path, templating preserved."


REGISTRY = {
    "ip": ip,
    "cve": cve,
    "port": port,
    "cookie": cookie,
    "http_header": http_header,
    "file_path": file_path,
    "api_endpoint": api_endpoint,
}
