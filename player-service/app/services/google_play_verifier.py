import json
from dataclasses import dataclass
from pathlib import Path

import httpx

from app.core.config import settings


GOOGLE_PLAY_API_BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3"
GOOGLE_OAUTH_SCOPE = "https://www.googleapis.com/auth/androidpublisher"


@dataclass
class VerifyResult:
    valid: bool
    error: str | None = None


class GooglePlayVerifier:
    """Verifies a Google Play purchase token via the Android Publisher API.

    In DEV_MODE, accepts any token prefixed with `mock_` without contacting Google.
    """

    async def verify(self, purchase_token: str, sku: str) -> VerifyResult:
        if settings.DEV_MODE and purchase_token.startswith("mock_"):
            return VerifyResult(valid=True)

        if not settings.GOOGLE_PLAY_PACKAGE_NAME or not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
            return VerifyResult(
                valid=False,
                error="google_play_not_configured",
            )

        try:
            access_token = await self._get_access_token()
        except Exception as exc:  # noqa: BLE001
            return VerifyResult(valid=False, error=f"oauth_failed:{exc}")

        url = (
            f"{GOOGLE_PLAY_API_BASE}/applications/{settings.GOOGLE_PLAY_PACKAGE_NAME}"
            f"/purchases/products/{sku}/tokens/{purchase_token}"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers={"Authorization": f"Bearer {access_token}"})

        if resp.status_code != 200:
            return VerifyResult(valid=False, error=f"google_status_{resp.status_code}")

        body = resp.json()
        # purchaseState: 0 = purchased, 1 = canceled, 2 = pending
        if body.get("purchaseState", -1) != 0:
            return VerifyResult(valid=False, error="purchase_not_completed")

        return VerifyResult(valid=True)

    async def _get_access_token(self) -> str:
        # google-auth handles service-account JWT signing + token exchange.
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request

        sa_path = Path(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        with sa_path.open("r", encoding="utf-8") as f:
            sa_info = json.load(f)

        creds = service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=[GOOGLE_OAUTH_SCOPE],
        )
        creds.refresh(Request())
        return creds.token
