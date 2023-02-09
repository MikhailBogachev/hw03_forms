from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import Post, Group
from .forms import PostForm


User = get_user_model()


NUM_POST_FOR_PAGE: int = 10

def index(request):
    """Вью для отображения главной страницы с публикациями"""
    template: str = 'posts/index.html'
    post_list = Post.objects.order_by('-pub_date')
    paginator = Paginator(post_list, NUM_POST_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context: dict = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Вью для отображения страниц с постами конкретной группы"""
    template: str = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(post_list, NUM_POST_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context: dict = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user).order_by('-pub_date')
    post_count = post_list.count()
    paginator = Paginator(post_list, NUM_POST_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': user,
        'page_obj': page_obj,
        'post_count': post_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    author = post.author
    post_count = Post.objects.filter(author=author).count()
    context = {
        'post': post,
        'post_count': post_count
    }
    return render(request, template, context) 


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    group = Group.objects.all()
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/profile/{post.author}/', {'form': form})
    return render(request, 'posts/create_post.html', {'form': form, 'group': group})


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST, instance=post)
    is_edit = True
    context = {
        'form': form,
        'is_edit': is_edit,
        'post': post
    }
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', context)