from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (CreateView,
                                  DeleteView,
                                  ListView,
                                  UpdateView)

from .blog_constants import INDEX_POSTS_LIMITER
from .forms import (CommentForm,
                    PostForm,
                    RegistrationForm,
                    ProfileUpdate)
from .models import Category, Post, User
from .mixins import AuthMixin, PostMixin, CommentMixin, FilterMixin


class RegistrationCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('blog:index')


class ProfileListView(FilterMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = INDEX_POSTS_LIMITER

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        author = self.kwargs['username']
        qs = self.select_annotate(Post.objects).filter(
            author__username=author
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    form_class = ProfileUpdate

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class IndexListView(FilterMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    ordering = '-pub_date'
    paginate_by = INDEX_POSTS_LIMITER

    def get_queryset(self):
        qs = self.select_annotate(Post.objects).filter(
            pub_date__lte=now(),
            is_published=True,
            category__is_published=True
        )
        return qs


class PostDetailView(FilterMixin, ListView):
    model = Post
    template_name = 'blog/detail.html'
    paginate_by = INDEX_POSTS_LIMITER

    def get_object(self):
        post = get_object_or_404(
            Post.objects.select_related(
                'author',
                'location',
                'category'
            ),
            pk=self.kwargs['pk'])
        if (self.request.user != post.author
            and (post.pub_date > now()
                 or not post.is_published
                 or not post.category.is_published)):
            raise Http404
        return post

    def get_queryset(self):
        return self.get_object().comments.select_related(
            'author'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post'] = self.get_object()
        return context


class CategoryListView(FilterMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post'
    paginate_by = INDEX_POSTS_LIMITER

    def get_object(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return category

    def get_queryset(self):
        qs = self.select_annotate(self.get_object().posts).filter(
            pub_date__lte=now(),
            is_published=True,
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(PostMixin, UpdateView):
    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['post_id']})


class PostDeleteView(PostMixin, DeleteView):
    pass


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, AuthMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, AuthMixin, DeleteView):
    pass
