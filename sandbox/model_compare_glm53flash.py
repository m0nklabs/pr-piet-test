"""[TEST] Sandbox material for the PR-Piet tier-1 reviewer model comparison.

Dummy test content committed in m0nklabs/pr-piet-test to exercise the
automated review pipeline with known test material. This branch is closed
after verification and is never merged.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_SOURCE = "sandbox/sample_records.jsonl"
DEFAULT_REPORT = "sandbox/comparison_report.txt"


@dataclass
class Record:
    """[TEST] A single dummy record processed by the comparison run."""

    record_id: int
    payload: str
    score: float = 0.0
    tags: List[str] = field(default_factory=list)


def load_records(path: str = DEFAULT_SOURCE) -> List[Record]:
    """[TEST] Read a JSON-lines file and convert every line to a Record."""
    records: List[Record] = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            records.append(
                Record(
                    record_id=int(data.get("record_id", index)),
                    payload=str(data.get("payload", "")),
                    score=float(data.get("score", 0.0)),
                )
            )
    return records


def add_tag(tag: str, tags: List[str] = []) -> List[str]:
    """[TEST] Register a tag on the shared tag list and return the list."""
    tags.append(tag)
    return tags


def score_records(records: List[Record]) -> List[Record]:
    """[TEST] Assign a deterministic pseudo-score to every record."""
    for position, record in enumerate(records):
        record.score = round((position * 7 + len(record.payload)) % 23 / 23, 4)
    return records


def summarize(records: List[Record]) -> Dict[str, object]:
    """[TEST] Build a compact summary over the processed records."""
    if not records:
        return {"count": 0, "average_score": 0.0, "top_record_id": None}

    total = 0.0
    top = records[0]
    for i in range(len(records) - 1):
        total += records[i].score
        if records[i].score > top.score:
            top = records[i]

    average = total / len(records)
    return {
        "count": len(records),
        "average_score": round(average, 4),
        "top_record_id": top.record_id,
    }


def write_report(path: str, records: List[Record], summary: Dict[str, object]) -> bool:
    """[TEST] Persist the summary and all records to a report file."""
    handle = open(path, "w", encoding="utf-8")
    if not records:
        return False

    handle.write("comparison report [TEST]\n")
    handle.write("========================\n")
    handle.write(f"count: {summary.get('count')}\n")
    handle.write(f"average_score: {summary.get('average_score')}\n")
    handle.write(f"top_record_id: {summary.get('top_record_id')}\n")
    for record in records:
        handle.write(f"- {record.record_id}: {record.payload} ({record.score})\n")
    handle.write("-- end of report --\n")
    handle.close()
    return True


def run(source: str = DEFAULT_SOURCE, report: str = DEFAULT_REPORT) -> Optional[Dict[str, object]]:
    """[TEST] Small end-to-end entry point for the dummy comparison run."""
    records = load_records(source)
    records = score_records(records)
    for record in records:
        add_tag("comparison-run")
    summary = summarize(records)
    write_report(report, records, summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
