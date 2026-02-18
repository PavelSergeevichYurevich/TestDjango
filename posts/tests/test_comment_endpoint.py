from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from posts.models import Post, Comment
from posts.services.exceptions import InstagramNotFoundError


@override_settings(INSTAGRAM_ACCESS_TOKEN="test-token")
class TestCreateCommentEndpoint(APITestCase):
    def test_create_comment_success(self) -> None:
        post = Post.objects.create(
            instagram_media_id="ig_123",
            media_type="IMAGE",
        )

        url = f"/api/posts/{post.id}/comment/"
        payload = {"text": "hello"}

        with patch(
            "posts.services.instagram_client.InstagramClient.create_comment"
        ) as mock_create_comment:
            mock_create_comment.return_value = {"id": "ig_comment_123"}
            response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

        comment = Comment.objects.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.text, "hello")
        self.assertEqual(comment.instagram_comment_id, "ig_comment_123")

        self.assertEqual(response.data["text"], "hello")
        self.assertEqual(response.data["instagram_comment_id"], "ig_comment_123")

    def test_create_comment_local_post_not_found(self) -> None:
        url = "/api/posts/999/comment/"
        payload = {"text": "hello"}

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 0)

    def test_create_comment_instagram_not_found(self) -> None:
        post = Post.objects.create(
            instagram_media_id="ig_123",
            media_type="IMAGE",
        )

        url = f"/api/posts/{post.id}/comment/"
        payload = {"text": "hello"}

        with patch(
            "posts.services.instagram_client.InstagramClient.create_comment"
        ) as mock_create_comment:
            mock_create_comment.side_effect = InstagramNotFoundError(
                "Not found in Instagram"
            )
            response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 0)
