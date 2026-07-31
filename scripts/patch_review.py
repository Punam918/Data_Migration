"""CLI to review and apply governance patches.

Usage:
  python scripts/patch_review.py --root ./var/governance --list
  python scripts/patch_review.py --root ./var/governance --show <id>
  python scripts/patch_review.py --root ./var/governance --apply <id>
  python scripts/patch_review.py --root ./var/governance --apply-all
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from migration_platform.governance.patcher import PatchManager


def list_patches(mgr: PatchManager, limit: int = 100) -> List[Dict[str, Any]]:
    return mgr.list_patches()[:limit]


def show_patch(mgr: PatchManager, patch_id: str) -> Optional[Dict[str, Any]]:
    for p in mgr.list_patches():
        if p.get("id") == patch_id:
            return p
    return None


def apply_patch(mgr: PatchManager, patch_id: str) -> Optional[Dict[str, Any]]:
    rec = mgr.apply_patch(patch_id)
    if rec is None:
        return None
    return rec.__dict__ if hasattr(rec, "__dict__") else rec


def confirm(prompt: str) -> bool:
    ans = input(prompt + " [y/N]: ")
    return ans.lower() in ("y", "yes")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Review and apply governance patches")
    parser.add_argument("--root", default="./var/governance", help="governance root dir")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="list patches")
    group.add_argument("--show", nargs=1, metavar="PATCH_ID", help="show a patch")
    group.add_argument("--apply", nargs=1, metavar="PATCH_ID", help="apply a patch")
    group.add_argument("--apply-all", action="store_true", help="apply all patches")
    parser.add_argument("--yes", action="store_true", help="auto-confirm actions")
    args = parser.parse_args(argv)

    mgr = PatchManager(Path(args.root))

    if args.list:
        patches = list_patches(mgr)
        print(json.dumps(patches, indent=2))
        return 0

    if args.show:
        pid = args.show[0]
        p = show_patch(mgr, pid)
        if p is None:
            print("patch not found", file=sys.stderr)
            return 2
        print(json.dumps(p, indent=2))
        return 0

    if args.apply:
        pid = args.apply[0]
        if not args.yes and not confirm(f"Apply patch {pid}?"):
            print("aborted")
            return 3
        rec = apply_patch(mgr, pid)
        if rec is None:
            print("patch not found", file=sys.stderr)
            return 2
        print(json.dumps(rec, indent=2))
        return 0

    if args.apply_all:
        patches = mgr.list_patches()
        if not patches:
            print("no patches")
            return 0
        if not args.yes and not confirm(f"Apply all {len(patches)} patches?"):
            print("aborted")
            return 3
        applied = []
        for p in patches:
            rec = mgr.apply_patch(p.get("id"))
            if rec is not None:
                applied.append(rec.__dict__ if hasattr(rec, "__dict__") else rec)
        print(json.dumps(applied, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
