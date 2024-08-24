from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import ObjectDoesNotExist
import json

from .models import User, Post


def index(request):
    page = request.GET.get("page", 1)
    try:
        page = int(page)
        if page < 1:
            return redirect(reverse("index"))
    except ValueError:
        return redirect(reverse("index"))

    posts = Post.objects.filter(parent=None).order_by('-date')
    paginator = Paginator(posts, 10)

    try:
        current = paginator.page(page)
    except EmptyPage:
        return redirect(reverse("index"))  # Redirect if page number is out of range

    post_data = []
    for post in current:
        post_data.append({
            'id': post.id,
            'content': post.post,
            'author': post.author.get_username(),
            'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),
            'likes': post.likes.count(),
            'userLiked': request.user in post.likes.all(),
            'isAuthor': request.user == post.author
        })

    return render(request, "network/index.html", {
        "page_obj": current,
        "posts": post_data
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url="/login", redirect_field_name=None)
def new_post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get('content', '')
        if not content or len(content) > 280:
            return JsonResponse({"error": "Content cannot be empty or more than 280 characters."}, status=400)

        post = Post(author=request.user, post=content)
        post.save()

        return JsonResponse({"message": "Post created successfully."}, status=201)


@login_required(login_url="/login", redirect_field_name=None)
def like_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return JsonResponse({"likes": post.likes.count(), "userLiked": request.user in post.likes.all()})


@login_required(login_url="/login", redirect_field_name=None)
def comment_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        data = json.loads(request.body)
        content = data.get('content', '')
        if not content or len(content) > 280:
            return JsonResponse({"error": "Content cannot be empty or more than 280 characters."}, status=400)

        comment = Post(author=request.user, post=content, parent=post)
        comment.save()

        return JsonResponse({"message": "Comment added successfully."}, status=201)


@login_required(login_url="/login", redirect_field_name=None)
def edit_post(request, post_id):
    if request.method == "PUT":
        post = Post.objects.get(id=post_id)

        if post.author != request.user:
            return JsonResponse({"error": "You are not authorized to edit this post."}, status=403)

        data = json.loads(request.body)
        new_content = data.get('content', '')

        if not new_content or len(new_content) > 280:
            return JsonResponse({"error": "Content cannot be empty or more thane 280 characters."}, status=400)

        post.post = new_content
        post.save()

        return JsonResponse({
            "message": "Post updated successfully.",
            "content": new_content
        }, status=200)


def user(request, name):
    try:
        user = User.objects.get(username=name)
    except ObjectDoesNotExist:
        return HttpResponse("Not Found", status=404)

    if request.user:
        profile = {
            "username": user.username,
            "isself": request.user == user,
            "isfollowing": request.user in user.followers.all(),
            "followercount": user.followers.count(),
            "followingcount": user.following.count(),
        }
    else:
        profile = {
            "username": user.username,
            "followercount": user.followers.count(),
            "followingcount": user.following.count(),
        }

    posts = Post.objects.filter( Q(author=user) & Q(parent__isnull=True)).order_by('-date')
    post_data = []
    for post in posts:
        post_data.append({
            'id': post.id,
            'content': post.post,
            'author': post.author.get_username(),
            'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),
            'likes': post.likes.count(),
            'userLiked': request.user in post.likes.all(),
            'isAuthor': request.user == post.author
        })

    return render(request, "network/user.html", {
        "profile": profile,
        "posts": post_data
    })


@login_required(login_url="/login", redirect_field_name=None)
def following(request):
    page = request.GET.get("page", 1)
    try:
        page = int(page)
        if page < 1:
            return redirect(reverse("index"))
    except ValueError:
        return redirect(reverse("index"))

    posts = Post.objects.filter( Q(author__in=request.user.following.all()) & Q(parent__isnull=True)).order_by('-date')
    paginator = Paginator(posts, 10)

    try:
        current = paginator.page(page)
    except EmptyPage:
        return redirect(reverse("index"))  # Redirect if page number is out of range

    post_data = []
    for post in current:
        post_data.append({
            'id': post.id,
            'content': post.post,
            'author': post.author.get_username(),
            'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),
            'likes': post.likes.count(),
            'userLiked': request.user in post.likes.all(),
            'isAuthor': request.user == post.author
        })

    return render(request, "network/following.html", {
        "page_obj": current,
        "posts": post_data
    })


def post(request, post_id):
    try:
        parent = Post.objects.get(id=post_id)
        parent_obj = {
            'id': parent.id,
            'content': parent.post,
            'author': parent.author.get_username(),
            'date': parent.date.strftime('%Y-%m-%d %H:%M:%S'),
            'likes': parent.likes.count(),
            'userLiked': request.user in parent.likes.all(),
            'isAuthor': request.user == parent.author
        }
    except ObjectDoesNotExist:
        return HttpResponse("Not Found", status=404)

    posts = Post.objects.filter(parent=parent).order_by('-date')
    post_data = []
    for post in posts:
        post_data.append({
            'id': post.id,
            'content': post.post,
            'author': post.author.get_username(),
            'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),
            'likes': post.likes.count(),
            'userLiked': request.user in post.likes.all(),
            'isAuthor': request.user == post.author
        })

    return render(request, "network/post.html", {
        "parent": parent_obj,
        "posts": post_data,
        "count": len(post_data)
    })

@login_required(login_url="/login", redirect_field_name=None)
def follow(request, name):
    if request.method == "POST":
        try:
            user = User.objects.get(username=name)
        except ObjectDoesNotExist:
            JsonResponse({"error": "Not found."}, status=404)

        if request.user in user.followers.all():
            user.followers.remove(request.user)
            message = "unfollowed"
        else:
            user.followers.add(request.user)
            message = "followed"

        return JsonResponse({
            "message": message,
            "followers": user.followers.count(),
            "following": user.following.count()
            })
    return JsonResponse({"error": "Only valid method is POST."}, status=404)
