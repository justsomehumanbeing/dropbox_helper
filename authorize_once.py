"""Interactive helper to obtain a Dropbox refresh token."""

from dropbox.oauth import DropboxOAuth2FlowNoRedirect
import subprocess
import config


def _read_from_pass(field: str) -> str | None:
    """Return the secret from ``pass`` if available."""
    try:
        return (
            subprocess.check_output(
                ["pass", "show", f"{config.PASS_PREFIX}/{field}"],
                text=True,
            ).strip()
        )
    except subprocess.CalledProcessError:
        return None


def main() -> None:
    """Start an OAuth flow and print the resulting tokens."""
    app_key = _read_from_pass("appkey") or input("Dropbox app key: ").strip()
    app_secret = _read_from_pass("appsecret") or input("Dropbox app secret: ").strip()

    flow = DropboxOAuth2FlowNoRedirect(app_key, app_secret, token_access_type="offline")
    authorize_url = flow.start()
    print("1. Visit:", authorize_url)
    print("2. Click 'Allow' and copy the authorization code.")
    code = input("Paste code here: ").strip()

    try:
        result = flow.finish(code)
    except Exception as exc:
        print(f"\u274c Authorization failed: {exc}")
        return

    print("Access Token:", result.access_token)
    print("Refresh Token:", result.refresh_token)
    print("User ID:", result.account_id)


if __name__ == "__main__":
    main()
