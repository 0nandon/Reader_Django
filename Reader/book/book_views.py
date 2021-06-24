from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from Reader.context_base import add_base_info
from django.views.generic import TemplateView, View
from book.models import Book, Review
from .room_views import return_category
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator

from recommendation.embedding import related_books
from firebase.models import Room
from firebase.firebase import db
import datetime
import time
import random


class BookList(TemplateView):
    template_name = 'book/book_book.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['categories'] = return_category()
        context['slug_main'] = self.kwargs['slug_main']
        context['slug_sub'] = self.kwargs['slug_sub']

        context['books'] = Book.objects.filter(category__slug=context['slug_sub']).order_by('create_dt')
        context['page'] = 1

        if len(context['books']) <= 10:
            context['is_page'] = False
        else:
            context['is_page'] = True
            if len(context['books']) < 200:
                div = 10
            else:
                div = 50
            p = Paginator(context['books'], div)
            page = p.page(self.kwargs['page'])
            context['books'] = page.object_list
            context['page_obj'] = p
            context['present_page_obj'] = page
            context['present_page'] = page.number

        context['book_modals'] = context['books']
        next_url = reverse_lazy('book:room_list', args=(context['slug_main'], context['slug_sub'],))
        return add_base_info(context, next_url)


class WishBook(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        book = get_object_or_404(Book, key=pk)
        if book in self.request.user.book_set.all():
            self.request.user.book_set.remove(book)
            return render(request, 'book/uncheck_wish_book.html', {'pk': pk})
        else:
            self.request.user.book_set.add(book)
            return render(request, 'book/check_wish_book.html', {'pk': pk})


class BookSingle(TemplateView):
    template_name = "book/book_single.html"

    def get_context_data(self, **kwargs):
        context = {}
        context['book'] = get_object_or_404(Book, slug=self.kwargs['slug_item'])

        if context['book'].category.slug == '추천_영문도서_':
            context['is_related'] = True
            related = related_books(context['book'].key)
            related_books_list = [iid for iid, _ in related]
            context['related_books'] = [get_object_or_404(Book, key=iid) for iid in related_books_list]
            print(context['related_books'])
        else:
            context['is_related'] = False

        today = datetime.date.today()
        today_str = str(today.year) + "-" + "0" + str(today.month) + "-" + str(today.day)
        context['today'] = today_str

        next_url = context['book'].get_absolute_url()
        return add_base_info(context, next_url)


class MakeRoom(View):
    def post(self, request, *args, **kwargs):
        subject = request.POST['subject']
        explain = request.POST['explain']
        tag = request.POST['tag']
        member = request.POST['member']
        duedate = request.POST['duedate']
        deaddate = request.POST['deaddate']

        category = self.kwargs['slug_sub']
        pk = self.kwargs['pk']
        book = get_object_or_404(Book, id=pk)

        duedate = duedate.split("-")
        if duedate[1][0] == '0':
            duedate[1] = duedate[1][1]
        if duedate[2][0] == '0':
            duedate[2] = duedate[0][1]
        duedate = time.mktime((int(duedate[0]),int(duedate[1]),int(duedate[2]),0,0,0,0,0,0))

        deaddate = deaddate.split("-")
        if deaddate[1][0] == '0':
            deaddate[1] = deaddate[1][1]
        if deaddate[2][0] == '0':
            deaddate[2] = deaddate[0][1]
        deaddate = time.mktime((int(deaddate[0]),int(deaddate[1]),int(deaddate[2]),0,0,0,0,0,0))

        tag_list = tag.split(',')

        room = Room(pk=random.randrange(1, 100000000),
                   subject=str(subject),
                   explain=str(explain),
                   category=category,
                   image=book.image.url,
                   deadline=deaddate,
                   duedate=duedate,
                   create=time.time(),
                   book=int(pk),
                   leader=self.request.user.email,
                   user=[self.request.user.email,],
                   page=[0,],
                   tags = tag_list,
                   full=int(member))
        db.collection(category).document().set(room.to_dict())
        db.collection('all').document().set(room.to_dict())

        return HttpResponseRedirect()


class BookReview(View):
    def post(self, request, *args, **kwargs):
        rating = request.POST['rating']
        subject = request.POST['subject']
        explain = request.POST['explain']

        rating = float(rating[:-2]) / 24.0

        book = get_object_or_404(Book, slug=self.kwargs['slug_item'])
        book.review_set.create(subject=subject, explain=explain, score=rating, owner=request.user)

        review_num = book.review_set.count()
        score = float((book.score * (review_num-1) + rating) / review_num)
        score = round(score, 2)
        book.score = score
        book.save()

        return HttpResponseRedirect()


class UpdateReview(View):
    def post(self, request, *args, **kwargs):
        rating = request.POST['rating']
        subject = request.POST['subject']
        explain = request.POST['explain']
        pk = int(request.POST['pk'])

        rating = float(rating[:-2]) / 24.0

        review = get_object_or_404(Review, pk=pk)
        review.subject = subject
        review.explain = explain
        review.score = rating
        review.save()

        return HttpResponseRedirect()


def DeleteReview(request, pk):
    review = Review.objects.get(id=pk)
    book = Book.objects.get(review = review)
    review_num = book.review_set.count()

    if review_num == 1:
        score = 0
    else:
        score = float((book.score * review_num - review.score) / (review_num-1))
        score = round(score, 2)
    book.score = score
    book.save()
    review.delete()
    return HttpResponseRedirect()
