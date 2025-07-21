# Dropbox ⇄ Git Sync Helpers

These tiny Python scripts keep **one file (or folder)** in your Dropbox
perfectly in‑sync with a Git repository.
They create throw‑away branches on pulls,
refuse to overwrite newer remote data on pushes,
and store the time of the last successful pull in a tiny log file.

---

## 1. Prerequisites

* Python ≥ 3.10
* `pip install dropbox python-dotenv`
* A Dropbox **“Scoped App”** with _files.content.write_ +
  _files.content.read_ permissions
  (Dashboard → “App Console” → Create App → Scoped Access)

---

## 2. Getting credentials **once**

```bash
# a) set two env vars temporarily …
export DROPBOX_APP_KEY=…  DROPBOX_APP_SECRET=…

# b) run the helper (prints refresh token):
python authorize_once.py
```

---

## Technical notes

The scripts rely only on the official Dropbox SDK and do not require
any additional third-party packages.  All communication with Git is
done via the command line using ``subprocess``.

Secrets can be supplied via environment variables or the ``pass``
password store (see ``dropbox_auth.py``).  Temporary branches are
created during a pull to avoid polluting ``main``.
