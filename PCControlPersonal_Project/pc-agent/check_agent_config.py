import json
import sys
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent


def main() -> int:
    with open(BASE_DIR / "agent_config.json", "r", encoding="utf-8") as handle:
        cfg = json.load(handle)

    base = str(cfg.get("server_base_url", "")).rstrip("/")
    key = str(cfg.get("access_key", ""))

    print("Server:", base)
    print("Agent:", cfg.get("agent_id", "-"))
    print("Access key configured:", bool(key and key != "CHANGE_ME"))
    print("Access key length:", len(key))

    if not base:
        print("ERROR: server_base_url is empty")
        return 2
    if not key or key == "CHANGE_ME":
        print("ERROR: access_key is not configured")
        return 2

    try:
        ping = requests.get(base + "/api/ping", timeout=8)
        print("Ping:", ping.status_code, ping.text[:120])
    except Exception as exc:
        print("ERROR: cannot reach server:", exc)
        return 3

    try:
        protected = requests.get(base + "/api/agents", headers={"X-Server-Access-Key": key}, timeout=8)
        print("Protected API:", protected.status_code)
        if protected.status_code == 200:
            print("OK: access_key is accepted")
            return 0
        print("ERROR:", protected.text[:300])
        return 4
    except Exception as exc:
        print("ERROR: protected API check failed:", exc)
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
