"""OIDC / SSO stub (ready for Keycloak, Azure AD, Google)."""
import os
from typing import Optional
from fastapi import HTTPException

OIDC_ENABLED = os.getenv("OIDC_ENABLED", "false").lower() == "true"
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID", "")


def get_oidc_login_url() -> Optional[str]:
    if not OIDC_ENABLED or not OIDC_ISSUER:
        return None
    return f"{OIDC_ISSUER}/protocol/openid-connect/auth?client_id={OIDC_CLIENT_ID}&response_type=code"


def validate_oidc_token(token: str) -> dict:
    """Placeholder. In production integrate with python-jose + JWKS."""
    if not OIDC_ENABLED:
        raise HTTPException(status_code=501, detail="OIDC not enabled")
    # Real implementation would fetch JWKS and validate
    return {"sub": "oidc-user", "role": "viewer"}
