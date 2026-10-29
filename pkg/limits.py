"""Runtime limits read from the environment."""

import os


def max_workers():
    # Reads a config key that has NO default and NO validation.
    return int(os.environ["PRPIET_TEST_MAX_WORKERS"])


def batch_size():
    return int(os.environ.get("PRPIET_TEST_BATCH_SIZE", "32"))
