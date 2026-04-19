from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class EvalCheck:
    type: str
    value: str


@dataclass(slots=True)
class EvalCase:
    id: str
    input: str
    checks: list[EvalCheck]
    simulate_output: str | None = None
    prompt: str | None = None


@dataclass(slots=True)
class EvalSpec:
    name: str
    provider: str
    model: str
    prompt_template: str
    system: str | None
    cases: list[EvalCase]


def load_spec(path: Path) -> EvalSpec:
    payload = _load_mapping(path)
    return parse_spec(payload)


def parse_spec(payload: dict[str, Any]) -> EvalSpec:
    name = str(payload.get("name") or "evalscope-run")
    provider = str(payload.get("provider") or "openai").strip().lower()
    if provider != "openai":
        raise ValueError("evalscope v0 only supports provider=openai")

    model = str(payload.get("model") or "").strip()
    if not model:
        raise ValueError("Spec must define a model")

    prompt_template = str(payload.get("prompt_template") or "{input}")
    system = payload.get("system")
    system_text = str(system) if system is not None else None

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("Spec must define at least one case")

    cases: list[EvalCase] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ValueError("Each case must be an object")

        case_id = str(raw_case.get("id") or "").strip()
        case_input = str(raw_case.get("input") or "")
        if not case_id:
            raise ValueError("Each case must define an id")

        raw_checks = raw_case.get("checks")
        if not isinstance(raw_checks, list) or not raw_checks:
            raise ValueError(f"Case {case_id} must define at least one check")

        checks: list[EvalCheck] = []
        for raw_check in raw_checks:
            if not isinstance(raw_check, dict):
                raise ValueError(f"Case {case_id} contains an invalid check")
            check_type = str(raw_check.get("type") or "").strip()
            check_value = raw_check.get("value")
            if not check_type or check_value is None:
                raise ValueError(f"Case {case_id} has an incomplete check")
            checks.append(EvalCheck(type=check_type, value=str(check_value)))

        simulate_output = raw_case.get("simulate_output")
        prompt = raw_case.get("prompt")
        cases.append(
            EvalCase(
                id=case_id,
                input=case_input,
                checks=checks,
                simulate_output=str(simulate_output) if simulate_output is not None else None,
                prompt=str(prompt) if prompt is not None else None,
            )
        )

    return EvalSpec(
        name=name,
        provider=provider,
        model=model,
        prompt_template=prompt_template,
        system=system_text,
        cases=cases,
    )


def build_prompt(spec: EvalSpec, case: EvalCase) -> str:
    template = case.prompt or spec.prompt_template
    return template.format(input=case.input)


def _load_mapping(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    raw = path.read_text(encoding="utf-8")

    if suffix == ".json":
        payload = json.loads(raw)
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError(
                "PyYAML is required for YAML specs. Install dependencies with `pip install -e .`."
            ) from exc
        payload = yaml.safe_load(raw)
    else:
        raise ValueError(f"Unsupported spec extension: {suffix}")

    if not isinstance(payload, dict):
        raise ValueError("Top-level spec must be an object")

    return payload
