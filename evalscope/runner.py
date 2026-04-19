from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .checks import CheckResult, evaluate_check
from .diffing import build_run_diff
from .openai_adapter import run_openai_prompt
from .specs import EvalCase, EvalSpec, build_prompt
from .storage import load_run, utc_now_iso


def run_spec(spec: EvalSpec, baseline_path: Path | None = None, output_path: Path | None = None) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    for case in spec.cases:
        prompt = ""
        case_error: str | None = None

        try:
            prompt = build_prompt(spec, case)
            output = _run_case(spec, case, prompt)
            check_results = _evaluate_case(output, case)
            case_passed = all(result.passed for result in check_results)
        except Exception as exc:
            output = ""
            check_results = []
            case_passed = False
            case_error = str(exc)

        case_payload = {
            "id": case.id,
            "input": case.input,
            "prompt": prompt,
            "output": output,
            "passed": case_passed,
            "checks": [asdict(result) for result in check_results],
        }
        if case_error:
            case_payload["error"] = case_error

        cases.append(case_payload)

    passed = sum(1 for case in cases if case["passed"])
    total = len(cases)
    run_payload: dict[str, Any] = {
        "created_at": utc_now_iso(),
        "spec": {
            "name": spec.name,
            "provider": spec.provider,
            "model": spec.model,
        },
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
        "cases": cases,
        "output_path": str(output_path) if output_path else None,
        "baseline_path": str(baseline_path) if baseline_path else None,
        "diff": None,
    }

    if baseline_path:
        baseline_run = load_run(baseline_path)
        run_payload["diff"] = build_run_diff(run_payload, baseline_run)

    return run_payload


def _run_case(spec: EvalSpec, case: EvalCase, prompt: str) -> str:
    if case.simulate_output is not None:
        return case.simulate_output
    return run_openai_prompt(model=spec.model, prompt=prompt, system=spec.system)


def _evaluate_case(output: str, case: EvalCase) -> list[CheckResult]:
    return [evaluate_check(output, check.type, check.value) for check in case.checks]
