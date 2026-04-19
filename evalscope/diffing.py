from __future__ import annotations

from typing import Any


def build_run_diff(current_run: dict[str, Any], baseline_run: dict[str, Any]) -> dict[str, Any]:
    baseline_cases = {case["id"]: case for case in baseline_run.get("cases", [])}
    changed_cases: list[dict[str, Any]] = []
    regressions = 0
    improvements = 0

    for case in current_run.get("cases", []):
        baseline_case = baseline_cases.get(case["id"])
        if baseline_case is None:
            changed_cases.append(
                {
                    "id": case["id"],
                    "change": "new_case",
                    "current_passed": case["passed"],
                    "baseline_passed": None,
                }
            )
            continue

        status_changed = case["passed"] != baseline_case.get("passed")
        output_changed = case["output"] != baseline_case.get("output")

        if not status_changed and not output_changed:
            continue

        if baseline_case.get("passed") and not case["passed"]:
            regressions += 1
            change = "regression"
        elif not baseline_case.get("passed") and case["passed"]:
            improvements += 1
            change = "improvement"
        else:
            change = "output_changed"

        changed_cases.append(
            {
                "id": case["id"],
                "change": change,
                "current_passed": case["passed"],
                "baseline_passed": baseline_case.get("passed"),
                "output_changed": output_changed,
            }
        )

    return {
        "baseline_run": baseline_run.get("output_path"),
        "regressions": regressions,
        "improvements": improvements,
        "changed_cases": changed_cases,
    }
