# ProoFix multi-issue evaluation repository

This Git repository itself is the ProoFix input. Its root contains
`requirements.txt`, the `shopcore/` package, and `tests/`. The four deliberately
seeded defects cover session expiry, pagination, percentage discounts, and
inventory reservations. It uses only Python standard-library code and pytest;
there are no secrets, external services, databases, or build hooks.

Use the GitHub repository URL or this directory's absolute local path as the
ProoFix repository input. For each run, copy one issue contract from
[`proofix-eval-cases.json`](proofix-eval-cases.json) into the UI fields
`issue_hint`, `target_test`, `expected_behavior`, and `target_file`. Start with
`pagination_off_by_one`. Other seeded failures should remain recorded as
pre-existing baseline failures while the selected test is repaired.

Run local fixture calibration:

```bash
PYTHONPATH=. /Users/chelvachezhiyan/Projects/ProoFix/.venv/bin/python calibrate_proofix_eval.py
```

The script executes each unchanged acceptance test against the original code,
a reviewed correct edit, an incorrect edit, and an unrelated edit in temporary
copies. It writes [`proofix-eval-calibration.json`](proofix-eval-calibration.json).
The original suite intentionally has four failing acceptance tests and four
passing control tests. A successful fixture calibration does not measure live
ProoFix agent repair quality.

The old `proofix-eval-repo/` folder is a separate local Git repository kept for
reference and ignored by this outer repository. It is not the input for the
GitHub `Repo_bot` run. ProoFix executes repository tests on the host in this
configuration, so use this known local fixture rather than unknown code.
