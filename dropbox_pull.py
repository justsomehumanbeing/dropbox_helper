#!/usr/bin/env python3

import os
import subprocess
import dropbox
from dropbox_auth import get_dropbox_client
from datetime import datetime, timezone


DROPBOX_PATH = "/WeaklyMeanSensitiveTuples/WeaklyMeanSensitiveTuples.tex"  # Remote file path
LOCAL_PATH = "./WeaklyMeanSensitiveTuples.tex"               # Local file to upload
TIMESTAMP_LOG = "scripts/.last_sync_time"

def get_current_branch() -> str:
    """
    Returns the symbolic branch name (e.g. 'main').
    Falls wir im detached-HEAD-Zustand sind, gibt’s die Commit-SHA zurück.
    Raises RuntimeError bei unerwarteten Git-Fehlern.
    """
    # Erst versuchen wir, einen symbolischen Branch-Namen zu bekommen
    res = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    if res.returncode == 0:
        return res.stdout.strip()

    # Detached HEAD: fallback auf SHA
    res = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout.strip()

def branch_has_changes_vs(branch: str, base: str = "main") -> bool:
    """
    Return True iff `branch` differs from `base` (index + working tree).
    """
    # Wir befinden uns bereits auf `branch`
    res = subprocess.run(
        ["git", "diff", "--quiet"],
        #["git", "diff", "--quiet", f"{base}...", "--"],  # drei Punkte = both changes
        check=False
    )
    return res.returncode != 0      # 0 ⇒ kein Diff, 1 ⇒ Änderungen, >1 ⇒ Fehler

def create_temp_branch():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"dropbox-pull-{timestamp}"
    current_branch = get_current_branch()
    if branch_has_changes_vs("HEAD", base=current_branch):
        print("You got unstaged changes! We stash them!")
        subprocess.run(["git", "stash", "--no-include-untracked"], check=True)
    subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    return branch_name

def pull():
    print("Initiate pull...")
    try:
        dbx = get_dropbox_client()

        metadata, res = dbx.files_download(DROPBOX_PATH)
        server_time = metadata.server_modified  # datetime object

        print("Try to switch to new branch for pulling...")
        # Create temp Git branch
        branch = create_temp_branch()

        print(f"🔽 Downloading from dropbox to {LOCAL_PATH}...")
        os.makedirs(os.path.dirname(LOCAL_PATH), exist_ok=True)
        with open(LOCAL_PATH, "wb") as f:
            f.write(res.content)

        # Write timestamp to log
        os.makedirs(os.path.dirname(TIMESTAMP_LOG), exist_ok=True)
        with open(TIMESTAMP_LOG, "w") as f:
            f.write(datetime.now(tz=timezone.utc).isoformat())

    except Exception as e:
        print(f"❌ Dropbox pull failed: {e}")
        exit(1)

    print("✅ Download complete.")

    # Check if there are changes:
    if not branch_has_changes_vs(branch, "main"):
                print("🤷 No differences to 'main'. Switching back …")
                subprocess.run(["git", "checkout", "main"], check=True)
                subprocess.run(["git", "branch", "-D", branch], check=True)
                return None                     # Früh raus, kein Commit!

    else: # not necessary, just for explicity
        print("We got new changes!")
        try:
            # Stage and commit the pulled file
            subprocess.run(["git", "add", LOCAL_PATH], check=True)
        except Exception as e:
            print(f"❌ (git) staging failed: {e}")
            exit(1)

        try:
            commit_msg = f"🚀 Dropbox pull: {DROPBOX_PATH} at {server_time.isoformat()}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        except Exception as e:
            print(f"❌ (git) commiting failed: {e}")
            exit(1)

        return None
    return None # unreachable, just for aesthetics

if __name__ == "__main__":
    pull()
