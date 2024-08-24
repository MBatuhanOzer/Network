
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post/<int:post_id>", views.post, name="post"),
    path("posts/new", views.new_post, name="new_post"),
    path("posts/<int:post_id>/like", views.like_post, name="like_post"),
    path("posts/<int:post_id>/comment", views.comment_post, name="comment_post"),
    path("posts/<int:post_id>/edit", views.edit_post, name="edit_post"),
    path("user/<str:name>", views.user, name="user"),
    path("following", views.following, name="following"),
    path("follow/<str:name>", views.follow, name="follow")
]
