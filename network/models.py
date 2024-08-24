from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="followers")


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.CharField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="liked")
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE, related_name="mentions")

