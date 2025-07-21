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

# ── CLI parsing:
def cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--remote", default=config.DROPBOX_REMOTE_PATH,
                   help="Dropbox path to download (default: %(default)s)")
    p.add_argument("--local", default=config.LOCAL_FILE_PATH, type=Path,
                   help="Destination file (default: %(default)s)")
    p.add_argument("--log", default=config.TIMESTAMP_LOG_PATH, type=Path,
                   help="Timestamp file (default: %(default)s)")
    return p.parse_args()

# ── Git helpers (unchanged logic, minor tweaks):
def git(*args, **kw):
    return subprocess.run(["git", *args], **kw)

def get_current_branch() -> str:
    """
    Returns the symbolic branch name (e.g. 'main').
    If git is in the detached-HEAD-state,
    Commit-SHA is returned.
    """
    res = git("symbolic-ref", "--quiet", "--short", "HEAD",
              capture_output=True, text=True)
    if res.returncode == 0:
        return res.stdout.strip()
    # Fallback for detached HEAD:
    res = git("rev-parse", "--verify", "HEAD",
              capture_output=True, text=True, check=True)
    return res.stdout.strip()
