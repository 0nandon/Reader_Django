
from django.contrib.auth import views as auth_view
from django.contrib import auth
from login.forms import CustomAuthenticationForm, CustomUserCreationForm
from django.urls import reverse_lazy
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Q

from .context_base import add_base_info
from recommendation.mf_model import recommend
from firebase.models import Room
from firebase.firebase import db
from blog.models import Post

from book.models import Book, SubCategory
from django.shortcuts import get_object_or_404
import datetime
import time

import pandas as pd
from pandas import DataFrame, Series
import numpy as np


def get_page(page):
    for check in [' p', ' P', 'P', 'p.', 'p', ' p.', ' P.', ' cm', '.', '`', ';']:
        if isinstance(page, str):
            page = page.replace(check, '')
    return page


def store_book(gookbang_books, idx, code, num):
    page = get_page(gookbang_books.loc[idx]['페이지'])
    if page == "" or '-' in gookbang_books.loc[idx]['발행년도']:
        return
    if "." in gookbang_books.loc[idx]['발행년도']:
        return
    b = Book(
        key=idx,
        name=gookbang_books.loc[idx]['제목'],
        slug=str(idx) + "_" + str(num),
        explain="이곳에는 책에 대한 설명을 보여줍니다. 책에 대한 줄거리, 서평, 평판 등을 간략히 3~4줄로 요약하여 나타냅니다. 예를 들어, 쉘 실버스타인의 책 '아낌없이 주는 나무'에 대한 설명을 적는다고 한다면, '1964년에 출판된 『아낌없이 주는 나무』는 더 이상 설명이 필요 없는 그 대표적인 작품으로, 출판된 지 50년이 넘은 지금까지도 독자들의 꾸준한 사랑을 받고 있다.' 라고 할 수 있을 것입니다.",
        page=int(page),
        code=float(code),
        author=gookbang_books.loc[idx]['저작자'],
        publication=gookbang_books.loc[idx]['발행자'],
        publication_date=gookbang_books.loc[idx]['발행년도'],
        image="/book/2021/06/default.png"
    )
    b.save()

    b = get_object_or_404(Book, key=idx)
    b.tag.add("태그1", "태그2", "태그3")

    c = get_object_or_404(SubCategory, code=code)
    c.book_set.add(b)


class HomeView(auth_view.LoginView):
    template_name = 'home.html'
    form_class = CustomAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = '총류'
        context['next'] = reverse_lazy('home')
        context['form_signup'] = CustomUserCreationForm

        # 영문 추천 도서
        if self.request.user.is_active:
            context['recommend_books'] = recommend(self.request.user.id)
        else:
            context['recommend_books'] = None

        # 최근 게시물 3개
        context['posts'] = Post.objects.all()[:3]

        # 최신 독서방
        from firebase_admin import firestore
        rooms = db.collection('all').order_by(u'create', direction=firestore.Query.DESCENDING).stream()

        context['rooms'] = []
        cnt = 0
        for room in rooms:

            if cnt == 3:
                break

            room_obj = Room.from_dict(room.to_dict())

            today = datetime.date.today()
            target = room_obj.duedate
            local = time.localtime(target)
            target = datetime.date(local.tm_year, local.tm_mon, local.tm_mday)
            room_obj.d_day = (target-today).days

            if room_obj.d_day < 0 or room_obj.full == room_obj.get_user_num():
                continue

            context['rooms'].append(room_obj)
            cnt += 1

        context['room_modals'] = context['rooms']

        """
        from firebase_admin import firestore
        rooms = db.collection(u'all').order_by(u'create', direction=firestore.Query.DESCENDING).stream()
        for room in rooms[:3]:
            room_obj = Room.from_dict(room.to_dict())
        """

        """
        # 국방데이터를 활용하여 책 데이터를 넣는 코드
        # 1. 데이터 항목이 NaN인 경우 제거
        # 2. 페이지 정보, KDC 분류 번호 데이터 전처리 진행

        gookbang_books = pd.read_csv('/workspace/Reader/recommendation/data/gookbang_library.csv', sep=',', encoding='utf-8')
        gookbang_books = gookbang_books.set_index('도서 KEY')

        cols = ['페이지', '제목', '저작자', '발행자', '발행년도', 'KDC 분류 번호']

        for col in cols:
            drop_idx = gookbang_books[gookbang_books[col].isnull()].index
            gookbang_books = gookbang_books.drop(drop_idx)

        pages = gookbang_books['페이지']
        idxs = np.array(gookbang_books.index)

        new_idxs = []
        for idx, page in zip(idxs, pages):
            is_continue = False
            for check in ['+', '?', '책', 'PM', 'M', ',', '-', '권', 'W', '월', 'V', 'v', '~', '간', ']', '[', '장', 'tae']:
                if check in page:
                    is_continue = True
                    break
            if is_continue:
                continue

            if page in ['', '가제', '3면', '면수복잡', 'xiii', '복잡', '2冊', '퓨터', '벽지도 1매', '알수없음']:
                continue

            new_idxs.append(idx)

        idxs = np.array(new_idxs)
        # codes = gookbang_books.loc[idxs]['KDC 분류 번호']

        count = {}
        num = 0
        for idx in idxs:
            code = gookbang_books.loc[idx]['KDC 분류 번호']
            if isinstance(code, Series):
                continue

            if isinstance(code, str):
                code = code.replace(' ', '')
            if isinstance(code, str):
                code = code.replace(',', '.')
            if isinstance(code, str):
                code = code.replace('..', '.')
            if isinstance(code, str):
                code = code.replace('`', '')
            if isinstance(code, str):
                code = code.replace('r', '')
            if isinstance(code, str):
                code = code.replace('.-', '.')
            if isinstance(code, str):
                code = code.replace('l', '1')
            if isinstance(code, str):
                code = code.replace('.76', '')
            if isinstance(code, str):
                code = code.replace('.008', '')
            if isinstance(code, str) and code == 'B39':
                continue

            code = int(float(code) / 10) * 10
            if code > 990:
                continue
            if code % 100 == 0:
                continue

            num += 1
            if code in count.keys() and num >= 8230:
                if count[code] < 1000:
                    count[code] += 1
                    print(num, idx)
                    store_book(gookbang_books, idx, code, num)
            elif num >= 8230:
                count[code] = 1
                print(num, idx)
                store_book(gookbang_books, idx, code, num)
        """

        return context


# 도서 검색
def HomeSearch(request):
    search = request.POST['home_search']

    books = Book.objects.filter(Q(name__icontains=search) |
                                Q(explain__icontains=search) |
                                Q(tag__name__in=[search]) |
                                Q(category__name__icontains=search)).distinct()
    context = {}
    context['books'] = books
    context['book_modals'] = context['books']
    next_url = reverse_lazy('search')
    return render(request, 'search.html', add_base_info(context, next_url))


class CreateUserModalView(View):
    form_class = CustomUserCreationForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()
            auth.login(request, user)  # 회원 가입 되자마자 로그인
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            return render(request, 'home.html', { 'form': CustomAuthenticationForm,
                                                'form_signup': form, 'slug': '총류' })

