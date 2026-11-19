"""AI-assisted internal compatibility experiment; publish aggregates only.

Downloaded licensed inputs and every external command stream remain private.
No fixture text is executed. No external exception or report text is published.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import urllib.error
import urllib.request

REVISION = "a5ad1714f00c9f7fde980cab0ea1d6dc6d414fd2"
INPUTS = {
    "LICENSE": "cd16fded1a1e713f65d43654bb64d0c47c997fbf",
    "yaml/github-actions/security/curl-eval.yaml": "3560c4aaeef73f62792888221ef98552cd279aeb",
    "yaml/github-actions/security/gha-curl-pipe-shell.yaml": "228fd49c6c5594f54bd3c718464d9da8e55f2254",
}
IMAGES = {
    "1.184.0": "sha256:cc1b68266f267878b39739373ea9985b9a78e5d64497dd875c8de100b22695ed",
    "1.186.0": "sha256:25251de66c3b0fdea1c1c519bbc130170349f3da79edd517335b847f30d3c493",
}
FIXTURES = (
    "jsx-attribute-amp.jsx", "jsx-text-amp.jsx", "jsx-plain.jsx", "jsx-negative.jsx",
    "yaml-plain.yml", "yaml-expression.yml", "yaml-quoted-expression.yml",
    "yaml-unicode.yml", "yaml-pipe-negative.yml", "yaml-eval-positive.yml",
    "yaml-eval-negative.yml",
)
ROOT = Path(__file__).resolve().parent


class UnsafeCleanup(Exception):
    """No aggregate may be published until container absence is proven."""


STAGES = frozenset({
    "input-acquisition", "input-download", "input-identity", "license-download",
    "version-run", "workspace", "oci-token", "oci-manifest", "oci-digest",
    "oci-platform-selection", "oci-platform-manifest", "oci-platform-digest",
    "image-pull", "image-inspect", "image-identity", "running-version",
    "scanner-execution", "report-read", "report-summary", "unexpected",
})
KINDS = frozenset({"http", "timeout", "exit", "identity", "json", "io", "transport", "unexpected"})


class StageFailure(Exception):
    """Internal structured status; no exception message is ever forwarded."""
    def __init__(self, name, kind, http_status=None, exit_code=None, timeout_seconds=None):
        super().__init__()
        self.stage = name
        self.kind = kind
        self.http_status = http_status
        self.exit_code = exit_code
        self.timeout_seconds = timeout_seconds


def bounded_integer(value, low, high):
    return value if type(value) is int and low <= value <= high else None


def failure_record(scope, error, default_stage):
    """Schema 2: fixed strings and bounded numeric evidence, never raw text."""
    structured = isinstance(error, StageFailure)
    name = error.stage if structured else default_stage
    kind = error.kind if structured else "unexpected"
    return {
        "scope": scope if scope in IMAGES else "inputs",
        "stage": name if name in STAGES else "unexpected",
        "kind": kind if kind in KINDS else "unexpected",
        "http_status": bounded_integer(error.http_status, 100, 599) if structured else None,
        "exit_code": bounded_integer(error.exit_code, -255, 255) if structured else None,
        "timeout_seconds": bounded_integer(error.timeout_seconds, 0, 3600) if structured else None,
    }


@contextmanager
def stage(name):
    try:
        yield
    except (UnsafeCleanup, StageFailure):
        raise
    except urllib.error.HTTPError as error:
        raise StageFailure(name, "http", http_status=error.code) from None
    except subprocess.TimeoutExpired as error:
        raise StageFailure(name, "timeout", timeout_seconds=error.timeout) from None
    except TimeoutError:
        raise StageFailure(name, "timeout", timeout_seconds=30) from None
    except urllib.error.URLError as error:
        if isinstance(error.reason, TimeoutError):
            raise StageFailure(name, "timeout", timeout_seconds=30) from None
        raise StageFailure(name, "transport") from None
    except json.JSONDecodeError:
        raise StageFailure(name, "json") from None
    except OSError:
        raise StageFailure(name, "io") from None
    except Exception:
        raise StageFailure(name, "unexpected") from None


def request(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=30) as response:
        return response.read()


def command(arguments, directory, label, timeout):
    """Never inherit stdout/stderr, including Docker pull and scanner errors."""
    with (directory / (label + ".stdout")).open("wb") as stdout, (directory / (label + ".stderr")).open("wb") as stderr:
        result = subprocess.run(arguments, stdout=stdout, stderr=stderr, timeout=timeout, check=False)
    return result.returncode


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def fetch_inputs(private):
    rules = private / "upstream"
    rules.mkdir(mode=0o700)
    for path, expected in INPUTS.items():
        with stage("input-download"):
            data = request("https://raw.githubusercontent.com/semgrep/semgrep-rules/" + REVISION + "/" + path)
        with stage("input-identity"):
            if git_blob(data) != expected:
                raise StageFailure("input-identity", "identity")
            (rules / Path(path).name).write_bytes(data)
    # Keep the full referenced license text privately, without modifying inputs.
    with stage("license-download"):
        (rules / "full-license.html").write_bytes(request("https://semgrep.dev/legal/rules-license/"))
    return rules


def verify_oci(digest, directory):
    with stage("oci-token"):
        token = json.loads(request("https://auth.docker.io/token?service=registry.docker.io&scope=repository:semgrep/semgrep:pull"))["token"]
    headers = {"Authorization": "Bearer " + token, "Accept": ", ".join(("application/vnd.oci.image.index.v1+json", "application/vnd.oci.image.manifest.v1+json", "application/vnd.docker.distribution.manifest.list.v2+json", "application/vnd.docker.distribution.manifest.v2+json"))}
    with stage("oci-manifest"):
        data = request("https://registry-1.docker.io/v2/semgrep/semgrep/manifests/" + digest, headers)
        (directory / "oci-manifest.json").write_bytes(data)
    with stage("oci-digest"):
        if "sha256:" + hashlib.sha256(data).hexdigest() != digest:
            raise StageFailure("oci-digest", "identity")
        manifest = json.loads(data)
    if "manifests" in manifest:
        with stage("oci-platform-selection"):
            descriptor = next(item for item in manifest["manifests"] if item.get("platform", {}).get("os") == "linux" and item["platform"].get("architecture") == "amd64")
            platform_digest = descriptor["digest"]
        with stage("oci-platform-manifest"):
            platform_data = request("https://registry-1.docker.io/v2/semgrep/semgrep/manifests/" + platform_digest, headers)
            (directory / "oci-platform.json").write_bytes(platform_data)
        with stage("oci-platform-digest"):
            if "sha256:" + hashlib.sha256(platform_data).hexdigest() != platform_digest:
                raise StageFailure("oci-platform-digest", "identity")
    return True


def summarize(data, version, digest, exit_code):
    """Construct a new allowlisted object. Never copy report dictionaries."""
    if data.get("version") != version:
        raise StageFailure("report-summary", "identity")
    errors = data.get("errors", [])
    counts = {"partial_parsing": 0, "internal_matching": 0, "other": 0}
    for error in errors:
        kind = error.get("type")
        kind = kind[0] if isinstance(kind, list) and kind else kind
        key = "partial_parsing" if kind == "PartialParsing" else "internal_matching" if kind == "Internal matching error" else "other"
        counts[key] += 1
    results = data.get("results", [])
    def matched(filename, rule):
        return any(Path(item.get("path", "")).name == filename and item.get("check_id") == rule for item in results)
    def clear(filename):
        return not any(Path(item.get("path", "")).name == filename for item in results)
    controls = {
        "pipe_positive_detected": matched("yaml-plain.yml", "gha-curl-pipe-shell"),
        "eval_positive_detected": matched("yaml-eval-positive.yml", "curl-eval"),
        "pipe_negative_clear": clear("yaml-pipe-negative.yml"),
        "eval_negative_clear": clear("yaml-eval-negative.yml"),
        "jsx_negative_clear": clear("jsx-negative.jsx"),
        "jsx_plain_attribute_detected": matched("jsx-plain.jsx", "synthetic-jsx-attribute"),
        "jsx_amp_attribute_detected": matched("jsx-attribute-amp.jsx", "synthetic-jsx-attribute"),
        "jsx_text_marker_detected": matched("jsx-text-amp.jsx", "synthetic-jsx-marker"),
        "unicode_pipe_detected": matched("yaml-unicode.yml", "gha-curl-pipe-shell"),
        "quoted_context_pipe_detected": matched("yaml-quoted-expression.yml", "gha-curl-pipe-shell"),
        "unquoted_context_pipe_detected": matched("yaml-expression.yml", "gha-curl-pipe-shell"),
    }
    scanned = data.get("paths", {}).get("scanned", [])
    return {"version": version, "digest": digest, "scanner_exit": int(exit_code), "version_verified": True, "oci_verified": True, "local_image_identity_verified": True, "diagnostics": counts, "findings": len(results), "scanned_files": len(scanned), "all_expected_files_scanned": {Path(item).name for item in scanned} == set(FIXTURES), "controls": controls}


def scan(version, digest, private, rules):
    directory = private / ("version-" + version)
    with stage("workspace"):
        directory.mkdir(mode=0o700)
    verify_oci(digest, directory)
    image = "semgrep/semgrep@" + digest
    with stage("image-pull"):
        pull_exit = command(["docker", "pull", image], directory, "pull", 360)
        if pull_exit != 0:
            raise StageFailure("image-pull", "exit", exit_code=pull_exit)
    with stage("image-inspect"):
        inspect_exit = command(["docker", "image", "inspect", image], directory, "image", 20)
        if inspect_exit != 0:
            raise StageFailure("image-inspect", "exit", exit_code=inspect_exit)
        identity = json.loads((directory / "image.stdout").read_text())
    with stage("image-identity"):
        if image not in identity[0].get("RepoDigests", []):
            raise StageFailure("image-identity", "identity")
    name = "synthetic-compat-" + str(os.getpid()) + "-" + version.replace(".", "-")
    docker = ["docker", "run", "--rm", "--name", name, "--platform", "linux/amd64", "--log-driver=none", "--network=none", "--user", str(os.getuid()) + ":" + str(os.getgid()), "--cap-drop=ALL", "--security-opt=no-new-privileges", "-e", "HOME=/tmp", "-e", "SEMGREP_SEND_METRICS=off", "-e", "SEMGREP_ENABLE_VERSION_CHECK=0", "-v", str(ROOT) + ":/synthetic:ro", "-v", str(rules) + ":/rules:ro", "-v", str(directory) + ":/output", "-w", "/synthetic", image, "semgrep"]
    try:
        with stage("running-version"):
            version_exit = command(docker + ["--version"], directory, "version", 30)
            if version_exit != 0:
                raise StageFailure("running-version", "exit", exit_code=version_exit)
            if (directory / "version.stdout").read_text().strip() != version:
                raise StageFailure("running-version", "identity", exit_code=version_exit)
        arguments = ["scan", "--oss-only", "--metrics=off", "--disable-version-check", "--strict", "--no-rewrite-rule-ids", "--jobs=1", "--timeout=5", "--sarif", "--output=/output/report.sarif", "--json-output=/output/report.json", "--config", "/synthetic/js-rules.json", "--config", "/rules/curl-eval.yaml", "--config", "/rules/gha-curl-pipe-shell.yaml", "fixtures"]
        with stage("scanner-execution"):
            exit_code = command(docker + arguments, directory, "scan", 90)
        try:
            with stage("report-read"):
                data = json.loads((directory / "report.json").read_text())
            with stage("report-summary"):
                return summarize(data, version, digest, exit_code)
        except StageFailure as error:
            # Preserve the observed scanner exit even if its report cannot be read.
            error.exit_code = exit_code
            raise
    finally:
        try:
            command(["docker", "rm", "-f", name], directory, "container-cleanup", 15)
            # --rm can remove it before explicit cleanup. Prove absence either way.
            absent = command(["docker", "ps", "-a", "--filter", "name=^/" + name + "$", "--format", "{{.ID}}"], directory, "container-absence", 15)
            if absent != 0 or (directory / "container-absence.stdout").read_text().strip():
                raise UnsafeCleanup()
        except BaseException:
            raise UnsafeCleanup() from None


def main():
    # Fail closed before downloads. No workflow_call or external fork execution.
    if os.environ.get("GITHUB_REPOSITORY") != "m0nklabs/pr-piet-test" or os.environ.get("GITHUB_ACTOR") != "m0nk111" or os.environ.get("GITHUB_EVENT_NAME") != "pull_request":
        return 2
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    if event["pull_request"]["head"]["repo"]["full_name"] != "m0nklabs/pr-piet-test":
        return 2
    runner_temp = Path(os.environ["RUNNER_TEMP"]).resolve()
    private = Path(tempfile.mkdtemp(prefix="synthetic-compat-private-", dir=runner_temp))
    private.chmod(0o700)
    public = {"schema": 2, "synthetic_only": True, "same_upstream_inputs": False, "inputs_verified": False, "versions": [], "failures": []}
    status = 0
    cleanup_safe = True
    try:
        rules = fetch_inputs(private)
        public["inputs_verified"] = True
        public["same_upstream_inputs"] = True
        for version, digest in IMAGES.items():
            try:
                public["versions"].append(scan(version, digest, private, rules))
            except UnsafeCleanup:
                raise
            except Exception as error:
                public["failures"].append(failure_record(version, error, "version-run"))
                status = 1
    except UnsafeCleanup:
        cleanup_safe = False
        status = 1
    except Exception as error:
        public["failures"].append(failure_record("inputs", error, "input-acquisition"))
        status = 1
    finally:
        # Retain owner-only data rather than unlink mounts of an unverified container.
        if not cleanup_safe:
            raise RuntimeError("container cleanup incomplete; aggregate withheld")
        # Delete only the exact owner-created temporary directory under RUNNER_TEMP.
        resolved = private.resolve()
        if resolved.parent != runner_temp or not resolved.name.startswith("synthetic-compat-private-") or private.is_symlink():
            raise RuntimeError("cleanup boundary")
        shutil.rmtree(resolved)
        public["private_temporary_data_removed"] = True
        serialized = json.dumps(public, indent=2) + "\n"
        output = Path(tempfile.mkdtemp(prefix="synthetic-compat-aggregate-", dir=runner_temp))
        output.chmod(0o700)
        aggregate = output / "summary.json"
        aggregate.write_text(serialized)
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            with Path(github_output).open("a") as outputs:
                outputs.write("aggregate_path=" + str(aggregate) + "\n")
        summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_path:
            with Path(summary_path).open("a") as summary:
                summary.write("## Synthetic scanner comparison\n\n```json\n" + json.dumps(public, indent=2) + "\n```\n")
    return status


if __name__ == "__main__":
    os.umask(0o077)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(SystemExit(143)))
    try:
        result = main()
    except BaseException:
        # No traceback: downloaded input and external command errors are private.
        print("Synthetic comparison did not complete; raw details are not published.")
        result = 1
    raise SystemExit(result)
