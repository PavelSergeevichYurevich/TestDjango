from rest_framework import serializers
from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "instagram_media_id",
            "caption",
            "media_type",
            "media_url",
            "permalink",
            "thumbnail_url",
            "instagram_timestamp",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "instagram_comment_id",
            "text",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]
        
class CreateCommentSerializer(serializers.Serializer):
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1000,
    )
   
