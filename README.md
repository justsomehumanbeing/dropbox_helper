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
=======
```bash
python dropbox_push.py