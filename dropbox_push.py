#!/usr/bin/env python3

import os
import subprocess
import dropbox
from dropbox_auth import get_dropbox_client
from datetime import datetime, timezone
from dropbox_pull import pull

DROPBOX_PATH = "/WeaklyMeanSensitiveTuples/WeaklyMeanSensitiveTuples.tex"  # Remote file path
LOCAL_PATH = "./WeaklyMeanSensitiveTuples.tex"               # Local file to upload
TIMESTAMP_LOG = "scripts/.last_sync_time" # Local File for timekeeping

def read_last_pull_time():
    try:
        with open(TIMESTAMP_LOG, "r") as f:
            timestamp = f.read().strip()
            dt = datetime.fromisoformat(timestamp)
            # Alte Log-Einträge enthielten keine TZ-Info → als UTC interpretieren
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
    except FileNotFoundError:
        return None

def push():
    # Ensure the file exists
    if not os.path.isfile(LOCAL_PATH):
        print(f"❌ Local file not found: {LOCAL_PATH}")
        exit(1)

    try:
        dbx = get_dropbox_client()
        print(f"Check if there are unpulled changes...")
        metadata = dbx.files_get_metadata(DROPBOX_PATH)
        remote_time = metadata.server_modified
        if remote_time.tzinfo is None:           # Dropbox → naive → UTC dazudenken
            remote_time = remote_time.replace(tzinfo=timezone.utc)
        print(remote_time)
        local_time = read_last_pull_time()
        print(local_time)
        if not local_time or remote_time > local_time:
            print("⚠️ Dropbox file has been updated *after* your last pull.")
            confirm = input("❓ Create a temporary Git branch and pull new changes? [y/N] ").strip().lower()
            if confirm != "y":
                print("❌ Push aborted to prevent overwriting remote changes.")
                print("Start pulling to get remote changes.")
                pull()
                exit(1)
            else:
                print("❌ Push aborted to prevent overwriting remote changes.")
                exit(1)

        print(f"🔼 Uploading {LOCAL_PATH} to {DROPBOX_PATH}...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

    try:
        with open(LOCAL_PATH, "rb") as f:
            dbx.files_upload(
                f.read(),
                DROPBOX_PATH,
                mode=dropbox.files.WriteMode.overwrite
            )

        print("✅ Upload complete.")
        # update timestamp
        os.makedirs(os.path.dirname(TIMESTAMP_LOG), exist_ok=True)
        with open(TIMESTAMP_LOG, "w") as f:
            f.write(datetime.now(timezone.utc).isoformat())
    except Exception as e:
        print(f"❌ Dropbox push failed: {e}")
        exit(1)


if __name__ == "__main__":
    push()
