"""A fork-signed app must never offer upstream's differently signed APK."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "app/src/main/java/com/m57/hermescontrol/data/update/AppUpdateChecker.kt"


class UpdateOriginTest(unittest.TestCase):
    def test_default_update_origin_is_the_signing_fork(self):
        source = CHECKER.read_text()
        self.assertIn('apiBaseUrl: String = "https://api.github.com/repos/Swagatar-LLC/hermes-control-android"', source)
        self.assertNotIn('apiBaseUrl: String = "https://api.github.com/repos/Hy4ri/hermes-mobile"', source)


if __name__ == "__main__":
    unittest.main()
