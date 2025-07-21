#!/usr/bin/env python3
"""
Pull a single file from Dropbox *into* the repo and commit it on a temporary
Git branch, keeping your main branch immaculate.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse, subprocess, os
from dropbox_auth import get_dropbox_client
import config
from base_functions import *

def branch_has_changes_vs(base: str = "main") -> bool:
    """
    True  ⇒ Commit‑History *or* work tree of current branch differs from base
    False ⇒ work tree clean *and* no commit differences
    ──────────────────────────────────────────────────────────────────
    Implementation details:
      `git diff --quiet <rev>` returns
        0 ⇒ no differences
        1 ⇒ there are differences
      other Exit‑Codes ⇒ Error (e.g. Branch does not exist)
    """
    try:
        res = git("diff", "--quiet", base)
        if res.returncode in (0, 1):
            # 1 → es gibt Unterschiede (working tree, index ODER Commits)
            return res.returncode == 1

        # Alles andere ist ein git‑Fehler (128 u. Ä.)
        raise RuntimeError(f"'git diff' exit code {res.returncode}")

    except Exception as exc:
        print(f"Error: git diff failed – {exc}", file=sys.stderr)
        sys.exit(1)

def create_temp_branch() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = f"dropbox-pull-{ts}"
    if branch_has_changes_vs():
        print("⚠  Unstaged changes detected → stashing.")
        git("stash", "--no-include-untracked", check=True)
    git("checkout", "-b", name, check=True)
    return name

# ── main pull routine
def pull():
    print("Initiate pull...")
    try:
        opt = cli()
        dbx = get_dropbox_client()
        meta, res = dbx.files_download(opt.remote)

        branch = create_temp_branch()
        print(f"🔽  Downloading → {opt.local}")
        opt.local.parent.mkdir(parents=True, exist_ok=True)
        opt.local.write_bytes(res.content)

        opt.log.parent.mkdir(parents=True, exist_ok=True)
        opt.log.write_text(datetime.now(tz=timezone.utc).isoformat())

        if not branch_has_changes_vs("main"):
            print("🤷  Nothing changed.  Cleaning up.")
            git("checkout", "main", check=True)
            git("branch", "-D", branch, check=True)
            return

        git("add", str(opt.local), check=True)
        git("commit", "-m",
            f"🚀 Dropbox pull: {opt.remote} @ {meta.server_modified.isoformat()}",
            check=True)
        print("✅  Pull committed on", branch)

    except Exception as e:
        print(f"❌ Dropbox pull failed: {e}")
        exit(1)


if __name__ == "__main__":
    pull()
