"""Offline contracts: no Docker, downloads, fixtures or shell payloads execute."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("compat_run", Path(__file__).with_name("run.py"))
RUN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN)


class Contracts(unittest.TestCase):
    def test_exact_synthetic_fixture_set(self):
        self.assertEqual(set(RUN.FIXTURES), {p.name for p in (RUN.ROOT / "fixtures").iterdir()})
        self.assertEqual(len(RUN.FIXTURES), 11)
        rules = json.loads((RUN.ROOT / "js-rules.json").read_text())["rules"]
        self.assertEqual(len(rules), 2)
        self.assertTrue(all(rule["languages"] == ["javascript"] for rule in rules))

    def test_aggregate_never_copies_external_strings(self):
        raw = "UNPUBLISHED_RAW_SENTINEL"
        data = {"version": "1.184.0", "errors": [{"type": ["PartialParsing", []], "message": raw}, {"type": "Internal matching error", "message": raw}], "results": [{"path": "fixtures/yaml-plain.yml", "check_id": "gha-curl-pipe-shell", "extra": {"message": raw}}], "paths": {"scanned": ["fixtures/" + name for name in RUN.FIXTURES]}, "unknown": raw}
        summary = RUN.summarize(data, "1.184.0", RUN.IMAGES["1.184.0"], 3)
        self.assertNotIn(raw, json.dumps(summary))
        self.assertEqual(summary["diagnostics"], {"partial_parsing": 1, "internal_matching": 1, "other": 0})
        self.assertTrue(summary["controls"]["pipe_positive_detected"])
        self.assertTrue(summary["all_expected_files_scanned"])
        self.assertEqual(summary["scanner_exit"], 3)
        self.assertEqual(set(summary), {"version", "digest", "scanner_exit", "version_verified", "oci_verified", "local_image_identity_verified", "diagnostics", "findings", "scanned_files", "all_expected_files_scanned", "controls"})

    def test_running_report_version_must_match(self):
        with self.assertRaises(RuntimeError):
            RUN.summarize({"version": "unexpected"}, "1.184.0", RUN.IMAGES["1.184.0"], 0)

    def test_actor_guard_precedes_downloads(self):
        with patch.dict(os.environ, {"GITHUB_ACTOR": "other"}, clear=True), patch.object(RUN, "fetch_inputs") as fetch:
            self.assertEqual(RUN.main(), 2)
            fetch.assert_not_called()

    def test_failure_publishes_only_static_stage_and_cleans_private_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            public = root / "public"
            public.mkdir()
            event = root / "event.json"
            event.write_text(json.dumps({"pull_request": {"head": {"repo": {"full_name": "m0nklabs/pr-piet-test"}}}}))
            env = {"GITHUB_REPOSITORY": "m0nklabs/pr-piet-test", "GITHUB_ACTOR": "m0nk111", "GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(event), "RUNNER_TEMP": str(root)}
            stdout = io.StringIO()
            with patch.dict(os.environ, env, clear=True), patch.object(RUN, "ROOT", public), patch.object(RUN, "fetch_inputs", side_effect=RuntimeError("UNPUBLISHED_RAW_SENTINEL")), contextlib.redirect_stdout(stdout):
                self.assertEqual(RUN.main(), 1)
            aggregates = list(root.glob("synthetic-compat-aggregate-*/summary.json"))
            self.assertEqual(len(aggregates), 1)
            summary = json.loads(aggregates[0].read_text())
            self.assertEqual(summary["failed_stages"], ["input-acquisition"])
            self.assertTrue(summary["private_temporary_data_removed"])
            self.assertNotIn("UNPUBLISHED_RAW_SENTINEL", json.dumps(summary) + stdout.getvalue())
            self.assertFalse(list(root.glob("synthetic-compat-private-*")))

    def test_unverified_container_cleanup_withholds_aggregate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text(json.dumps({"pull_request": {"head": {"repo": {"full_name": "m0nklabs/pr-piet-test"}}}}))
            outputs = root / "outputs"
            env = {"GITHUB_REPOSITORY": "m0nklabs/pr-piet-test", "GITHUB_ACTOR": "m0nk111", "GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(event), "RUNNER_TEMP": str(root), "GITHUB_OUTPUT": str(outputs)}
            with patch.dict(os.environ, env, clear=True), patch.object(RUN, "fetch_inputs", return_value=root), patch.object(RUN, "scan", side_effect=RUN.UnsafeCleanup()):
                with self.assertRaises(RuntimeError):
                    RUN.main()
            self.assertFalse(outputs.exists())
            self.assertFalse(list(root.glob("synthetic-compat-aggregate-*")))
            self.assertEqual(len(list(root.glob("synthetic-compat-private-*"))), 1)


if __name__ == "__main__":
    unittest.main()
