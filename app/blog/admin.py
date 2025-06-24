from django.contrib import admin
from .models import ReadHistory, LikeHistory
from blog.models import Blogs
from blog.recommender.logs import mongo

admin.site.register(Blogs)


class MongoReadAdmin(admin.ModelAdmin):
    list_display = ("user_id", "blog_id", "timestamp")

    def get_queryset(self, request):
        results = mongo.reads_collection.find().sort("timestamp", -1)
        objects = [
            ReadHistory(
                user_id=doc["user_id"],
                blog_id=doc["blog_id"],
                timestamp=doc["timestamp"],
            )
            for doc in results
        ]
        return objects

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MongoLikeAdmin(admin.ModelAdmin):
    list_display = ("user_id", "blog_id", "timestamp")

    def get_queryset(self, request):
        results = mongo.likes_collection.find().sort("timestamp", -1)
        objects = [
            LikeHistory(
                user_id=doc["user_id"],
                blog_id=doc["blog_id"],
                timestamp=doc["timestamp"],
            )
            for doc in results
        ]
        return objects

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ReadHistory, MongoReadAdmin)
admin.site.register(LikeHistory, MongoLikeAdmin)
