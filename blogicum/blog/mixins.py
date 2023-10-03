from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import CommentForm, PostForm
from .models import Post, Comment


class AuthMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author


class PostMixin(AuthMixin, LoginRequiredMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.get_object())
        return context


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['post_id']})


class FilterMixin:
    @staticmethod
    def select_annotate(objects):
        return (
            objects.select_related(
                'author',
                'location',
                'category'
            )
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
