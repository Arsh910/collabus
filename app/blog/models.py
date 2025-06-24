from django.db import models


class Blogs(models.Model):
    title = models.CharField(max_length=255, blank=False)
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="blogs"
    )
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True, blank=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# proxy models
class ReadHistory(models.Model):
    user_id = models.CharField(max_length=255)
    blog_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        verbose_name = "Read History"
        verbose_name_plural = "Read Histories"


class LikeHistory(models.Model):
    user_id = models.CharField(max_length=255)
    blog_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        verbose_name = "Like History"
        verbose_name_plural = "Like Histories"
