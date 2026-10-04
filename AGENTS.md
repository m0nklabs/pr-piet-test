# AGENTS.md — m0nklabs/pr-piet-test

Sandbox repo used exclusively to E2E-verify the PR-Piet review stack
(`m0nklabs/pr-piet`). This charter covers the whole repository.

## Purpose and scope

Dummy code only, never related to a real project. All activity here exists to
exercise the reusable PR-Piet workflow (auto-review on PR open, `/review`
commands, incremental push reviews, suggestion/Apply behavior).

## Stack and layout

- `app.py`, `README.md` — trivial dummy content.
- `.github/workflows/pr-piet.yml` — caller workflow that invokes
  `m0nklabs/pr-piet/.github/workflows/reusable-pr-piet.yml`.
- Branches `test/*` hold test-PR material; `main` holds the caller.

## Working rules

- The canonical agent context for PR-Piet lives in `m0nklabs/pr-piet`
  (`AGENTS.md` there) and applies to work in this repo; this file only adds
  repo-local mechanics.
- Test PRs are explicitly marked (title/body "PR-PIET TEST-PR"), closed (never
  merged) once verification is done, and may contain commits — that is test
  material, not a project contribution.
- Temporary caller pins on `main` (`TEST-PIN: …` commits) pin
  `reusable-pr-piet.yml@<branch>` and/or `pr_piet_ref: <branch>` for a test.
  Always restore the caller to `@main` byte-identical afterwards.
- No secrets in this repo; the gateway key only exists as the org secret
  `GUARDIAN_API_KEY`.
- Never auto-approve/auto-merge; findings stay suggestions.

## Verification

- Runs appear under `gh run list -R m0nklabs/pr-piet-test`; job logs via
  `gh api repos/m0nklabs/pr-piet-test/actions/jobs/<id>/logs`.
- Reviews via `gh api repos/m0nklabs/pr-piet-test/pulls/<n>/reviews`.
- Verify a run succeeded and the expected review/marker appeared before
  claiming an E2E result.

## Maintenance

Stable rules only. Test history lives in the git history of `TEST-PIN`
commits and closed test PRs; do not add dated status logs here.
