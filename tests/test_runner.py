import tempfile
import unittest
from pathlib import Path

from evalscope.diffing import build_run_diff
from evalscope.runner import run_spec
from evalscope.specs import load_spec
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


if __name__ == "__main__":
    unittest.main()
