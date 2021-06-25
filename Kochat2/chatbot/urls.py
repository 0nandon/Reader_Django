
from django.urls import path, re_path
from .views import fit, RequestChat, ChatBot
from .krawl import krawl


app_name = 'kochat'
urlpatterns = [
    path('', ChatBot.as_view(), name='run'),
    path('fit/', fit, name='fit'),
    path('fit/<slug:url_pattern>/<str:uid>/<str:text>/', RequestChat.as_view(), name='chatbot'),
    path('krawl/', krawl, name='krawl'),
]
