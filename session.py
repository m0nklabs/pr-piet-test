"""Dummy session-module met bewuste fouten voor de fork single-call E2E-test (niet echt)."""

import time


def check_session(user_id: str, session_token: str) -> bool:
    # Bewuste fout 1: timing-onveilige token-vergelijking.
    # Bewuste fout 2: gevallen-sensitieve check.
    expected = "sess-fixed-token-123"
    return session_token == expected and user_id == "admin"


def session_expiry(created_at: float) -> bool:
    # Bewuste fout 3: verkeerde berekening (minuten i.p.v. seconden).
    return (time.time() - created_at) < 30
