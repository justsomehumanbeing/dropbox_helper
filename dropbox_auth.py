import dropbox
import os
import subprocess
from dropbox.oauth import DropboxOAuth2FlowNoRedirect

# Load tokens and secrets from pass (this will open GPG prompt if needed)

def get_secrets():
    try:
        APP_KEY = subprocess.check_output(
            ["pass", "show", "services/uni/dropbox.com/appkey"],
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to retrieve app key from pass: {e}")
        exit(1)

    try:
        APP_SECRET = subprocess.check_output(
            ["pass", "show", "services/uni/dropbox.com/appsecret"],
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to retrieve app secret from pass: {e}")
        exit(1)

    try:
        REFRESH_TOKEN = subprocess.check_output(
            ["pass", "show", "services/uni/dropbox.com/refresh_token"],
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to retrieve app secret from pass: {e}")
        exit(1)

    if not (APP_KEY and APP_SECRET and REFRESH_TOKEN):
        raise RuntimeError("Missing Dropbox app credentials or refresh token.")

    return (APP_KEY, APP_SECRET, REFRESH_TOKEN)

# Create Dropbox client with auto-refresh support
def get_dropbox_client():

    (APP_KEY, APP_SECRET, REFRESH_TOKEN) = get_secrets()
    try: dbx = dropbox.Dropbox(
        oauth2_refresh_token=REFRESH_TOKEN,
        app_key=APP_KEY,
        app_secret=APP_SECRET,
    )

    except dropbox.exceptions.AuthError as err:
        print(f"❌ Invalid Dropbox access token: {err}")
        return err
    except dropbox.exceptions.ApiError as err:
        print(f"❌ Dropbox API error: {err}")
        return err
    except Exception as err:
        print(f"❌ Unexpected error: {err}")
        return err

    return dbx
