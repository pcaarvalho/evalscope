import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evalscope.diffing import build_run_diff
from evalscope.runner import run_spec
from evalscope.specs import load_spec, parse_spec
from evalscope.storage import load_run, write_run


class RunnerTests(unittest.TestCase):
    def test_run_spec_with_simulated_outputs(self) -> None:
        spec = load_spec(Path("examples/quickstart.json"))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "run.json"
            payload = run_spec(spec, output_path=output_path)
            write_run(output_path, payload)

            saved = load_run(output_path)
            self.assertEqual(saved["summary"]["failed"], 0)
            self.assertEqual(len(saved["cases"]), 2)

    def test_run_diff_detects_regression(self) -> None:
        spec = load_spec(Path("examples/quickstart.json"))

        with tempfile.TemporaryDirectory() as temp_dir:
            baseline_path = Path(temp_dir) / "baseline.json"
            current_path = Path(temp_dir) / "current.json"

            baseline = run_spec(spec, output_path=baseline_path)
            write_run(baseline_path, baseline)

            current = run_spec(spec, output_path=current_path)
            current["cases"][0]["output"] = "Goodbye, Pedro."
            current["cases"][0]["passed"] = False
            current["summary"]["passed"] = 1
            current["summary"]["failed"] = 1
            current["diff"] = build_run_diff(current, baseline)

            self.assertEqual(current["diff"]["regressions"], 1)

    def test_run_diff_detects_deleted_case(self) -> None:
        baseline = {
            "output_path": "baseline.json",
            "cases": [{"id": "billing", "passed": True, "output": "billing"}],
        }
        current = {"output_path": "current.json", "cases": []}

        diff = build_run_diff(current, baseline)

        self.assertEqual(diff["regressions"], 1)
        self.assertEqual(diff["changed_cases"][0]["change"], "deleted_case")

    def test_run_spec_records_case_error_and_continues(self) -> None:
        spec = parse_spec(
            {
                "name": "error-isolation",
                "provider": "openai",
                "model": "gpt-4.1-mini",
                "prompt_template": "{input}",
                "cases": [
                    {
                        "id": "local-pass",
                        "input": "billing",
                        "simulate_output": "billing",
                        "checks": [{"type": "exact_match", "value": "billing"}],
                    },
                    {
                        "id": "api-failure",
                        "input": "shipping",
                        "checks": [{"type": "exact_match", "value": "shipping"}],
                    },
                ],
            }
        )

        with patch("evalscope.runner.run_openai_prompt", side_effect=RuntimeError("upstream timeout")):
            payload = run_spec(spec)

        self.assertEqual(payload["summary"]["total"], 2)
        self.assertEqual(payload["summary"]["passed"], 1)
        self.assertEqual(payload["summary"]["failed"], 1)
        self.assertEqual(payload["cases"][1]["error"], "upstream timeout")
        self.assertFalse(payload["cases"][1]["passed"])

    def test_run_spec_isolates_prompt_render_error(self) -> None:
        spec = parse_spec(
            {
                "name": "prompt-error-isolation",
                "provider": "openai",
                "model": "gpt-4.1-mini",
                "prompt_template": "{input}",
                "cases": [
                    {
                        "id": "local-pass",
                        "input": "billing",
                        "simulate_output": "billing",
                        "checks": [{"type": "exact_match", "value": "billing"}],
                    },
                    {
                        "id": "bad-prompt",
                        "input": "shipping",
                        "prompt": "{missing}",
                        "simulate_output": "shipping",
                        "checks": [{"type": "exact_match", "value": "shipping"}],
                    },
                ],
            }
        )

        payload = run_spec(spec)

        self.assertEqual(payload["summary"]["total"], 2)
        self.assertEqual(payload["summary"]["passed"], 1)
        self.assertEqual(payload["summary"]["failed"], 1)
        self.assertEqual(payload["cases"][1]["prompt"], "")
        self.assertIn("missing", payload["cases"][1]["error"])
        self.assertFalse(payload["cases"][1]["passed"])

    def test_parse_spec_rejects_duplicate_case_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "Duplicate case id: dup"):
            parse_spec(
                {
                    "name": "dup-ids",
                    "provider": "openai",
                    "model": "gpt-4.1-mini",
                    "cases": [
                        {
                            "id": "dup",
                            "input": "a",
                            "simulate_output": "a",
                            "checks": [{"type": "exact_match", "value": "a"}],
                        },
                        {
                            "id": "dup",
                            "input": "b",
                            "simulate_output": "b",
                            "checks": [{"type": "exact_match", "value": "b"}],
                        },
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
