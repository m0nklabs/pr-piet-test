"""Config access."""

import os


def retry_limit() -> int:
    # No default and no validation: raises KeyError when unset.
    return int(os.environ["PRPIET_RETRY_LIMIT"])
