from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class CheckResult:
    check_type: str
    expected: str
    passed: bool
    detail: str


def evaluate_check(output: str, check_type: str, expected: str) -> CheckResult:
    normalized_type = check_type.strip().lower()
    text = output or ""

    if normalized_type == "exact_match":
        passed = text == expected
        detail = "output matched exactly" if passed else "output did not match exactly"
    elif normalized_type == "contains":
        passed = expected in text
        detail = "substring found" if passed else "substring missing"
    elif normalized_type == "regex":
        try:
            passed = re.search(expected, text) is not None
            detail = "pattern matched" if passed else "pattern did not match"
        except re.error as exc:
            passed = False
            detail = f"invalid regex: {exc}"
    else:
        raise ValueError(f"Unsupported check type: {check_type}")

    return CheckResult(
        check_type=normalized_type,
        expected=expected,
        passed=passed,
        detail=detail,
    )
