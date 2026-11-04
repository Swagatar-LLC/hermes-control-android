"""A published stable version must never be followed by a same-base preview."""

import subprocess
import unittest

from version_policy import check_version, latest_release


class VersionPolicyTest(unittest.TestCase):
    def test_no_release_or_older_stable_allows_preview(self):
        check_version("2.9.2", None)
        check_version("2.9.3", "v2.9.2")
        check_version("2.10.0", "v2.9.9")

    def test_same_or_newer_stable_blocks_preview(self):
        for base, tag in (("2.9.2", "v2.9.2"), ("2.9.2", "v2.10.0")):
            with self.subTest(base=base, tag=tag), self.assertRaises(ValueError):
                check_version(base, tag)

    def test_malformed_versions_fail_closed(self):
        for base, tag in (("2.09.2", None), ("2.9.2", "v2.9.2-rc.1")):
            with self.subTest(base=base, tag=tag), self.assertRaises(ValueError):
                check_version(base, tag)

    def test_only_404_means_no_release(self):
        self.assertIsNone(latest_release(lambda command: subprocess.CompletedProcess(command, 1, "", "gh: Not Found (HTTP 404)")))
        with self.assertRaises(RuntimeError):
            latest_release(lambda command: subprocess.CompletedProcess(command, 1, "", "gh: Server Error (HTTP 500)"))

    def test_reads_stable_tag_from_successful_github_response(self):
        result = latest_release(lambda command: subprocess.CompletedProcess(command, 0, '{"tag_name":"v2.9.1"}', ""))
        self.assertEqual("v2.9.1", result)


if __name__ == "__main__":
    unittest.main()
