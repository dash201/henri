from django.shortcuts import render
from henri.blog.models import (Post, Category, Comment, ViewCount)
from henri.blog.forms import CommentForm


def visitor_ip_address(request):
    """
    Get and return user ip address
    :param request:
    :return ip:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def posts(request):
    """
    list all available posts
    :param request:
    :return context:
    """
    all_posts = Post.objects.filter(published=True)
    cats = Category.objects.all()

    context = {'posts': all_posts, 'cats': cats}
    return render(request, 'post.html', context)


def details(request, slug):
    """
    Return details for a specific post
    :param request:
    :param slug:
    :return context:
    """
    post = Post.objects.get(slug=slug)  # Get post
    cats = Category.objects.all()  # get all posts categories

    ip = visitor_ip_address(request)  # get visitor ip
    post_ip = ViewCount.objects.filter(post=post, ip_adress=ip)  # get view object for user_ip and post

    if post_ip:
        # check if the visitor has already read this post
        post.view = post.view
        post.save()
    elif not post_ip and post.published:
        # check if the visitor has not read this post and if post is already published
        # add new view for the post
        new_ip = ViewCount(post=post, ip_adress=ip)
        new_ip.save()
        post.view += 1
        post.save()

    form = CommentForm
    if request.method == 'POST':
        form = CommentForm(data=request.POST)  # get form data
        if form.is_valid():
            # check form validity and save comment
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

    comments = Comment.objects.filter(post=post.id)  # get all comment for the post
    context = {'post': post, 'cats': cats, 'comments': comments, 'form': form}
    return render(request, 'post-details.html', context)


def categories(request, category):
    """
    list all available posts by category
    :param request:
    :param category:
    :return:
    """
    posts = Post.objects.filter(category__title=category, published=True)
    cats = Category.objects.all()
    cat_title = category

    context = {'posts': posts, 'cats': cats, 'cat_title': cat_title}
    return render(request, 'category.html', context)
