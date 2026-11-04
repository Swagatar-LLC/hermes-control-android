"""Versions for signed main-branch APKs."""

import argparse
import re


def preview_version(base_version: str, run_number: str) -> tuple[str, int]:
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", base_version):
        raise ValueError("VERSION must be a stable MAJOR.MINOR.PATCH SemVer")
    if not re.fullmatch(r"[1-9][0-9]*", run_number):
        raise ValueError("GitHub run number must be a positive integer without leading zeros")
    code = int(run_number) * 100
    if code > 2_100_000_000:
        raise ValueError("Android versionCode exceeds its supported range")
    return f"{base_version}-dev.{run_number}", code


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_version")
    parser.add_argument("run_number")
    args = parser.parse_args()
    name, code = preview_version(args.base_version, args.run_number)
    print(f"name={name}\ncode={code}")


if __name__ == "__main__":
    main()
