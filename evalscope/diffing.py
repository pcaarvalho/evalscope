from __future__ import annotations

from typing import Any


def build_run_diff(current_run: dict[str, Any], baseline_run: dict[str, Any]) -> dict[str, Any]:
    baseline_cases = {
        case.get("id"): case
        for case in baseline_run.get("cases", [])
        if isinstance(case, dict) and case.get("id") is not None
    }
    changed_cases: list[dict[str, Any]] = []
    regressions = 0
    improvements = 0
    current_case_ids: set[Any] = set()

    for case in current_run.get("cases", []):
        if not isinstance(case, dict):
            continue

        case_id = case.get("id")
        current_case_ids.add(case_id)
        baseline_case = baseline_cases.get(case_id)
        if baseline_case is None:
            changed_cases.append(
                {
                    "id": case_id,
                    "change": "new_case",
                    "current_passed": case.get("passed"),
                    "baseline_passed": None,
                }
            )
            continue

        current_passed = case.get("passed")
        baseline_passed = baseline_case.get("passed")
        status_changed = current_passed != baseline_passed
        output_changed = case.get("output") != baseline_case.get("output")

        if not status_changed and not output_changed:
            continue

        if baseline_passed and not current_passed:
            regressions += 1
            change = "regression"
        elif not baseline_passed and current_passed:
            improvements += 1
            change = "improvement"
        else:
            change = "output_changed"

        changed_cases.append(
            {
                "id": case_id,
                "change": change,
                "current_passed": current_passed,
                "baseline_passed": baseline_passed,
                "output_changed": output_changed,
            }
        )

    for case_id, baseline_case in baseline_cases.items():
        if case_id in current_case_ids:
            continue

        baseline_passed = baseline_case.get("passed")
        if baseline_passed:
            regressions += 1

        changed_cases.append(
            {
                "id": case_id,
                "change": "deleted_case",
                "current_passed": None,
                "baseline_passed": baseline_passed,
                "output_changed": True,
            }
        )

    return {
        "baseline_run": baseline_run.get("output_path"),
        "regressions": regressions,
        "improvements": improvements,
        "changed_cases": changed_cases,
    }
