from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (CreateView,
                                  DeleteView,
                                  DetailView,
                                  ListView,
                                  UpdateView)

from .blog_constants import INDEX_POSTS_LIMITER
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post, User
from blogicum.forms import ProfileUpdate


def selection(model_name):
    return (
        model_name.select_related(
            'author',
            'location',
            'category'
        )
    )


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = INDEX_POSTS_LIMITER

    def get_queryset(self):
        qs = selection(Post.objects).filter(
            author__username=self.kwargs['username']
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        if self.request.user != self.kwargs['username']:
            qs.filter(pub_date__lte=now(),
                      is_published=True,
                      category__is_published=True,
                      )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    form_class = ProfileUpdate
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return get_object_or_404(User, username=self.request.user)


class IndexListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    ordering = '-pub_date'
    paginate_by = INDEX_POSTS_LIMITER

    def get_queryset(self):
        post_list = selection(Post.objects.filter(
            pub_date__lte=now(),
            is_published=True,
            category__is_published=True,)
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return post_list


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self):
        post = get_object_or_404(
            selection(Post.objects),
            pk=self.kwargs['pk'])
        if self.request.user != post.author:
            post = get_object_or_404(
                selection(Post.objects),
                pk=self.kwargs['pk'],
                pub_date__lte=now(),
                is_published=True,
                category__is_published=True
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.select_related(
            'author'
        )
        return context


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post'
    paginate_by = INDEX_POSTS_LIMITER

    def get_category(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return category

    def get_queryset(self):
        qs = selection(self.get_category().posts).filter(
            pub_date__lte=now(),
            is_published=True,
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if 'image' in self.request.FILES:
            form.instance.image = self.request.FILES['image']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['post_id']})


@login_required
def delete_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id, author=request.user)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', context)


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_id = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.post_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_id.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def is_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:index')


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = 'blog:index'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['post_id']})
