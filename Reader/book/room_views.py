from django.shortcuts import render
from django.views.generic import ListView, TemplateView, View
from .models import MainCategory
from django.urls import reverse_lazy
from Reader.context_base import add_base_info
from django.http import HttpResponseRedirect
from django.core.cache import cache


from firebase.models import Room, Comments
from firebase.firebase import db
import datetime
import time
import random


# 캐시에서 카테고리 목록 가져오기
def return_category():
    cache_key = 'category'
    shop = cache.get(cache_key, None)
    if not shop:
        shop = MainCategory.objects.all()
        cache.set(cache_key, shop, 60 * 60)
    return shop


# Create your views here.
class BookView(ListView):
    model = MainCategory
    context_object_name = 'categories'
    template_name = 'book/book.html'

    def get_queryset(self):
        return return_category()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = reverse_lazy('book:book')
        return add_base_info(context, next_url)


class RoomList(TemplateView):
    template_name = 'book/book_room.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['categories'] = return_category()
        context['slug_main'] = self.kwargs['slug_main']
        context['slug_sub'] = self.kwargs['slug_sub']
        context['page'] = 1

        if 'pk' in self.kwargs.keys():
            time.sleep(0.4)

        # firestore query
        from firebase_admin import firestore
        rooms = db.collection(context['slug_sub']).order_by(u'create', direction=firestore.Query.DESCENDING).stream()
        context['rooms'] = []
        for room in rooms:
            context['rooms'].append(Room.from_dict(room.to_dict()))

            today = datetime.date.today()
            target = context['rooms'][-1].duedate
            local = time.localtime(target)
            target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
            context['rooms'][-1].d_day = (target-today).days

        context['room_modals'] = context['rooms']
        next_url = reverse_lazy('book:room_list', args=(context['slug_main'], context['slug_sub'],))
        return add_base_info(context, next_url)


class RoomSort(View):
    def get(self, request, *args, **kwargs):
        pk = int(request.GET['pk'])

        # firestore query
        from firebase_admin import firestore
        rooms = db.collection(self.kwargs['slug_sub']).order_by(u'create', direction=firestore.Query.DESCENDING).stream()
        context = {}
        context['rooms'] = []
        context['slug_sub'] = self.kwargs['slug_sub']
        if pk == 0:
            for room in rooms:
                context['rooms'].append(Room.from_dict(room.to_dict()))

                today = datetime.date.today()
                target = context['rooms'][-1].duedate
                local = time.localtime(target)
                target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
                context['rooms'][-1].d_day = (target-today).days
        elif pk == 1:
            for room in rooms:
                room_obj = Room.from_dict(room.to_dict())

                today = datetime.date.today()
                target = room_obj.duedate
                local = time.localtime(target)
                target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
                room_obj.d_day = (target-today).days

                if room_obj.d_day >= 0 and len(room_obj.user) < room_obj.full:
                    context['rooms'].append(room_obj)
        elif pk == 2:
            for room in rooms:
                room_obj = Room.from_dict(room.to_dict())

                today = datetime.date.today()
                target = room_obj.duedate
                local = time.localtime(target)
                target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
                room_obj.d_day = (target-today).days

                if room_obj.d_day >= 0 and room_obj.d_day <= 10 and len(room_obj.user) < room_obj.full:
                    context['rooms'].append(room_obj)
        elif pk == 3:
            for room in rooms:
                room_obj = Room.from_dict(room.to_dict())

                today = datetime.date.today()
                target = room_obj.duedate
                local = time.localtime(target)
                target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
                room_obj.d_day = (target-today).days

                if room_obj.d_day < 0 or len(room_obj.user) >= room_obj.full:
                    context['rooms'].append(room_obj)

        return render(request, 'book/room_sort.html', context)


class WishRoom(View):
    def get(self, request, *args, **kwargs):
        pk = int(self.kwargs['pk'])
        slug = self.kwargs['slug_sub']
        rooms = db.collection(slug).where(u'pk', u'==', pk).stream()

        for room_doc in rooms:
            room = Room.from_dict(room_doc.to_dict())

            if self.request.user.email in room.wish:
                room.wish.remove(self.request.user.email)
                room_query = db.collection(slug).document(room_doc.id)
                room_query.update({u'wish': room.wish})
                return render(request, 'book/uncheck_wish.html', {})
            else:
                room.wish.append(self.request.user.email)
                room_query = db.collection(slug).document(room_doc.id)
                room_query.update({u'wish': room.wish})
                return render(request, 'book/check_wish.html', {})


