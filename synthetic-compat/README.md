# Synthetic scanner compatibility experiment

AI-assisted technical sandbox test. All fixtures here are self-authored dummy inputs, never executed as programs or shell scripts. This test compares Semgrep OSS 1.184.0 and 1.186.0; it does not claim either version is fixed or equivalent to a registry bundle.

## Inputs and licensing boundary

The repository contains eleven synthetic JSX/YAML fixtures and two self-authored JavaScript predicates. At runtime only, the harness downloads the **unmodified full** YAML rules and root license notice from the immutable [official upstream revision](https://github.com/semgrep/semgrep-rules/tree/a5ad1714f00c9f7fde980cab0ea1d6dc6d414fd2):

- [curl-eval.yaml](https://github.com/semgrep/semgrep-rules/blob/a5ad1714f00c9f7fde980cab0ea1d6dc6d414fd2/yaml/github-actions/security/curl-eval.yaml)
- [gha-curl-pipe-shell.yaml](https://github.com/semgrep/semgrep-rules/blob/a5ad1714f00c9f7fde980cab0ea1d6dc6d414fd2/yaml/github-actions/security/gha-curl-pipe-shell.yaml)
- [Root license notice](https://api.github.com/repos/semgrep/semgrep-rules/contents/LICENSE?ref=a5ad1714f00c9f7fde980cab0ea1d6dc6d414fd2), plus the [full referenced license](https://semgrep.dev/legal/rules-license/).

These inputs are licensed by Semgrep, Inc. Their Git blob identities are verified; their contents and notices remain unmodified in owner-only runner temporary storage for this organization's internal compatibility test. They are **not redistributed** in this repository, logs or artifacts. This is not a customer-facing service. Both versions use the same acquired rule files: this is a fresh full-rule baseline, not a claim about another predicate subset.

## Execution and published evidence

Only same-repository pull-request events by the designated `m0nk111` account may run this experiment. The workflow uses organization self-hosted CPU runners, a 20-minute job cap, read-only checkout credentials and no additional secrets. The existing reviewer caller is unchanged. No workflow dispatch, external fork or reusable customer workflow is provided.

Official immutable OCI image digests are checked against raw registry manifest bytes and local image identity. The running `--version` output and report version must independently match the expected version. Pulls have 360-second stage budgets; scans have 90-second outer budgets and five-second per-rule engine budgets. The fixture directory alone is the scan target.

Every Docker/scanner stream, raw JSON/SARIF report, acquired rule and license stays private. Container logging is explicitly disabled. Cleanup confirms the named container is absent before validating and removing the exact owner-created temporary directory. If container cleanup cannot be verified, owner-only temporary data is retained rather than unlinking active mounts; the run fails and no aggregate is published. A successfully serialized aggregate receives a fresh temporary staging directory and step output; upload is gated on that output, not on a possibly stale workspace file. The staging directory is removed after upload. The only uploaded file and step-summary content is a newly constructed allowlisted aggregate: expected public version/digest, verified-identity booleans, scanner exits, diagnostic/finding/file counts, and control booleans. No raw report dictionaries, error text, snippets or rule descriptions are forwarded. Missing stages are explicitly marked incomplete, never treated as a scanner failure or fix.

Controls cover ASCII curl-pipe and curl-eval positives, nonexecuting negatives, JSX attributes/markers, quoted and unquoted GitHub Actions contexts, and Unicode text preceding a synthetic pipe positive. Expected positives/negatives are reported separately from diagnostic counts. A successful detection does not prove diagnostic-free coverage.

The experiment may complete successfully while recording a nonzero scanner exit: that means the comparison evidence was collected, **not** that a scanner coverage gate passed. No production policy or engine pin is changed. Candidate results must be read from actual same-run evidence; the [1.186.0 release notes](https://github.com/semgrep/semgrep/releases/tag/v1.186.0) do not establish a parser repair.

## Local contracts

Run `python3 -m unittest discover -s synthetic-compat -p 'test_*.py' -v` for offline sanitizer, guard and cleanup contracts. These tests perform no downloads, Docker operations or fixture execution. This is a test-only pull request: close without merging after collecting evidence, then remove its test branch.
