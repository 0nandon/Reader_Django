
from django.urls import path
from .views import Profile, WishList, WishDelete, RoomList


app_name = 'profile'
urlpatterns = [
    path('', Profile.as_view(), name='profile'),
    path('wishlist/', WishList.as_view(), name='wishlist'),
    path('room/', RoomList.as_view(), name='room'),
    path('delete/<int:pk>/', WishDelete.as_view(), name='delete'),
]