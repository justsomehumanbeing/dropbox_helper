import subprocess
import dropbox
from typing import Tuple
import config

# ── helpers:

def _read_from_pass(field: str) -> str:
    """Return a single secret from pass or raise a crisp RuntimeError."""
    try:
        return (
            subprocess.check_output(
                ["pass", "show", f"{config.PASS_PREFIX}/{field}"],
                text=True,
            )
            .strip()
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"pass: field '{field}' not found under '{config.PASS_PREFIX}'"
        ) from exc


def _get_secret(pass_field: str) -> str:
    """Return the secret from pass."""
    return _read_from_pass(pass_field)


# ── public API:
def get_credentials() -> Tuple[str, str, str]:
    """Fetch (app_key, app_secret, refresh_token) from pass."""
    return (
        _get_secret("appkey"),
        _get_secret("appsecret"),
        _get_secret("refresh_token"),
    )


def get_dropbox_client() -> dropbox.Dropbox:
    """Return an authenticated, auto‑refreshing Dropbox client."""
    app_key, app_secret, refresh_token = get_credentials()
    try:
        dbx = dropbox.Dropbox(  oauth2_refresh_token=refresh_token,
        app_key=app_key,
        app_secret=app_secret)

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
