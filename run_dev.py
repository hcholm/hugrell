from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
APP_ROOT = PROJECT_ROOT / "app"
LOCAL_MAKRELL_ROOT = PROJECT_ROOT.parent.parent / "src" / "impl" / "py"

for entry in [str(APP_ROOT), str(LOCAL_MAKRELL_ROOT)]:
    if entry not in sys.path:
        sys.path.insert(0, entry)

import makrell  # noqa: F401
from dev_server import main


if __name__ == "__main__":
    raise SystemExit(main(None))
