"""Code churn per module for regression scoring (CODIFAi Phase 5, criterion 4).

The 7rmart app is a black box to this repo, so churn must come from the APP's repository, not this one.
Usage: python scripts/churn.py --repo PATH_TO_APP_REPO [--days 90]
Module -> folder mapping comes from config/workflow.json "modules.<name>.app_paths".
Prints {"module": {"commits": N, "points": 0|8|17|25}}; modules without app_paths print "unknown".
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def points(commits: int) -> int:
    return 0 if commits == 0 else 8 if commits <= 3 else 17 if commits <= 10 else 25


def main() -> int:
    if "--repo" not in sys.argv:
        sys.exit(__doc__)
    repo = sys.argv[sys.argv.index("--repo") + 1]
    days = sys.argv[sys.argv.index("--days") + 1] if "--days" in sys.argv else "90"
    modules = json.loads((ROOT / "config" / "workflow.json").read_text(encoding="utf-8"))["modules"]
    result = {}
    for name, cfg in modules.items():
        paths = cfg.get("app_paths") or []
        if not paths:
            result[name] = "unknown"
            continue
        out = subprocess.run(["git", "-C", repo, "log", f"--since={days} days ago", "--format=%H", "--", *paths],
                             capture_output=True, text=True, check=True).stdout.split()
        result[name] = {"commits": len(out), "points": points(len(out))}
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
