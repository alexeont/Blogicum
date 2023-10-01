from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  )


class ProfileUpdate(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  )
        field_classes = {'username': UsernameField}
