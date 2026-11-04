"""Main-branch APK versions must be SemVer and Android-upgradeable."""

from pathlib import Path
import unittest

from preview_version import preview_version


class PreviewVersionTest(unittest.TestCase):
    def test_tracked_version_file_is_a_valid_base(self):
        base = (Path(__file__).resolve().parents[2] / "VERSION").read_text().strip()
        self.assertTrue(preview_version(base, "1")[0].startswith(base + "-dev."))

    def test_main_run_gets_numeric_semver_prerelease(self):
        self.assertEqual(("1.0.0-dev.27", 2700), preview_version("1.0.0", "27"))

    def test_rerun_is_identical_and_next_run_is_upgradeable(self):
        self.assertEqual(preview_version("1.0.0", "27"), preview_version("1.0.0", "27"))
        self.assertGreater(preview_version("1.0.0", "28")[1], preview_version("1.0.0", "27")[1])

    def test_new_base_version_does_not_reset_android_code(self):
        self.assertEqual(("1.1.0-dev.28", 2800), preview_version("1.1.0", "28"))

    def test_invalid_base_versions_fail_closed(self):
        for value in ("1.0", "v1.0.0", "1.00.0", "1.0.0-dev", "1.0.0+local", "1.0.0\nother"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                preview_version(value, "27")

    def test_invalid_run_numbers_fail_closed(self):
        for value in ("0", "01", "-1", "abc", "21000001"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                preview_version("1.0.0", value)


if __name__ == "__main__":
    unittest.main()
