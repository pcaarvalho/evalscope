import unittest

from evalscope.checks import evaluate_check


class CheckTests(unittest.TestCase):
    def test_exact_match_passes(self) -> None:
        result = evaluate_check("billing", "exact_match", "billing")
        self.assertTrue(result.passed)

    def test_contains_fails_when_missing(self) -> None:
        result = evaluate_check("bug", "contains", "billing")
        self.assertFalse(result.passed)

    def test_regex_passes(self) -> None:
        result = evaluate_check('{"status":"ok"}', "regex", '"status"\\s*:\\s*"ok"')
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
