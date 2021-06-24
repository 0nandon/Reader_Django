

from login.forms import CustomAuthenticationForm, CustomUserCreationForm
from django.core.cache import cache
from django.urls import reverse_lazy


def add_base_info(context, next_url):
    context['next'] = next_url
    context['form_signup'] = CustomUserCreationForm
    context['form'] = CustomAuthenticationForm
    context['slug'] = '총류'
    return context