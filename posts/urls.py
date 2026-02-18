from django.urls import path
from .views import CreateCommentView, HealthCheckView, PostListView, SyncPostsView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    
    # синхронизация Instagram
    path("sync/", SyncPostsView.as_view(), name="sync-posts"),

    # список постов
    path("posts/", PostListView.as_view(), name="post-list"),

    # создать комментарий к посту
    path(
        "posts/<int:id>/comment/",
        CreateCommentView.as_view(),
        name="create-comment",
    ),
]
