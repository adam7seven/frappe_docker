import os
import re


def get_versions():
    frappe_version = os.getenv("FRAPPE_VERSION")
    assert frappe_version, "No Frappe version set"
    return frappe_version


def update_pwd(frappe_version: str):
    with open("pwd.yml", "r+") as f:
        content = f.read()
        content = re.sub(
            rf"adam7/frappe:.*", f"adam7/frappe:{frappe_version}", content
        )
        f.seek(0)
        f.truncate()
        f.write(content)


def main() -> int:
    update_pwd(*get_versions())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
