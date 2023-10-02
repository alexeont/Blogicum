from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth import get_user_model

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                            attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class RegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name')


class ProfileUpdate(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name')
        field_classes = {'username': UsernameField}
