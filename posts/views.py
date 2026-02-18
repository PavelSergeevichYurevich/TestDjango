from django.db import OperationalError, connection
from django.conf import settings
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from .models import Post
from .serializers import (
    PostSerializer,
    CreateCommentSerializer,
    CommentSerializer,
)
from .pagination import PostCursorPagination
from posts.services.instagram_client import InstagramClient
from posts.services.instagram_service import InstagramService
from posts.services.exceptions import (
    InstagramAPIError,
    InstagramAuthError,
    InstagramNotFoundError,
)


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            connection.ensure_connection()
            db_status = "ok"
        except OperationalError:
            db_status = "error"

        if db_status == "ok":
            return Response({"status": "ok"}, status=200)
        return Response({"status": "error"}, status=503)


class SyncPostsView(APIView):
    """
    Запускает синхронизацию постов пользователя из Instagram.
    """

    def post(self, request):
        access_token = settings.INSTAGRAM_ACCESS_TOKEN
        user_id = settings.INSTAGRAM_USER_ID

        client = InstagramClient(access_token=access_token)
        service = InstagramService(client=client)

        try:
            synced_count = service.sync_user_media(user_id=user_id)
        except InstagramAuthError:
            return Response(
                {"detail": "Instagram authentication failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except InstagramAPIError:
            return Response(
                {"detail": "Instagram API error"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {"synced_count": synced_count},
            status=status.HTTP_200_OK,
        )

class PostListView(ListAPIView):
    """
    Список локальных постов с CursorPagination.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostCursorPagination


class CreateCommentView(APIView):
    """
    Создаёт комментарий к посту.
    """

    def post(self, request, id: int):
        serializer = CreateCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = settings.INSTAGRAM_ACCESS_TOKEN
        client = InstagramClient(access_token=access_token)
        service = InstagramService(client=client)

        try:
            comment = service.create_comment_for_post(
                local_post_id=id,
                text=serializer.validated_data["text"],
            )
        except Post.DoesNotExist:
            raise Http404("Post not found")
        except InstagramNotFoundError:
            return Response(
                {"detail": "Post not found in Instagram"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InstagramAuthError:
            return Response(
                {"detail": "Instagram authentication failed"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except InstagramAPIError:
            return Response(
                {"detail": "Instagram API error"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )
