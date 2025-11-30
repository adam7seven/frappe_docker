import os
import re


def get_FRAPPE_VERSION():
    FRAPPE_VERSION = os.getenv("FRAPPE_VERSION")
    assert FRAPPE_VERSION, "No Frappe version set"
    return FRAPPE_VERSION


def update_env(FRAPPE_VERSION: str):
    with open("example.env", "r+") as f:
        content = f.read()
        content = re.sub(
            rf"FRAPPE_VERSION=.*", f"FRAPPE_VERSION={FRAPPE_VERSION}", content
        )
        f.seek(0)
        f.truncate()
        f.write(content)


def main() -> int:
    update_env(get_FRAPPE_VERSION())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
