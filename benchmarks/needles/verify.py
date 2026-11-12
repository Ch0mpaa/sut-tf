"""
Scoring. Exact-match on needle value; Wilson binomial CI on recall rates.

Scaffolding only.
"""
from __future__ import annotations

import math


def exact_match(expected: str, response_text: str) -> bool:
    """
    True iff `expected` appears verbatim in `response_text`. Case-sensitive for
    hex / case-insensitive for API method names will be decided after the first
    baseline run shows false-negative rates.
    """
    return expected in response_text


def wilson_ci(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """
    Wilson score interval for a binomial proportion. Returns (lower, upper).
    """
    if trials == 0:
        return 0.0, 1.0
    z = {0.90: 1.6449, 0.95: 1.9599, 0.99: 2.5758}[confidence]
    phat = successes / trials
    denom = 1 + z * z / trials
    center = (phat + z * z / (2 * trials)) / denom
    halfwidth = z * math.sqrt(phat * (1 - phat) / trials + z * z / (4 * trials * trials)) / denom
    return max(0.0, center - halfwidth), min(1.0, center + halfwidth)
