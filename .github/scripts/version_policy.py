"""Reject a main preview whose SemVer base was already published."""

import json
import os
from pathlib import Path
import re
import subprocess

VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def check_version(base: str, tag: str | None) -> None:
    if not VERSION.fullmatch(base):
        raise ValueError("VERSION must be stable MAJOR.MINOR.PATCH SemVer")
    if tag is None:
        return
    if not tag.startswith("v") or not VERSION.fullmatch(tag[1:]):
        raise ValueError("Latest GitHub release tag is not stable SemVer")
    latest = tuple(map(int, tag[1:].split(".")))
    current = tuple(map(int, base.split(".")))
    if current <= latest:
        raise ValueError("Bump VERSION beyond the published stable release before merging")


def latest_release(runner=None) -> str | None:
    if os.environ.get("GITHUB_REPOSITORY", "Swagatar-LLC/hermes-control-android") != "Swagatar-LLC/hermes-control-android":
        raise ValueError("Refusing to inspect a different repository")
    command = ["gh", "api", "-X", "GET", "repos/Swagatar-LLC/hermes-control-android/releases/latest"]
    result = (runner or (lambda args: subprocess.run(args, capture_output=True, text=True, check=False)))(command)
    if result.returncode:
        if "gh: Not Found (HTTP 404)" in result.stderr:
            return None
        raise RuntimeError("GitHub release lookup failed")
    data = json.loads(result.stdout)
    tag = data.get("tag_name") if isinstance(data, dict) else None
    if not isinstance(tag, str):
        raise ValueError("GitHub release response has no tag_name")
    return tag


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    base = (root / "VERSION").read_text().strip()
    tag = latest_release()
    check_version(base, tag)
    print(f"VERSION {base} is newer than the latest stable release {tag or '(none)'}")


if __name__ == "__main__":
    main()
