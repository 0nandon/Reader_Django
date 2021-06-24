"""Reader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import HomeView, HomeSearch, CreateUserModalView
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('book/', include('book.urls')),
    path('account/', include('login.urls')),
    path('blog/', include('blog.urls')),
    path('chatbot/', include('chatbot.urls')),
    # path('model/', include('recommendation.urls')),
    path('profile/', include('myprofile.urls')),
    path('', HomeView.as_view(), name='home'),
    path('signup/', CreateUserModalView.as_view(), name='signup'),
    path('search/', HomeSearch, name='search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
