#!/usr/bin/env python3
"""
Upload LOCAL_FILE_PATH to Dropbox, making sure we never overwrite newer remote content.
Interactive prompt if remote is newer than our last pull.
"""
import argparse, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
import dropbox
from dropbox_auth import get_dropbox_client
from dropbox_pull import pull  # reuse temp‑branch logic
import config
from base_functions import *

def read_last_pull_time(ts_file: Path):
    """Return the timestamp stored in *ts_file* or ``None`` if the file is absent."""
    try:
        txt = ts_file.read_text().strip()
        dt = datetime.fromisoformat(txt)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except FileNotFoundError:
        return None

def push():
    """Upload the configured local file to Dropbox after sanity checks."""
    opt = cli()
    # Ensure the file exists:
    if not opt.local.is_file():
        raise SystemExit(f"❌ Local file missing: {opt.local}")

    try:
        dbx = get_dropbox_client()
        remote_meta = dbx.files_get_metadata(opt.remote)
        remote_ts = remote_meta.server_modified
        # Dropbox uses naive timestamps, assume UTC
        if remote_ts.tzinfo is None:
            remote_ts = remote_ts.replace(tzinfo=timezone.utc)
        local_ts  = read_last_pull_time(opt.log)

        if not local_ts or remote_ts > local_ts:
            print("⚠  Remote file is newer than last pull.")
            if input("Pull first on temporary branch? [y/N] ").strip().lower() == "y":
                pull()
            raise SystemExit("Push aborted to protect remote data.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

    try:
        print(f"🔼  Uploading {opt.local} → {opt.remote}")
        with opt.local.open("rb") as fh:
            dbx.files_upload(
                    fh.read(),
                    opt.remote,
                    mode=dropbox.files.WriteMode.overwrite
            )

        opt.log.parent.mkdir(parents=True, exist_ok=True)
        opt.log.write_text(datetime.now(tz=timezone.utc).isoformat())
        print("✅  Upload complete.")

    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    push()
