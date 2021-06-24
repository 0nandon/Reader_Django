from django.shortcuts import render, get_object_or_404
from django.views.generic import UpdateView, ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from book.models import Book
from login.models import User

from firebase.models import Room
from firebase.firebase import db
import os
import datetime
import time


# Create your views here.
class Profile(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['name', 'sosok', 'image']
    template_name = 'myprofile/profile.html'
    success_url = reverse_lazy('profile:profile')
    image_url = None
    image_path = None
    image_thumb_path = None

    def form_valid(self, form):
        if self.image_url and form.instance.image.url != self.image_url:
            os.remove(self.image_path)
            os.remove(self.image_thumb_path)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = '총류'
        return context

    def get_object(self):
        if self.request.user.image:
            self.image_url = self.request.user.image.url
            self.image_path = self.request.user.image.path
            self.image_thumb_path = self.request.user.image.thumb_path
        return self.request.user


class WishList(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'myprofile/wishlist.html'
    context_object_name = 'books'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = '총류'
        return context

    def get_queryset(self):
        return Book.objects.filter(wish=self.request.user)


class RoomList(LoginRequiredMixin, TemplateView):
    template_name = 'myprofile/room.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['slug'] = '총류'

        context['rooms'] = []
        from firebase_admin import firestore
        rooms = db.collection(u'all').order_by(u'create', direction=firestore.Query.DESCENDING).stream()

        for room in rooms:
            room_obj = Room.from_dict(room.to_dict())
            if self.request.user.email in room_obj.user:
                context['rooms'].append(room_obj)
                today = datetime.date.today()
                target = context['rooms'][-1].duedate
                local = time.localtime(target)
                target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
                context['rooms'][-1].d_day = (target-today).days

                target = context['rooms'][-1].deadline
                local = time.localtime(target)
                target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
                context['rooms'][-1].d_dead = (target-today).days
        return context


class WishDelete(View):
    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, id=self.kwargs['pk'])
        self.request.user.book_set.remove(book)

        context = {}
        context['books'] = Book.objects.filter(wish=self.request.user)
        return render(request, 'myprofile/delete.html', context)


