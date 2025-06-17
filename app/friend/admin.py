from django.contrib import admin
from .models import Friendship


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "created_at")
    search_fields = ("from_user",)
    readonly_fields = ("created_at",)


admin.site.register(Friendship, FriendshipAdmin)
