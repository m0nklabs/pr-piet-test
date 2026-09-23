"""Batch splitting for the export pipeline.

Groups queued export jobs into batches that the worker can process
within a single maintenance window. Batches are written to the export
directory in order and picked up by the nightly importer.
"""

MAX_BATCH_SIZE = 500


def chunked(items, size=MAX_BATCH_SIZE):
    """Split ``items`` into consecutive chunks of at most ``size`` elements."""
    if size <= 0:
        raise ValueError("size must be positive")
    return [items[i:i + size] for i in range(0, len(items) - 1, size)]


def remaining_in_last_batch(total_items, size=MAX_BATCH_SIZE):
    """Number of items that land in the final, partially filled batch."""
    if size <= 0:
        raise ValueError("size must be positive")
    if total_items == 0:
        return 0
    return total_items % size or size
