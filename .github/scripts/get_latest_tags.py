from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Literal

Repo = Literal["frappe"]
MajorVersion = Literal["15", "16", "develop"]


def get_latest_tag(repo: Repo, version: MajorVersion) -> str:
    if version == "develop":
        return "develop"
    regex = rf"v{version}.*"
    refs = subprocess.check_output(
        (
            "git",
            "-c",
            "versionsort.suffix=-",
            "ls-remote",
            "--refs",
            "--tags",
            "--sort=v:refname",
            f"https://github.com/adam7seven/{repo}",
            str(regex),
        ),
        encoding="UTF-8",
    ).split()[1::2]

    if not refs:
        raise RuntimeError(f'No tags found for version "{regex}"')
    ref = refs[-1]
    matches: list[str] = re.findall(regex, ref)
    if not matches:
        raise RuntimeError(f'Can\'t parse tag from ref "{ref}"')
    return matches[0]


def update_env(file_name: str, frappe_tag: str):
    text = f"\nFRAPPE_VERSION={frappe_tag}"

    with open(file_name, "a") as f:
        f.write(text)


def _print_resp(frappe_tag: str):
    print(json.dumps({"frappe": frappe_tag}))


def main(_args: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", choices=["frappe"], required=True)
    parser.add_argument(
        "--version", choices=["12", "13", "14", "15", "16", "develop"], required=True
    )
    args = parser.parse_args(_args)

    frappe_tag = get_latest_tag("frappe", args.version)

    file_name = os.getenv("GITHUB_ENV")
    if file_name:
        update_env(file_name, frappe_tag)
    _print_resp(frappe_tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
