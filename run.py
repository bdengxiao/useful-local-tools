"""Convenient dispatcher; each skill script also runs independently."""
import argparse
import importlib.util
from pathlib import Path
import sys

TOOLS = {"csv": "csv-text-safe", "handoff": "handoff-check", "env": "env-preflight"}


def main():
    parser = argparse.ArgumentParser(description="Three local tools. Select a tool, then use --help.")
    parser.add_argument("tool", choices=TOOLS)
    args, remaining = parser.parse_known_args(sys.argv[1:2])
    name = TOOLS[args.tool]
    script = Path(__file__).parent / "skills" / name / "scripts" / (name.replace("-", "_") + ".py")
    spec = importlib.util.spec_from_file_location("selected_tool", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main(sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())
