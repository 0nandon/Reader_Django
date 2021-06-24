
from django.urls import path, re_path
from .views import AboutChatbot
# ChatBot, RequestChat, fit

app_name = 'chatbot'
urlpatterns = [
    # path('', ChatBot.as_view(), name='run'),
    # path('fit/', fit, name='fit'),
    path('about/', AboutChatbot.as_view(), name='about'),
    # path('<slug:url_pattern>/<str:uid>/<str:text>/', RequestChat.as_view(), name='chatbot'),
]