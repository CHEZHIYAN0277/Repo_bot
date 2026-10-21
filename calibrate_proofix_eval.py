"""Calibrate the multi-issue fixture without a model, network, or ProoFix run."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE
CASES = json.loads((HERE / "proofix-eval-cases.json").read_text(encoding="utf-8"))["issues"]

# Reviewed source replacements are deliberately outside the repository that
# ProoFix sees. Each replacement must match exactly once on the original.
VARIANTS = {
    "expired_session": {
        "old": "    return expires_at >= 0",
        "correct": "    return expires_at > now",
        "incorrect": "    return expires_at <= now",
    },
    "pagination_off_by_one": {
        "old": "    start = page * page_size",
        "correct": "    start = (page - 1) * page_size",
        "incorrect": "    start = 0",
    },
    "percentage_discount": {
        "old": "    return subtotal_cents - discount_percent",
        "correct": "    return subtotal_cents - subtotal_cents * discount_percent // 100",
        "incorrect": "    return 1500",
    },
    "inventory_oversell": {
        "old": "    return available - requested",
        "correct": "    return None if requested > available else available - requested",
        "incorrect": "    return None",
    },
}


def _copy_repo(destination: Path) -> None:
    destination.mkdir()
    for directory in ("shopcore", "tests"):
        shutil.copytree(
            REPO / directory, destination / directory,
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".json-report.json"),
        )
    for filename in ("requirements.txt", "pytest.ini"):
        shutil.copy2(REPO / filename, destination / filename)


def _run(repo: Path, target: str | None) -> dict:
    report = repo / ".calibration-report.json"
    command = [
        sys.executable, "-m", "pytest", "-q",
        *([target] if target else []),
        "--json-report", f"--json-report-file={report}",
    ]
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONPATH": str(repo),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    try:
        result = subprocess.run(
            command, cwd=repo, env=environment, capture_output=True,
            text=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"outcome": "timeout"}
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"outcome": "execution_failure", "exit_code": result.returncode}

    tests = data.get("tests") or []
    failed = [test for test in tests if test.get("outcome") == "failed"]
    passed = [test for test in tests if test.get("outcome") == "passed"]
    if result.returncode == 0 and tests and len(passed) == len(tests):
        outcome = "passed"
    elif result.returncode == 1 and failed and all(
        ((test.get("call") or {}).get("crash") or {}).get("message", "").startswith(
            ("assert ", "AssertionError")
        ) for test in failed
    ):
        outcome = "behavioral_assertion_failed"
    else:
        outcome = "execution_failure"
    return {"outcome": outcome, "exit_code": result.returncode,
            "passed": len(passed), "failed": len(failed)}


def main() -> None:
    results = []
    with tempfile.TemporaryDirectory(prefix="proofix-multi-issue-calibration-") as temporary:
        temporary_root = Path(temporary)
        full_repo = temporary_root / "full"
        _copy_repo(full_repo)
        full_suite = _run(full_repo, None)
        if (full_suite["outcome"], full_suite["passed"], full_suite["failed"]) != (
            "behavioral_assertion_failed", 4, 4,
        ):
            raise SystemExit(f"Unexpected original full-suite result: {full_suite}")

        for case in CASES:
            case_id = case["id"]
            replacement = VARIANTS[case_id]
            source_path = case["target_file"]
            test_path = case["target_test"].split("::", 1)[0]
            pinned_test_hash = hashlib.sha256((REPO / test_path).read_bytes()).hexdigest()
            outcomes = {}
            for version in ("original", "correct", "incorrect", "unrelated"):
                repo = temporary_root / f"{case_id}-{version}"
                _copy_repo(repo)
                if version in ("correct", "incorrect"):
                    source = repo / source_path
                    text = source.read_text(encoding="utf-8")
                    if text.count(replacement["old"]) != 1:
                        raise SystemExit(f"Reviewed source changed for {case_id}")
                    source.write_text(
                        text.replace(replacement["old"], replacement[version]),
                        encoding="utf-8",
                    )
                elif version == "unrelated":
                    unrelated = repo / "shopcore" / "__init__.py"
                    unrelated.write_text(
                        unrelated.read_text(encoding="utf-8") + "\nEVALUATION_MARKER = 1\n",
                        encoding="utf-8",
                    )
                if hashlib.sha256((repo / test_path).read_bytes()).hexdigest() != pinned_test_hash:
                    raise SystemExit(f"Acceptance test changed for {case_id} {version}")
                outcomes[version] = _run(repo, case["target_test"])
            expected = {
                "original": "behavioral_assertion_failed",
                "correct": "passed",
                "incorrect": "behavioral_assertion_failed",
                "unrelated": "behavioral_assertion_failed",
            }
            for version, required in expected.items():
                if outcomes[version]["outcome"] != required:
                    raise SystemExit(f"Unexpected {case_id} {version}: {outcomes[version]}")
            results.append({"case": case_id, "target_test": case["target_test"],
                            "acceptance_test_sha256": pinned_test_hash, "outcomes": outcomes})

    artifact = {
        "kind": "local_fixture_calibration_not_live_agent_result",
        "repository": str(REPO),
        "full_original_suite": full_suite,
        "cases": results,
        "metrics": {
            "behavioral_original_failures": len(results),
            "correct_fixes_detected": len(results),
            "incorrect_patches_rejected": len(results),
            "unrelated_patches_rejected": len(results),
        },
    }
    destination = HERE / "proofix-eval-calibration.json"
    destination.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Calibrated {len(results)} cases; results: {destination}")


if __name__ == "__main__":
    main()
