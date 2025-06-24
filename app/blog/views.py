from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from blog.serializer import BlogSerializer
from django.contrib.auth import get_user_model
from blog.models import Blogs
from blog.recommender.logs import mongo
from blog.recommender.recommend import recommend, recommend_authors

# Create your views here.


class CreateBlogView(generics.CreateAPIView):
    """Create a new blog"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlogSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UpdateBlogView(generics.RetrieveUpdateAPIView):
    """Retrive  and update the user"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlogSerializer
    queryset = Blogs.objects.all()

    def get_object(self):
        blog = super().get_object()

        if self.request.method in ["PUT", "PATCH"]:
            if blog.user != self.request.user:
                raise PermissionDenied("You cannot update another user's blog.")

        try:
            mongo.log_read_event(user_id=self.request.user.id, blog_id=blog.id)
        except Exception as e:
            print(f"[MongoDB Log Error] {e}")

        return blog


class LikedBlogs(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        blog_id = request.data.get("blog_id")
        user_id = request.user.id

        if not blog_id:
            return Response(
                {"error": "Missing blog_id in query params."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mongo.log_like_event(blog_id=blog_id, user_id=user_id)

        return Response(status=status.HTTP_200_OK)

    def delete(self, request):
        """Remove a like event."""
        blog_id = request.data.get("blog_id")
        user_id = request.user.id

        if not blog_id:
            return Response(
                {"error": "Missing blog_id in request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        deleted = mongo.remove_like_event(blog_id=blog_id, user_id=user_id)

        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Like not found."}, status=status.HTTP_404_NOT_FOUND)


class RecommendBlogs(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        data = recommend(user.id, user.last_visit)
        r_blogs = data["recommended_blogs"]

        blogs_list = []

        for blog in r_blogs:
            blog_obj = Blogs.objects.get(id=blog["id"])
            d = {
                "blog_id": blog_obj.id,
                "author_id": blog_obj.user.id,
                "author_image": f"{blog_obj.user.get_profile_image_url()}",
                "blog_image": "",
            }
            blogs_list.append(d)

        return Response(
            {"user_id": user.id, "blogs": blogs_list}, status=status.HTTP_200_OK
        )


class RecommendAuthors(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        data = recommend_authors(user.id)
        r_authors = data["recommended_authors"]

        authors_list = []
        for author_id in r_authors:
            author_obj = get_user_model().objects.get(id=int(author_id))
            d = {
                "author_id": author_obj.id,
                "author_image": f"{author_obj.get_profile_image_url()}",
            }
            authors_list.append(d)

        return Response(
            {"user_id": user.id, "authors": authors_list}, status=status.HTTP_200_OK
        )
