"""A stable tag must follow a verified signed main build of the same source."""

import unittest

from release_version import release_version, select_main_run, require_signed_artifact

SHA = "a" * 40


def run(number=6, sha=SHA, conclusion="success", event="push", branch="main", status="completed"):
    return {"id": 42, "run_attempt": 1, "run_number": number, "head_sha": sha, "conclusion": conclusion, "event": event, "head_branch": branch, "status": status}


class ReleaseVersionTest(unittest.TestCase):
    def test_stable_tag_allocates_code_between_preview_and_next_main(self):
        version, code = release_version("v2.9.2", "2.9.2", 6)
        self.assertEqual(("2.9.2", 699), (version, code))
        self.assertLess(600, code)
        self.assertLess(code, 700)

    def test_rejects_mismatch_prerelease_and_bad_version(self):
        for tag, base in (("v2.9.3", "2.9.2"), ("v2.9.2-rc.1", "2.9.2"), ("v2.9.2", "2.09.2")):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release_version(tag, base, 6)

    def test_rejects_android_code_overflow(self):
        with self.assertRaises(ValueError):
            release_version("v2.9.2", "2.9.2", 21_000_000)

    def test_selects_only_one_completed_green_main_push_of_exact_sha(self):
        self.assertEqual((6, 42, 1), select_main_run({"workflow_runs": [run()]}, SHA))
        for runs in ([], [run(conclusion="failure")], [run(sha="b" * 40)],
                     [run(event="pull_request")], [run(branch="other")],
                     [run(status="in_progress")], [run(), run(number=7)]):
            with self.subTest(runs=runs), self.assertRaises(ValueError):
                select_main_run({"workflow_runs": runs}, SHA)

    def test_requires_exact_nonempty_signed_artifact_not_only_green_ci(self):
        name = f"hermes-control-android-main-{SHA}-42-1"
        valid = {"name": name, "expired": False, "size_in_bytes": 100}
        require_signed_artifact({"artifacts": [valid]}, SHA, 42, 1)
        for artifacts in ([], [{**valid, "expired": True}], [{**valid, "size_in_bytes": 0}],
                          [{**valid, "name": "hermescontrol-debug-apk"}]):
            with self.subTest(artifacts=artifacts), self.assertRaises(ValueError):
                require_signed_artifact({"artifacts": artifacts}, SHA, 42, 1)


if __name__ == "__main__":
    unittest.main()
