from typing import Any

import requests

from posts.services.exceptions import InstagramAPIError, InstagramNotFoundError, InstagramAuthError


class InstagramClient:
    """
    Клиент для работы с Instagram Graph API.
    Инкапсулирует HTTP-логику и маппинг ошибок в доменные исключения.
    """
    DEFAULT_BASE_URL = "https://graph.facebook.com/v19.0"
    DEFAULT_MEDIA_FIELDS = (
        "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp"
    )

    def __init__(
        self,
        access_token: str,
        base_url: str | None = None,
        timeout: float = 5.0,
    ) -> None:
        self.access_token = access_token
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout

    def get_user_media_page(
        self, user_id: str, next_url: str | None = None
    ) -> dict[str, Any]:
        if next_url:
            url = next_url
            params = {}
        else:
            url = f"{self.base_url}/{user_id}/media"
            params = {
                "access_token": self.access_token,
                "fields": self.DEFAULT_MEDIA_FIELDS,
            }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise InstagramAPIError(f"Instagram request failed: {exc}") from exc
        self._handle_response_errors(response)

        return response.json()

    def create_comment(self, media_id: str, text: str) -> dict[str, Any]:
        """
        Создаёт комментарий к медиа-объекту.
        """

        url = f"{self.base_url}/{media_id}/comments"
        payload = {
            "message": text,
            "access_token": self.access_token,
        }

        try:
            response = requests.post(url, data=payload, timeout=self.timeout)
        except requests.RequestException as exc:
            raise InstagramAPIError(f"Instagram request failed: {exc}") from exc
        self._handle_response_errors(response)

        return response.json()
    
    def _handle_response_errors(self, response: requests.Response) -> None:
        """
        Маппинг HTTP-статусов Instagram API в доменные исключения.
        """

        if response.status_code in (401, 403):
            raise InstagramAuthError("Instagram authentication failed")

        if response.status_code == 404:
            raise InstagramNotFoundError("Resource not found in Instagram")

        if not response.ok:
            raise InstagramAPIError(
                f"Instagram API error: {response.status_code}"
            )
