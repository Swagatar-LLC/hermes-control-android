"""The PR gate asks reviewers for a falsifiable claim and a security boundary."""

import unittest

import check_pr_template as template


BODY = """## Summary
Add a release transport policy.
## Description
Reject cleartext credentials in release builds.
## Type of Change
- [x] 🔧 CI / chore
## How to test
Ran release-policy regression tests before and after the change.
## Checklist
- [x] Review completed
"""


class AssuranceTemplateTest(unittest.TestCase):
    def test_missing_rigor_and_security_evidence_is_rejected(self):
        problems = template.validate(BODY, title="ci: enforce transport policy", base="main")
        rendered = str(problems)
        self.assertIn("Rigor spine", rendered)
        self.assertIn("Security review", rendered)

    def test_placeholder_sections_do_not_satisfy_gate(self):
        body = BODY + "\n## Rigor spine\n<!-- Fill in later -->\n## Security review\n<!-- Fill in later -->\n"
        problems = template.validate(body, title="ci: enforce transport policy", base="main")
        rendered = str(problems)
        self.assertIn("Rigor spine", rendered)
        self.assertIn("Security review", rendered)

    def test_reviewable_evidence_satisfies_gate(self):
        body = BODY + """
## Rigor spine
Premise: release accepts HTTP. Check: rejected before network with a failing policy test. Countercase: debug still permits HTTP.
## Security review
Boundary: gateway credential over Wi-Fi. Reviewed transport, notification and backup paths; no real device behavior has been verified.
"""
        self.assertEqual([], template.validate(body, title="ci: enforce transport policy", base="main"))


if __name__ == "__main__":
    unittest.main()
