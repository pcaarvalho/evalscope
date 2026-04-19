from __future__ import annotations

import argparse
import sys
from pathlib import Path

from evalscope import __version__
from evalscope.diffing import build_run_diff
from evalscope.runner import run_spec
from evalscope.specs import load_spec
from evalscope.storage import default_output_path, load_run, write_run


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_command(args)
    if args.command == "diff":
        return _diff_command(args)

    parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evalscope", description="Local-first eval workflows for LLM apps.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run an eval spec.")
    run_parser.add_argument("spec", help="Path to a JSON or YAML eval spec.")
    run_parser.add_argument("--baseline", help="Path to a previous run artifact.")
    run_parser.add_argument("--output", help="Path for the current run artifact.")
    run_parser.add_argument("--ci", action="store_true", help="Exit non-zero when failures or regressions exist.")

    diff_parser = subparsers.add_parser("diff", help="Diff two run artifacts.")
    diff_parser.add_argument("current", help="Current run artifact JSON.")
    diff_parser.add_argument("baseline", help="Baseline run artifact JSON.")

    return parser


def _run_command(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    baseline_path = Path(args.baseline) if args.baseline else None
    file_error = _ensure_existing_file(spec_path, "spec")
    if file_error:
        print(file_error, file=sys.stderr)
        return 2
    if baseline_path:
        file_error = _ensure_existing_file(baseline_path, "baseline")
        if file_error:
            print(file_error, file=sys.stderr)
            return 2

    try:
        spec = load_spec(spec_path)
        output_path = Path(args.output) if args.output else default_output_path(spec.name)
        payload = run_spec(spec, baseline_path=baseline_path, output_path=output_path)
        payload["output_path"] = str(output_path)
        write_run(output_path, payload)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    summary = payload["summary"]
    print(f"Run written to: {output_path}")
    print(
        "Summary: "
        f"{summary['passed']}/{summary['total']} passed "
        f"({summary['failed']} failed, pass_rate={summary['pass_rate']})"
    )

    if payload["diff"]:
        _print_diff(payload["diff"])

    if args.ci:
        regressions = int(payload["diff"]["regressions"]) if payload["diff"] else 0
        if summary["failed"] or regressions:
            return 1
    return 0


def _diff_command(args: argparse.Namespace) -> int:
    current_path = Path(args.current)
    baseline_path = Path(args.baseline)

    for label, path in (("current", current_path), ("baseline", baseline_path)):
        file_error = _ensure_existing_file(path, label)
        if file_error:
            print(file_error, file=sys.stderr)
            return 2

    try:
        current = load_run(current_path)
        baseline = load_run(baseline_path)
        diff = build_run_diff(current, baseline)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    _print_diff(diff)
    return 0


def _print_diff(diff: dict[str, object]) -> None:
    changed_cases = diff.get("changed_cases", [])
    print(
        "Diff: "
        f"regressions={diff.get('regressions', 0)} "
        f"improvements={diff.get('improvements', 0)} "
        f"changed_cases={len(changed_cases) if isinstance(changed_cases, list) else 0}"
    )
    if isinstance(changed_cases, list):
        for case in changed_cases:
            print(
                f"- {case['id']}: {case['change']} "
                f"(baseline={case['baseline_passed']}, current={case['current_passed']})"
            )


def _ensure_existing_file(path: Path, label: str) -> str | None:
    if not path.exists():
        return f"Error: {label} file not found: {path}"
    if not path.is_file():
        return f"Error: {label} path is not a file: {path}"
    return None
