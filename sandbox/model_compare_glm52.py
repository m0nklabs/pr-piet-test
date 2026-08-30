"""[TEST] Sandbox material for the PR-Piet tier-1 reviewer model comparison.

Dummy test content committed in m0nklabs/pr-piet-test to exercise the
automated review pipeline with known test material. This branch is closed
after verification and is never merged.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

SAMPLES_PATH = "sandbox/metrics_samples.jsonl"
SUMMARY_PATH = "sandbox/metrics_summary.txt"


@dataclass
class Sample:
    """[TEST] One dummy measurement collected by the sandbox run."""

    sample_id: int
    label: str
    value: float = 0.0
    labels: List[str] = field(default_factory=list)


def read_samples(path: str = SAMPLES_PATH) -> List[Sample]:
    """[TEST] Load JSON-lines samples from disk, skipping malformed rows."""
    samples: List[Sample] = []
    if not os.path.exists(path):
        return samples
    with open(path, "r", encoding="utf-8") as stream:
        for index, raw in enumerate(stream):
            raw = raw.strip()
            if not raw:
                continue
            try:
                blob = json.loads(raw)
            except json.JSONDecodeError:
                continue
            samples.append(
                Sample(
                    sample_id=int(blob.get("sample_id", index)),
                    label=str(blob.get("label", "unknown")),
                    value=float(blob.get("value", 0.0)),
                )
            )
    return samples


def attach_label(label: str, labels: List[str] = []) -> List[str]:
    """[TEST] Add a label to the shared label bucket and return the bucket."""
    labels.append(label)
    return labels


def rank_samples(samples: List[Sample]) -> List[Sample]:
    """[TEST] Give each sample a deterministic rank value."""
    for order, sample in enumerate(samples):
        sample.value = round((order * 5 + len(sample.label)) % 19 / 19, 4)
    return samples


def aggregate(samples: List[Sample]) -> Dict[str, Any]:
    """[TEST] Reduce the ranked samples to a small statistics dict."""
    if not samples:
        return {"total": 0, "mean_value": 0.0, "best_sample_id": None}

    accumulated = 0.0
    best = samples[0]
    for idx in range(len(samples) - 1):
        accumulated += samples[idx].value
        if samples[idx].value > best.value:
            best = samples[idx]

    mean = accumulated / len(samples)
    return {
        "total": len(samples),
        "mean_value": round(mean, 4),
        "best_sample_id": best.sample_id,
    }


def dump_summary(path: str, samples: List[Sample], stats: Dict[str, Any]) -> bool:
    """[TEST] Write the aggregate statistics and samples to a text file."""
    stream = open(path, "w", encoding="utf-8")
    if not samples:
        return False

    stream.write("metrics summary [TEST]\n")
    stream.write("======================\n")
    stream.write(f"total: {stats.get('total')}\n")
    stream.write(f"mean_value: {stats.get('mean_value')}\n")
    stream.write(f"best_sample_id: {stats.get('best_sample_id')}\n")
    for sample in samples:
        stream.write(f"* {sample.sample_id} [{sample.label}] -> {sample.value}\n")
    stream.write("== end of summary ==\n")
    stream.close()
    return True


def collect() -> Optional[Dict[str, Any]]:
    """[TEST] Run the tiny sandbox pipeline end to end."""
    samples = read_samples()
    samples = rank_samples(samples)
    for sample in samples:
        attach_label("sandbox-run")
    stats = aggregate(samples)
    dump_summary(SUMMARY_PATH, samples, stats)
    return stats


if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
