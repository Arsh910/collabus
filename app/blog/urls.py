from django.urls import path
from blog.views import (
    CreateBlogView,
    UpdateBlogView,
    LikedBlogs,
    RecommendBlogs,
    RecommendAuthors,
)

app_name = "blog"

urlpatterns = [
    path("create/", CreateBlogView.as_view(), name="create"),
    path("manage/<int:pk>/", UpdateBlogView.as_view(), name="manage"),
    path("like/", LikedBlogs.as_view(), name="like"),
    path("recommend/", RecommendBlogs.as_view(), name="recommend"),
    path("recommend_auth/", RecommendAuthors.as_view(), name="recommend_auth"),
]
