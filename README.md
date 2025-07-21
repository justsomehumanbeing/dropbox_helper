# Dropbox ⇄ Git Sync Helpers

These tiny Python scripts keep **one file (or folder)** in your Dropbox perfectly in‑sync with a Git repository. They create throw‑away branches on pulls, refuse to overwrite newer remote data on pushes, and store the time of the last successful pull in a log file.

---

## 1. Prerequisites

* Python ≥ 3.10
* `pip install dropbox`
* [`pass`](https://www.passwordstore.org/) for secret management
* A Dropbox **“Scoped App”** with *files.content.write* and *files.content.read* permissions

---

## 2. Storing credentials

All secrets are kept in `pass`. Create the following entries:

```bash
pass insert services/uni/dropbox.com/appkey
pass insert services/uni/dropbox.com/appsecret
pass insert services/uni/dropbox.com/refresh_token
```

After storing your credentials, run `python authorize_once.py` once to verify everything works.

---

## 3. Configuration

Edit `config.py` to point to your Dropbox file or folder and the local paths. **No secrets** are stored in this file.
---

## 4. Usage

Pull the data from Dropbox:

```bash
python dropbox_pull.py
```

## Technical notes

The scripts rely only on the official Dropbox SDK and do not require
any additional third-party packages.  All communication with Git is
done via the command line using ``subprocess``.

Secrets can be supplied via the ``pass``password store (see ``dropbox_auth.py``).
Temporary branches are created during a pull to avoid polluting ``main``.
```bash
python dropbox_push.py
```


## 🚀 Setup Instructions (with Refresh Token Support)

This guide walks you through setting up your own Dropbox app and enabling persistent command-line access to your Dropbox account.

---


### 📌 Step-by-Step Setup

<ol>

<li>
  <p><strong>Create a Dropbox App</strong></p>
  <ul>
    <li>Go to <a href="https://www.dropbox.com/developers/apps">https://www.dropbox.com/developers/apps</a></li>
    <li>Click <em>Create App</em></li>
    <li>Select <strong>Scoped Access</strong></li>
    <li>Choose <code>App folder</code> or <code>Full Dropbox</code> access, depending on your needs</li>
    <li>Enable the following permissions under <em>OAuth 2 → Permissions</em>:
      <ul>
        <li><code>files.content.read</code></li>
        <li><code>files.content.write</code></li>
        <li><code>files.metadata.read</code></li>
      </ul>
    </li>
  </ul>
</li>

<li>
  <p><strong>Enable Refresh Token Support</strong></p>
  <ul>
    <li>Still in the app console, go to <em>OAuth 2</em></li>
    <li>Ensure <code>Access token expiration</code> is set to <strong>Short-lived</strong></li>
    <li>This enables the use of refresh tokens</li>
  </ul>
</li>

<li>
  <p><strong>Store App Credentials</strong></p>
  <pre><code>pass insert services/dropbox/appkey
pass insert services/dropbox/appsecret</code></pre>
</li>

<li>
  <p><strong>Run One-Time Authorization Flow</strong></p>
  <ul>
    <li>Use the provided <code>authorize_once.py</code> script or run this manually:</li>
  </ul>
  <pre><code>from dropbox import DropboxOAuth2FlowNoRedirect

flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET, token_access_type='offline')
auth_url = flow.start()
print("Visit:", auth_url)
</code></pre>
  <p>Then:</p>
  <pre><code># Visit the URL, log in, click "Allow", and paste the code here:
oauth_result = flow.finish("PASTE_YOUR_CODE_HERE")
print(oauth_result.access_token)
print(oauth_result.refresh_token)</code></pre>
</li>

<li>
  <p><strong>Save Refresh Token Securely</strong></p>
  <pre><code>pass insert services/dropbox/refresh_token</code></pre>
</li>

<li>
  <p><strong>Configure Your Sync Paths</strong></p>
  <p>Edit <code>config.py</code> to define the sync targets:</p>
  <pre><code>DROPBOX_REMOTE_PATH = "/your/dropbox/path.txt"
LOCAL_FILE_PATH    = Path("/home/user/path.txt")
TIMESTAMP_LOG_PATH = Path(".last_sync_time")
</code></pre>
</li>

<li>
  <p><strong>Install Dependencies</strong></p>
  <pre><code>python3 -m venv .venv
source .venv/bin/activate
pip install dropbox passlib</code></pre>
</li>

<li>
  <p><strong>Run the Tools</strong></p>
  <pre><code>python dropbox_pull.py    # Downloads the file/folder
python dropbox_push.py    # Uploads the file/folder</code></pre>
</li>

<li>
  <p><strong>Optional: Automate via Cron or Git Hook</strong></p>
  <ul>
    <li>For example: trigger <code>dropbox_push.py</code> on every <code>git commit</code></li>
  </ul>
</li>

</ol>

---

## 🔐 Token Management Details

- **Access Tokens** (short-lived): expire after ~4 hours
- **Refresh Tokens** (long-lived): used to get new access tokens automatically
- This script uses the Dropbox SDK's built-in token refresh mechanism

---

## 💡 Tips

- You can re-authorize to regenerate tokens at any time using `authorize_once.py`
- Never commit tokens or secrets to git
- If you revoke the app in Dropbox, you'll need to repeat the auth flow

---
