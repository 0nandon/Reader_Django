
from django.urls import path, re_path
from .views import SignIn, SignUp
from django.contrib.auth.views import LogoutView


app_name = 'account'
urlpatterns = [
    path('login/', SignIn.as_view(), name='login'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='signout'),
]