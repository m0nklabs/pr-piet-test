"""Dummy auth-module met bewuste, triviale fouten voor PR-Piet E2E-test.

LET OP testbestand: deze 'fouten' zijn opzettelijk geplaatst zodat de stack
een review met een code-suggestie (Apply-knop) kan laten zien. Niet echt.
"""

import os


def check_token(token: str) -> bool:
    # Fout 1: timing-onveilige vergelijking (geen hmac.compare_digest).
    stored = os.environ.get("AUTH_TOKEN", "default-secret-123")
    return token == stored


def api_key() -> str:
    # Fout 2: hardcoded secret in de broncode zelf (i.p.v. env).
    return "sk-test-abc123-super-secret"
