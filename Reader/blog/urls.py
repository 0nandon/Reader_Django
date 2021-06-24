
from django.urls import path, re_path
from .views import PostList, PostSingle, AddComment, Sub, Update, Delete, SubUpdate, SubDelete, PostDelete, PostUpdate, PostSearch


app_name = 'blog'
urlpatterns = [
    path(r'sub/update/<int:pk>/', SubUpdate.as_view(), name='sub_update'),
    path(r'sub/delete/<int:pk>/', SubDelete, name='sub_delete'),
    path(r'update/<int:pk>/', Update.as_view(), name='comment_update'),
    path(r'delete/<int:pk>/', Delete, name='comment_delete'),
    path(r'sub/<int:pk>/', Sub.as_view(), name='sub'),
    path(r'comment/<int:pk>/', AddComment.as_view(), name='comment'),
    path(r'post/delete/<int:pk>/', PostDelete, name='post_delete'),
    path(r'post/update/<int:pk>/', PostUpdate.as_view(), name='post_update'),
    path(r'single/post/<int:pk>/', PostSingle.as_view(), name='single'),
    path(r'search/', PostSearch, name='search'),
    re_path(r'(?P<slug>[-\w]+)/(?P<page>\d+)/$', PostList.as_view(), name='blog_page'),
    re_path(r'(?P<slug>[-\w]+)/$', PostList.as_view(), name='blog'),
]