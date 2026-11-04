"""Guard the fork's release transport contract independently of the debug build."""

from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]


class ReleaseTransportPolicyTest(unittest.TestCase):
    def test_release_build_disallows_cleartext(self):
        gradle = (ROOT / "app/build.gradle.kts").read_text()
        release = re.search(r"(?m)^\s{8}release \{(?P<body>.*?)^\s{8}\}", gradle, re.S)
        self.assertIsNotNone(release, "release build type missing")
        assert release is not None
        self.assertIn('buildConfigField("boolean", "ALLOW_CLEARTEXT", "false")', release["body"])
        self.assertIn('manifestPlaceholders["usesCleartextTraffic"] = "false"', release["body"])

    def test_main_network_policy_disallows_cleartext(self):
        policy = ET.parse(ROOT / "app/src/main/res/xml/network_security_config.xml")
        base = policy.find("base-config")
        self.assertIsNotNone(base, "base-config missing")
        assert base is not None
        self.assertEqual("false", base.get("cleartextTrafficPermitted"))

    def test_debug_network_policy_is_separate(self):
        policy = ET.parse(ROOT / "app/src/debug/res/xml/network_security_config.xml")
        base = policy.find("base-config")
        self.assertIsNotNone(base, "debug base-config missing")
        assert base is not None
        self.assertEqual("true", base.get("cleartextTrafficPermitted"))


if __name__ == "__main__":
    unittest.main()
