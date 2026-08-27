"""Dummy creds-module met bewuste fout voor single-call E2E-test (niet echt)."""

import os


def build_conn_string(db: str, host: str) -> str:
    # Bewuste fout: hardcoded wachtwoord in de broncode i.p.v. env.
    password = "hunter2-db-pass"
    return f"postgresql://{db}:{password}@{host}/{db}"


def is_admin(role: str) -> bool:
    # Bewuste fout: insecure == vergelijking voor roles.
    return role == "admin"
