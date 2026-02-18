from django.db import models

class Post(models.Model):
    instagram_media_id = models.CharField(max_length=255, unique=True, db_index=True)
    caption = models.TextField(blank=True, default='')
    media_type = models.CharField(max_length=50)
    media_url = models.URLField(max_length=1000, blank=True, default='')
    permalink = models.URLField(max_length=1000, blank=True, default='')
    thumbnail_url = models.URLField(max_length=1000, blank=True, default='')
    instagram_timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ("-instagram_timestamp", "-id")

    def __str__(self):
        return self.instagram_media_id
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    instagram_comment_id = models.CharField(max_length=255, unique=True, db_index=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.text
    