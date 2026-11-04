"""A skipped PR-only gate must not silently suppress the signed main APK."""

from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / "workflows/android.yml"


class MainApkGateTest(unittest.TestCase):
    def test_main_apk_explicitly_overrides_implicit_success_of_skipped_ancestors(self):
        source = WORKFLOW.read_text()
        job = source.split("\n  main-apk:\n", 1)[1]
        self.assertIn("if: ${{ !cancelled() && github.event_name == 'push'", job)
        self.assertIn("needs.ci-summary.result == 'success'", job)


if __name__ == "__main__":
    unittest.main()
