from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    CommentForm,
    PostForm,
    UserEditForm,
    UserRegistrationForm,
)
from .models import Category, Comment, Post


User = get_user_model()


def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    posts = (
        Post.objects
        .select_related('author', 'category', 'location')
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )

    page_obj = paginate_queryset(request, posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    posts = (
        Post.objects
        .select_related('author', 'category', 'location')
        .prefetch_related('comments')
        .filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now(),
        )
        .order_by('-pub_date')
    )

    page_obj = paginate_queryset(request, posts)

    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': page_obj,
        },
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects
        .select_related('author', 'category', 'location')
        .prefetch_related('comments__author'),
        id=post_id,
    )

    if not post.is_published or post.pub_date > timezone.now():
        if request.user != post.author:
            raise Http404

    comments = (
        post.comments
        .select_related('author')
        .order_by('created_at')
    )
    form = CommentForm()

    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
        },
    )


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', request.user.username)
    else:
        form = PostForm()

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', request.user.username)

    return render(
        request,
        'blog/confirm_delete.html',
        {
            'object': post,
            'type': 'post',
        },
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

        url = reverse('blog:post_detail', args=(post.id,))
        return HttpResponseRedirect(
            f'{url}#comment_{comment.id}'
        )

    return redirect('blog:post_detail', post.id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id,
    )

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        form = CommentForm(
            request.POST,
            instance=comment,
        )
        if form.is_valid():
            form.save()
            url = reverse(
                'blog:post_detail',
                args=(post_id,),
            )
            return HttpResponseRedirect(
                f'{url}#comment_{comment.id}'
            )
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        'blog/comment.html',
        {
            'form': form,
            'comment': comment,
            'object': comment,
        },
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id,
    )

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)

    return render(
        request,
        'blog/comment.html',
        {
            'comment': comment,
            'object': comment,
        },
    )


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
    else:
        form = UserRegistrationForm()

    return render(
        request,
        'registration/registration_form.html',
        {'form': form},
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user.is_authenticated and request.user == profile_user:
        posts = Post.objects.filter(author=profile_user)
    else:
        posts = Post.objects.filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    posts = (
        posts
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )

    page_obj = paginate_queryset(request, posts)

    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile_user,
            'page_obj': page_obj,
        },
    )


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserEditForm(
            request.POST,
            instance=user,
        )
        if form.is_valid():
            form.save()
            return redirect('blog:profile', user.username)
    else:
        form = UserEditForm(instance=user)

    return render(
        request,
        'blog/user.html',
        {'form': form},
    )
