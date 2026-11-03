"""Verify a production container without credentials or upstream services."""

import argparse
import json
import subprocess
import time


def docker(*args, capture=False):
    """Run Docker and surface failures to CI."""
    return subprocess.run(
        ["docker", *args], check=True, text=True, capture_output=capture, timeout=180
    )


def main():
    """Check the real default command, non-root user, and readiness."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()
    container = docker(
        "run", "--detach", "--network", "none", "--env", "RUN_ON_START=0", args.image, capture=True
    ).stdout.strip()
    try:
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            info = json.loads(docker("inspect", container, capture=True).stdout)[0]
            assert info["Config"]["User"] not in ("", "root", "0"), "Container must run non-root"
            assert info["State"]["Running"], "Default command exited"
            if "Health" in info["State"]:
                if info["State"]["Health"]["Status"] == "healthy":
                    docker(
                        "exec",
                        container,
                        "python",
                        "-c",
                        "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True, args=['--no-sandbox']); b.close(); p.stop()",
                    )
                    return
            elif "Sleeping" in docker("logs", container, capture=True).stderr:
                docker("exec", container, "python", "-m", "src", "--help")
                return
            time.sleep(1)
        raise RuntimeError("Container did not become ready")
    finally:
        try:
            docker("logs", container)
        finally:
            docker("rm", "--force", container)


if __name__ == "__main__":
    main()
