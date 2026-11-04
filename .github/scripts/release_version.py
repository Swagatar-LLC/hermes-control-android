"""Resolve a stable release tag against a verified main CI run."""

import argparse
import json
from pathlib import Path
import re
import subprocess

from preview_version import preview_version


def release_version(tag: str, base: str, run_number: int) -> tuple[str, int]:
    if not re.fullmatch(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", tag):
        raise ValueError("Stable release tag must be vMAJOR.MINOR.PATCH")
    if tag != f"v{base}" or type(run_number) is not int:
        raise ValueError("Release tag and reviewed VERSION must match a main run")
    _, preview_code = preview_version(base, str(run_number))
    code = preview_code + 99
    if code > 2_100_000_000:
        raise ValueError("Android versionCode exceeds its supported range")
    return base, code


def select_main_run(data: dict, sha: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Source SHA must be a complete commit ID")
    runs = data.get("workflow_runs") if isinstance(data, dict) else None
    if not isinstance(runs, list):
        raise ValueError("Missing main CI runs")
    matches = [
        row for row in runs if isinstance(row, dict)
        and row.get("head_sha") == sha and row.get("event") == "push"
        and row.get("head_branch") == "main" and row.get("status") == "completed"
        and row.get("conclusion") == "success"
    ]
    if len(matches) != 1 or any(
        type(matches[0].get(key)) is not int or matches[0][key] < 1
        for key in ("run_number", "id", "run_attempt")
    ):
        raise ValueError("Expected exactly one successful main CI run for source SHA")
    return matches[0]["run_number"], matches[0]["id"], matches[0]["run_attempt"]


def require_signed_artifact(data: dict, sha: str, run_id: int, attempt: int) -> None:
    artifacts = data.get("artifacts") if isinstance(data, dict) else None
    if not isinstance(artifacts, list):
        raise ValueError("Missing main CI artifacts")
    expected = f"hermes-control-android-main-{sha}-{run_id}-{attempt}"
    matches = [
        item for item in artifacts if isinstance(item, dict)
        and item.get("name") == expected and item.get("expired") is False
        and type(item.get("size_in_bytes")) is int and item["size_in_bytes"] > 0
    ]
    if len(matches) != 1:
        raise ValueError("Successful main run lacks its exact signed APK artifact")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("base")
    parser.add_argument("sha")
    parser.add_argument("runs_json", type=Path)
    args = parser.parse_args()
    run, run_id, attempt = select_main_run(json.loads(args.runs_json.read_text()), args.sha)
    result = subprocess.run(
        ["gh", "api", "-X", "GET", f"repos/Swagatar-LLC/hermes-control-android/actions/runs/{run_id}/artifacts"],
        capture_output=True, text=True, check=True,
    )
    require_signed_artifact(json.loads(result.stdout), args.sha, run_id, attempt)
    version, code = release_version(args.tag, args.base, run)
    print(f"tag={args.tag}\nversion={version}\ncode={code}\nprerelease=false")


if __name__ == "__main__":
    main()
