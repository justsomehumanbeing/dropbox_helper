import dropbox
import os
import subprocess

try:
    ACCESS_TOKEN = subprocess.check_output(
        ["pass", "show", "services/uni/dropbox.com/apiacesstoken"],
        text=True
    ).strip()
except subprocess.CalledProcessError as e:
    print("❌ Failed to retrieve Dropbox token from pass.")
    exit(1)

try:
    APP_KEY = subprocess.check_output(
        ["pass", "show", "services/uni/dropbox.com/appkey"],
        text=True
    ).strip()
except subprocess.CalledProcessError as e:
    print("❌ Failed to retrieve app key from pass.")
    exit(1)

try:
    APP_SECRET = subprocess.check_output(
        ["pass", "show", "services/uni/dropbox.com/appsecret"],
        text=True
    ).strip()
except subprocess.CalledProcessError as e:
    print("❌ Failed to retrieve app secret from pass.")
    exit(1)


try:
    ACCESS_CODE = subprocess.check_output(
        ["pass", "show", "services/uni/dropbox.com/refresh_token"],
        text=True
    ).strip()
except subprocess.CalledProcessError as e:
    print("❌ Failed to retrieve refresh token from pass.")
    exit(1)

flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')
oauth_result = flow.finish(ACCESS_CODE)

print("Access Token:", oauth_result.access_token)
print("Refresh Token:", oauth_result.refresh_token)
print("User ID:", oauth_result.account_id)
