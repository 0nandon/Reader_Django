
from django.urls import path, re_path
from .room_views import BookView, RoomList, WishRoom, RoomIn, RoomSingle, AddRoomComment, DeleteComment, UpdateComment, UpdateProgress, RoomSort
from .book_views import BookList, WishBook, BookSingle, BookReview, DeleteReview, UpdateReview, MakeRoom


app_name = 'book'
urlpatterns = [
    re_path(r'room/update/progress/(?P<slug_sub>[-\w]+)/(?P<doc_id>[-\w]+)/$', UpdateProgress.as_view(), name='update_progress'),
    re_path(r'room/inside/(?P<slug_sub>[-\w]+)/(?P<pk>\d+)/(?P<in>\d+)/$', RoomIn.as_view(), name='room_modal_in'),
    re_path(r'room/inside/(?P<slug_sub>[-\w]+)/(?P<pk>\d+)/$', RoomIn.as_view(), name='room_in'),
    re_path(r'update/(?P<col_id>[-\w]+)/(?P<doc_id>[-\w]+)/$', UpdateComment.as_view(), name='comment_update'),
    re_path(r'delete/(?P<col_id>[-\w]+)/(?P<doc_id>[-\w]+)/$', DeleteComment.as_view(), name='comment_delete'),
    re_path(r'room/(?P<doc_id>[-\w]+)/$', AddRoomComment.as_view(), name='room_add_comment'),
    re_path(r'room/(?P<slug_main>[-\w]+)/(?P<slug_sub>[-\w]+)/(?P<pk>\d+)/$', RoomSingle.as_view(), name='room_single'),
    re_path(r'room/(?P<slug_sub>[-\w]+)/(?P<pk>\d+)/$', WishRoom.as_view(), name='wish_room'),
    re_path(r'sort/(?P<slug_sub>[-\w]+)/$', RoomSort.as_view(), name='room_sort'),
    re_path(r'room/(?P<slug_main>[-\w]+)/(?P<slug_sub>[-\w]+)/$', RoomList.as_view(), name='room_list'),
    re_path(r'make/(?P<slug_main>[-\w]+)/(?P<slug_sub>[-\w]+)/(?P<pk>\d+)/$', RoomList.as_view(), name='room_list_'),
    path('', BookView.as_view(), name='book'),
] + [
    re_path(r'make/(?P<slug_sub>[-\w]+)/(?P<pk>\d+)/$', MakeRoom.as_view(), name='make_room'),
    path('delete/<int:pk>/', DeleteReview, name='delete'),
    re_path(r'update/$', UpdateReview.as_view(), name='update'),
    re_path(r'single/(?P<slug_item>[-\w]+)/$', BookSingle.as_view(), name='book_single'),
    re_path(r'review/(?P<slug_item>[-\w]+)/$', BookReview.as_view(), name='book_review'),
    path('wish/<int:pk>/', WishBook.as_view(), name='book_wish'),
    re_path(r'(?P<slug_main>[-\w]+)/(?P<slug_sub>[-\w]+)/(?P<page>\d+)/$', BookList.as_view(), name='book_list'),
]