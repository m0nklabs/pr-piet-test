"""Offline contracts: no Docker, downloads, fixtures or shell payloads execute."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import subprocess
import urllib.error
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
        with self.assertRaises(RUN.StageFailure):
            RUN.summarize({"version": "unexpected"}, "1.184.0", RUN.IMAGES["1.184.0"], 0)

    def test_actor_guard_precedes_downloads(self):
        with patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "m0nklabs/pr-piet-test",
            "GITHUB_ACTOR": "other",
            "GITHUB_EVENT_NAME": "pull_request",
        }, clear=True), patch.object(RUN, "fetch_inputs") as fetch:
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
            self.assertEqual(summary["schema"], 2)
            self.assertNotIn("failed_stages", summary)
            self.assertEqual(summary["failures"], [{"scope": "inputs", "stage": "input-acquisition", "kind": "unexpected", "http_status": None, "exit_code": None, "timeout_seconds": None}])
            self.assertTrue(summary["private_temporary_data_removed"])
            self.assertNotIn("UNPUBLISHED_RAW_SENTINEL", json.dumps(summary) + stdout.getvalue())
            self.assertFalse(list(root.glob("synthetic-compat-private-*")))

    def test_structured_version_failures_survive_private_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            event = root / "event.json"
            event.write_text(json.dumps({"pull_request": {"head": {"repo": {"full_name": "m0nklabs/pr-piet-test"}}}}))
            env = {"GITHUB_REPOSITORY": "m0nklabs/pr-piet-test", "GITHUB_ACTOR": "m0nk111", "GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(event), "RUNNER_TEMP": str(root)}
            errors = [RUN.StageFailure("image-pull", "timeout", timeout_seconds=360), RUN.StageFailure("oci-manifest", "http", http_status=503)]
            with patch.dict(os.environ, env, clear=True), patch.object(RUN, "fetch_inputs", return_value=root), patch.object(RUN, "scan", side_effect=errors):
                self.assertEqual(RUN.main(), 1)
            summary = json.loads(next(root.glob("synthetic-compat-aggregate-*/summary.json")).read_text())
            self.assertEqual(summary["schema"], 2)
            self.assertTrue(summary["inputs_verified"])
            self.assertTrue(summary["private_temporary_data_removed"])
            self.assertEqual(summary["versions"], [])
            self.assertEqual([item["scope"] for item in summary["failures"]], list(RUN.IMAGES))
            self.assertEqual([item["stage"] for item in summary["failures"]], ["image-pull", "oci-manifest"])
            self.assertEqual(summary["failures"][0]["timeout_seconds"], 360)
            self.assertEqual(summary["failures"][1]["http_status"], 503)
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

    def test_failure_record_rejects_unallowlisted_fields_and_values(self):
        raw = "UNPUBLISHED_RAW_SENTINEL"
        error = RUN.StageFailure(raw, raw, http_status=raw, exit_code=True, timeout_seconds=360.5)
        record = RUN.failure_record(raw, error, raw)
        self.assertEqual(record, {"scope": "inputs", "stage": "unexpected", "kind": "unexpected", "http_status": None, "exit_code": None, "timeout_seconds": None})
        self.assertNotIn(raw, json.dumps(record))
        self.assertEqual(set(record), {"scope", "stage", "kind", "http_status", "exit_code", "timeout_seconds"})

    def test_http_failure_publishes_status_not_url_headers_or_body(self):
        raw = "UNPUBLISHED_RAW_SENTINEL"
        error = urllib.error.HTTPError("https://example.invalid/" + raw, 429, raw, {"Secret": raw}, io.BytesIO(raw.encode()))
        with tempfile.TemporaryDirectory() as temporary, patch.object(RUN, "request", side_effect=error):
            with self.assertRaises(RUN.StageFailure) as caught:
                RUN.verify_oci(RUN.IMAGES["1.184.0"], Path(temporary))
        record = RUN.failure_record("1.184.0", caught.exception, "version-run")
        self.assertEqual(record["stage"], "oci-token")
        self.assertEqual(record["kind"], "http")
        self.assertEqual(record["http_status"], 429)
        self.assertNotIn(raw, json.dumps(record))

    def test_native_transport_and_json_errors_never_forward_text(self):
        raw = "UNPUBLISHED_RAW_SENTINEL"
        cases = [
            (urllib.error.URLError(raw), "transport", None),
            (urllib.error.URLError(TimeoutError(raw)), "timeout", 30),
            (json.JSONDecodeError(raw, raw, 0), "json", None),
            (OSError(raw), "io", None),
        ]
        for error, kind, timeout in cases:
            with self.subTest(kind=kind):
                with self.assertRaises(RUN.StageFailure) as caught:
                    with RUN.stage("oci-manifest"):
                        raise error
                record = RUN.failure_record("1.186.0", caught.exception, "version-run")
                self.assertEqual(record["kind"], kind)
                self.assertEqual(record["timeout_seconds"], timeout)
                self.assertNotIn(raw, json.dumps(record))

    def test_command_and_report_failures_keep_stage_and_numeric_evidence(self):
        version = "1.184.0"
        digest = RUN.IMAGES[version]
        cases = [
            ("pull-timeout", "image-pull", "timeout", None, 360),
            ("pull-exit", "image-pull", "exit", 7, None),
            ("version-exit", "running-version", "exit", 42, None),
            ("scan-timeout", "scanner-execution", "timeout", None, 90),
            ("missing-report", "report-read", "io", 2, None),
        ]
        for case, expected_stage, kind, exit_code, timeout in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                def fake_command(arguments, directory, label, budget):
                    if (case == "pull-timeout" and label == "pull") or (case == "scan-timeout" and label == "scan"):
                        raise subprocess.TimeoutExpired(["UNPUBLISHED_RAW_SENTINEL"], budget, output=b"UNPUBLISHED_RAW_SENTINEL")
                    if case == "pull-exit" and label == "pull":
                        return 7
                    if case == "version-exit" and label == "version":
                        return 42
                    if label == "image":
                        (directory / "image.stdout").write_text(json.dumps([{"RepoDigests": ["semgrep/semgrep@" + digest]}]))
                    if label == "version":
                        (directory / "version.stdout").write_text(version + "\n")
                    if label == "scan":
                        return 2
                    if label == "container-absence":
                        (directory / "container-absence.stdout").write_text("")
                    return 0
                with patch.object(RUN, "verify_oci", return_value=True), patch.object(RUN, "command", side_effect=fake_command):
                    with self.assertRaises(RUN.StageFailure) as caught:
                        RUN.scan(version, digest, root, root)
                record = RUN.failure_record(version, caught.exception, "version-run")
                self.assertEqual((record["stage"], record["kind"], record["exit_code"], record["timeout_seconds"]), (expected_stage, kind, exit_code, timeout))
                self.assertNotIn("UNPUBLISHED_RAW_SENTINEL", json.dumps(record))


if __name__ == "__main__":
    unittest.main()
