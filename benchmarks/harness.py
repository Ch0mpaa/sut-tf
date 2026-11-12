#!/usr/bin/env python3
"""
SUT-TF benchmark harness.

Scaffolding. Does not run yet. Shape only.

Command:
  python benchmarks/harness.py --config benchmarks/config.yaml --tag <slug>

Produces results under benchmarks/results/<date>-<slug>/.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import pathlib
import sys
from typing import Any


@dataclasses.dataclass
class TrialResult:
    endpoint: str
    corpus: str
    context_tokens: int
    needle_type: str
    needle_depth: float
    trial_index: int
    prefill_seconds: float | None
    decode_tokens_per_second: float | None
    time_to_first_token_seconds: float | None
    vram_peak_mib: int | None
    needle_match: bool | None
    raw_response: dict[str, Any] | None


def load_config(path: pathlib.Path) -> dict[str, Any]:
    raise NotImplementedError("YAML loader not yet wired")


def enumerate_trials(config: dict[str, Any]):
    """Yield one TrialSpec per (endpoint, corpus, context_size, needle, depth, trial)."""
    raise NotImplementedError


def run_trial(spec, needle_catalog, vram_sampler) -> TrialResult:
    """
    1. Build corpus of `context_tokens`, insert `needle` at `depth`.
    2. Send chat completion to endpoint's base_url.
    3. While request runs, vram_sampler captures peak.
    4. On response, parse prefill_seconds / tokens_per_second from the
       tensorfold payload; grade needle recall by exact string match.
    5. Return TrialResult.
    """
    raise NotImplementedError


def write_outputs(results: list[TrialResult], out_dir: pathlib.Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "run.json").write_text(
        json.dumps([dataclasses.asdict(r) for r in results], indent=2)
    )
    # report.md rendered in a later commit.


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=pathlib.Path, required=True)
    parser.add_argument("--tag", required=True, help="Short slug for this run")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List trials that would run without sending requests",
    )
    args = parser.parse_args(argv)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = pathlib.Path("benchmarks/results") / f"{stamp}-{args.tag}"

    print(f"[harness] config={args.config} out={out_dir} dry_run={args.dry_run}")
    print("[harness] NOT IMPLEMENTED — scaffolding only")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
