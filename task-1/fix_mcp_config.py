
"""
Run this once from inside your project directory:
    python3 fix_mcp_config.py

It rewrites mcp_config.json in place, replacing:
- the filesystem server's workspace path with the real one on this machine
- the docker server's placeholder path with the real path to docker_mcp_server.py
It does NOT touch the fetch server — see the separate cache-clean fix for that.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "mcp_config.json")
WORKSPACE_PATH = os.path.join(HERE, "workspace")
DOCKER_SERVER_PATH = os.path.join(HERE, "docker_mcp_server.py")

if not os.path.exists(CONFIG_PATH):
    sys.exit(f"mcp_config.json not found at {CONFIG_PATH} — run this from your project dir.")

os.makedirs(WORKSPACE_PATH, exist_ok=True)

if not os.path.exists(DOCKER_SERVER_PATH):
    sys.exit(f"docker_mcp_server.py not found at {DOCKER_SERVER_PATH} — make sure it's saved there.")

with open(CONFIG_PATH) as f:
    config = json.load(f)

if "filesystem" in config:
    config["filesystem"]["args"] = ["-y", "@modelcontextprotocol/server-filesystem", WORKSPACE_PATH]
    print(f"filesystem -> {WORKSPACE_PATH}")

if "docker" in config:
    config["docker"]["command"] = "python3"
    config["docker"]["args"] = [DOCKER_SERVER_PATH]
    print(f"docker -> python3 {DOCKER_SERVER_PATH}")

with open(CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)

print(f"\nWrote fixed paths to {CONFIG_PATH}")
