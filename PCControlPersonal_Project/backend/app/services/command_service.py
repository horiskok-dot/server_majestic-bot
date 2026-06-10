from __future__ import annotations

import subprocess


def run_safe(command: list[str], timeout: int = 15) -> tuple[int, str]:
    """Run a fixed allowlisted command shape and return combined output."""
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
        return proc.returncode, (proc.stdout + proc.stderr).strip()
    except Exception as exc:
        return 1, str(exc)

