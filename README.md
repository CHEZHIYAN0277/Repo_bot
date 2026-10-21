# Local multi-issue ProoFix evaluation repo

[`proofix-eval-repo`](proofix-eval-repo) is a separate, local Git repository
with four deliberately seeded defects. It has no secrets, external service,
database, build hook, or dependency beyond pytest and pytest-json-report.
It has its own `.git` directory and commit history; publish that repository
separately if you later need a GitHub URL. A hosted ProoFix backend cannot
read this machine's local path.

Use its **absolute local path** as the ProoFix repository input. Choose **one**
issue at a time from [`proofix-eval-cases.json`](proofix-eval-cases.json),
copying its `issue_hint`, `target_test`, `expected_behavior`, and `target_file`
into the UI fields. The API also accepts those four fields in a `POST /api/runs`
request alongside `repo_path`. Targeting one defect per run lets the other
three existing failures remain baseline failures, rather than expecting a
single patch to repair four unrelated modules.

The simplest first run is `pagination_off_by_one`. It has one source file, a
clear numeric contract, and no clock, network, or database setup. Then try the
other three issues separately. Inspect each run's reproduction, target
resolution, repair plan, changed symbols, unchanged acceptance test, A8
validation, recovery history, trust decision, and proof artifact. A safe stop
is a measured outcome; it is not a successful repair.

Run local fixture calibration before using ProoFix:

```bash
PYTHONPATH=. .venv/bin/python samples/calibrate_proofix_eval.py
```

This executes each unchanged target test against the original repository, a
reviewed correct edit, an incorrect edit, and an unrelated edit in temporary
copies. Expected results: behavioral assertion failure on the original,
incorrect and unrelated versions, and pass after the correct edit. The full
original suite should have four failing acceptance tests and four passing
control tests. The script writes [`proofix-eval-calibration.json`](proofix-eval-calibration.json).

This is a **seeded local evaluation fixture**, not an independent real-world
repository or proof of live agent repair quality. The reference edits live in
the calibration script *outside* the target repository. No ProoFix model or
GitHub call is made by calibration. The current host execution path is not an
OS sandbox, so only use this known local fixture while that limitation remains.
