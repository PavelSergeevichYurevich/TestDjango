from datetime import datetime, timezone as dt_timezone
from typing import Optional

from django.utils.dateparse import parse_datetime
from django.utils import timezone

from posts.models import Post, Comment
from posts.services.exceptions import InstagramAPIError
from posts.services.instagram_client import InstagramClient


class InstagramService:
    """
    Сервисный слой для синхронизации и взаимодействия
    с Instagram через InstagramClient.
    """

    def __init__(self, client: InstagramClient) -> None:
        self.client = client

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def sync_user_media(self, user_id: str) -> int:
        """
        Синхронизирует все страницы медиа пользователя.
        Делает upsert Post по instagram_media_id.
        Возвращает количество обработанных постов.
        """

        processed_count = 0
        next_url: Optional[str] = None

        while True:
            page = self.client.get_user_media_page(
                user_id=user_id,
                next_url=next_url,
            )

            data = page.get("data", [])
            paging = page.get("paging", {})

            for item in data:
                instagram_id = item["id"]
                caption = item.get("caption", "")
                media_type = item.get("media_type") or "UNKNOWN"
                media_url = item.get("media_url", "")
                permalink = item.get("permalink", "")
                thumbnail_url = item.get("thumbnail_url", "")
                timestamp_raw = item.get("timestamp")

                instagram_timestamp = self._parse_instagram_timestamp(
                    timestamp_raw
                )

                Post.objects.update_or_create(
                    instagram_media_id=instagram_id,
                    defaults={
                        "caption": caption,
                        "media_type": media_type,
                        "media_url": media_url,
                        "permalink": permalink,
                        "thumbnail_url": thumbnail_url,
                        "instagram_timestamp": instagram_timestamp,
                    },
                )

                processed_count += 1

            next_url = paging.get("next")
            if not next_url:
                break

        return processed_count

    def create_comment_for_post(
        self,
        local_post_id: int,
        text: str,
    ) -> Comment:
        """
        Создаёт комментарий к локальному Post.
        Отправляет комментарий в Instagram и сохраняет
        его в локальную БД только при успешном ответе.
        """

        post = Post.objects.get(pk=local_post_id)

        response = self.client.create_comment(
            media_id=post.instagram_media_id,
            text=text,
        )
        comment_id = response.get("id")
        if not comment_id:
            raise InstagramAPIError(
                "Instagram API returned success without comment id"
            )

        # Если клиент не выбросил исключение —
        # значит ответ успешный (2xx)
        comment = Comment.objects.create(
            post=post,
            text=text,
            instagram_comment_id=comment_id,
        )

        return comment

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _parse_instagram_timestamp(
        self,
        value: Optional[str],
    ) -> Optional[datetime]:
        """
        Парсит timestamp из Instagram в aware datetime.
        """

        if not value:
            return None

        dt = parse_datetime(value)

        if dt is None:
            return None

        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone=dt_timezone.utc)

        return dt