class RoomIn(View):
    def get(self, request, *args, **kwargs):
        pk = int(self.kwargs['pk'])
        slug = self.kwargs['slug_sub']
        rooms = db.collection(slug).where(u'pk', u'==', pk).stream()
        url = None

        for room_doc in rooms:
            room = Room.from_dict(room_doc.to_dict())

            # 이미 방에 합류가 돼있을 경우
            url = room
            if 'in' in self.kwargs.keys() and self.request.user.email in url.user:
                return HttpResponseRedirect(url.get_absolute_url())

            room_query = db.collection(slug).document(room_doc.id)
            room.user.append(self.request.user.email)
            room.page.append(0)
            room_query.update({u'user': room.user})
            room_query.update({u'page': room.page})

        rooms = db.collection('all').where(u'pk', u'==', pk).stream()
        for room_doc in rooms:
            room = Room.from_dict(room_doc.to_dict())

            room_query = db.collection('all').document(room_doc.id)
            room.user.append(self.request.user.email)
            room.page.append(0)
            room_query.update({u'user': room.user})
            room_query.update({u'page': room.page})

        if 'in' in self.kwargs.keys():
            return HttpResponseRedirect(url.get_absolute_url())
        return render(request, 'book/room_inside.html', {})


class RoomSingle(TemplateView):
    template_name = 'book/room_single.html'

    def get_context_data(self, **kwargs):
        context = {}
        pk = int(self.kwargs['pk'])
        slug = self.kwargs['slug_sub']
        context['slug'] = slug

        time.sleep(0.2)  # firestore data 수정 시간 지연 고려
        rooms = db.collection(slug).where(u'pk', u'==', pk).stream()
        for room in rooms:
            context['room'] = Room.from_dict(room.to_dict())

            comments = db.collection(room.id).order_by(u'create').stream()
            context['comments_num'] = 0

            # 목표일까지 남은 기간 계산
            today = datetime.date.today()
            target = context['room'].deadline
            local = time.localtime(target)
            target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
            context['room'].d_day = (target-today).days

            # 목표 진행률 계산
            days = context['room'].create
            local = time.localtime(days)
            days = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
            present = (today-days).days
            entire = (target-days).days
            context['deadline'] = int((present / entire) * 100)
            context['deadline'] = str(context['deadline']) + '%'

            # 대화 목록 업로드
            context['comments'] = []
            context['doc_id'] = room.id
            for comment in comments:
                comment_obj = Comments.from_dict(comment.to_dict())
                context['comments'].append(comment_obj)
                context['comments'][-1].doc_id = comment.id
                context['comments_num'] += 1
                context['comments_num'] += len(context['comments'][-1].get_sub())

                local = time.localtime(context['comments'][-1].create)
                context['comments'][-1].create = str(local.tm_year) + '년, ' + str(local.tm_mon) + '월 ' + str(local.tm_mday) + '일'

            # 진행률 목록 업로드
            context['page'], context['progress'] = context['room'].user_progress(self.request.user.email)
            idx = 0
            for i, progress in enumerate(context['progress']):
                if progress.user.email == self.request.user.email:
                    idx = i
                    context['percentage'] = progress.percentage
                    break
            del context['progress'][idx]  # 로그인 된 해당 사용자는 목록에서 제거

        return context


class AddRoomComment(View):
    def post(self, request, *args, **kwargs):
        contents = request.POST['contents']
        doc_id = kwargs['doc_id']

        comment = Comments(pk=random.randrange(1, 100000000), contents=contents, user=request.user.email, create=time.time())
        db.collection(doc_id).document().set(comment.to_dict())
        return HttpResponseRedirect()


class DeleteComment(View):
    def get(self, request, *args, **kwargs):
        col_id = kwargs['col_id']
        doc_id = kwargs['doc_id']
        db.collection(col_id).document(doc_id).delete()


class UpdateComment(View):
    def post(self, request, *args, **kwargs):
        col_id = kwargs['col_id']
        doc_id = kwargs['doc_id']
        contents = request.POST['contents']
        query = db.collection(col_id).document(doc_id)
        query.update({u'contents': contents})


class UpdateProgress(View):
    def post(self, request, *args, **kwargs):
        slug = kwargs['slug_sub']
        doc_id = kwargs['doc_id']
        page = int(request.POST['page'])

        query = db.collection(slug).document(doc_id)
        room = query.get()
        room = Room.from_dict(room.to_dict())

        for idx, user in enumerate(room.user):
            if user == self.request.user.email:
                room.page[idx] = page
                break
        query.update({u'page': room.page})
