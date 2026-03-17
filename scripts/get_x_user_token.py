from __future__ import annotations

import argparse
import base64
import hashlib
import os
import secrets
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


AUTH_URL = "https://x.com/i/oauth2/authorize"
TOKEN_URL = "https://api.x.com/2/oauth2/token"
USERS_ME_URL = "https://api.x.com/2/users/me"
SCOPES = ["bookmark.read", "tweet.read", "users.read", "offline.access"]


def load_env() -> dict[str, str]:
    load_dotenv(PROJECT_ROOT / ".env")
    values = {
        "client_id": os.getenv("X_CLIENT_ID", "").strip(),
        "client_secret": os.getenv("X_CLIENT_SECRET", "").strip(),
        "redirect_uri": os.getenv("X_REDIRECT_URI", "").strip(),
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        env_names = ", ".join(
            {
                "client_id": "X_CLIENT_ID",
                "client_secret": "X_CLIENT_SECRET",
                "redirect_uri": "X_REDIRECT_URI",
            }[name]
            for name in missing
        )
        raise RuntimeError(f"Missing required environment values: {env_names}")
    return values


def generate_pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest()).decode("utf-8").rstrip("=")
    return verifier, challenge


def build_authorization_url(client_id: str, redirect_uri: str, state: str, code_challenge: str) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def parse_callback_input(raw_value: str) -> tuple[str, str | None]:
    value = raw_value.strip()
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        params = parse_qs(parsed.query)
        code = (params.get("code") or [""])[0].strip()
        state = (params.get("state") or [""])[0].strip() or None
        if not code:
            raise RuntimeError("The callback URL did not contain a code parameter.")
        return code, state
    return value, None


def token_debug_summary(token_payload: dict) -> dict[str, object]:
    scope_value = token_payload.get("scope")
    if isinstance(scope_value, list):
        granted_scope = " ".join(str(item).strip() for item in scope_value if str(item).strip())
    elif scope_value is None:
        granted_scope = None
    else:
        granted_scope = str(scope_value).strip() or None
    return {
        "token_type": token_payload.get("token_type"),
        "expires_in": token_payload.get("expires_in"),
        "has_refresh_token": bool(token_payload.get("refresh_token")),
        "granted_scope": granted_scope,
    }


def exchange_code_for_tokens(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
    code_verifier: str,
) -> dict:
    basic_token = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "code": code,
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=45)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Token exchange failed with HTTP {response.status_code}. "
            "Make sure the code was just generated, the redirect URI matches exactly, and the app is configured for OAuth 2.0."
        ) from exc
    return response.json()


def fetch_user_profile(access_token: str) -> requests.Response:
    response = requests.get(
        USERS_ME_URL,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        params={"user.fields": "id,username,name"},
        timeout=45,
    )
    return response


def explain_users_me_failure(status_code: int, response_body: str, granted_scope: str | None) -> str:
    body_lower = response_body.lower()
    granted_scope_lower = (granted_scope or "").lower()
    requested_scope_lower = " ".join(SCOPES).lower()

    if status_code == 403:
        if "scope" in body_lower or "permission" in body_lower:
            return (
                "This looks like a missing-scope or permission-level failure. "
                f"Requested scopes were: {requested_scope_lower}. "
                f"Granted scopes were: {granted_scope_lower or 'not returned by X'}."
            )
        if granted_scope and "users.read" not in granted_scope_lower:
            return (
                "This looks like a missing users.read scope on the granted token. "
                f"Granted scopes were: {granted_scope_lower}."
            )
        return (
            "This is a 403 after a successful token exchange, which usually means the token is valid but the app, "
            "granted scopes, or project access level is not allowed to call /2/users/me."
        )

    if status_code == 401:
        return "This looks like an invalid, expired, or malformed bearer token rather than a scope issue."

    return "This does not look like a simple missing-scope failure. Check the response body and X app configuration."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="One-time helper to obtain X_USER_ACCESS_TOKEN and X_USER_ID.")
    parser.add_argument(
        "--callback-url",
        help="Optional full callback URL copied from the browser after authorization.",
    )
    parser.add_argument(
        "--code",
        help="Optional raw authorization code if you are pasting only the code value.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env = load_env()

    code_verifier, code_challenge = generate_pkce_pair()
    expected_state = secrets.token_urlsafe(24)
    authorization_url = build_authorization_url(
        client_id=env["client_id"],
        redirect_uri=env["redirect_uri"],
        state=expected_state,
        code_challenge=code_challenge,
    )

    print("Visit this URL in your browser and authorize the app:\n")
    print(authorization_url)
    print("\nRequested scopes:")
    print(", ".join(SCOPES))
    print("\nAfter approval, paste either the full callback URL or the raw code.\n")

    if args.callback_url:
        raw_input_value = args.callback_url
    elif args.code:
        raw_input_value = args.code
    else:
        raw_input_value = input("Callback URL or code: ").strip()

    code, returned_state = parse_callback_input(raw_input_value)
    if returned_state and returned_state != expected_state:
        raise RuntimeError("State mismatch. Restart the flow and use the new authorization URL.")

    token_payload = exchange_code_for_tokens(
        client_id=env["client_id"],
        client_secret=env["client_secret"],
        redirect_uri=env["redirect_uri"],
        code=code,
        code_verifier=code_verifier,
    )

    access_token = str(token_payload.get("access_token", "")).strip()
    if not access_token:
        raise RuntimeError("Token response did not include an access_token.")

    summary = token_debug_summary(token_payload)
    print("\nToken response summary:")
    print(f"token_type={summary['token_type']}")
    print(f"expires_in={summary['expires_in']}")
    print(f"has_refresh_token={summary['has_refresh_token']}")
    print(f"granted_scope={summary['granted_scope']}")

    profile_response = fetch_user_profile(access_token)
    if profile_response.status_code != 200:
        response_body = profile_response.text.strip()
        print("\nGET /2/users/me failed.")
        print(f"status_code={profile_response.status_code}")
        print(f"response_body={response_body}")
        print(
            "explanation="
            + explain_users_me_failure(
                profile_response.status_code,
                response_body,
                summary["granted_scope"] if isinstance(summary["granted_scope"], str) else None,
            )
        )
        return 1

    profile_payload = profile_response.json()
    user_data = profile_payload.get("data", {})
    user_id = str(user_data.get("id", "")).strip()
    if not user_id:
        raise RuntimeError("GET /2/users/me did not return a user ID.")

    print("\nToken exchange and /2/users/me succeeded.")
    print("Raw tokens are intentionally not printed.")
    print("Add these values to your .env:\n")
    print("X_USER_ACCESS_TOKEN=<redacted>")
    print(f"X_USER_ID={user_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
