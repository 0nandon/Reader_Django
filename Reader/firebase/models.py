from .firebase import db
from book.models import Book, SubCategory
from login.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
import time
import numpy as np

from firebase.firebase import db


class UserProgress:
    def __init__(self, user, progress):
        self.user = user
        self.percentage = progress


# firebase model
class Room(object):
    def __init__(self, pk, subject, explain, category, image, leader, deadline=0.0,
                 duedate=0.0, create=0, book=0, user=[], page=[], tags=[], wish=[], full=0):
        self.pk = pk
        self.subject = subject
        self.explain = explain
        self.category = category
        self.image = image
        self.leader = leader  # 방 리더
        self.deadline = deadline
        self.duedate = duedate  # 인원 모집 마감 기한
        self.create = create  # 생성 시간
        self.book = book  # 책
        self.user = user
        self.page = page
        self.tags = tags
        self.wish = wish
        self.full = full

        self.d_day = None
        self.d_dead = None

    @staticmethod
    def from_dict(source):
        # [START_EXCLUDE]
        room = Room(source[u'pk'], source[u'subject'], source[u'explain'], source[u'category'], source[u'image'], source[u'leader'])

        if u'deadline' in source:
            room.deadline = source[u'deadline']
        if u'duedate' in source:
            room.duedate = source[u'duedate']
        if u'create' in source:
            room.create = source[u'create']
        if u'book' in source:
            room.book = source[u'book']
        if u'user' in source:
            room.user = source[u'user']
        if u'page' in source:
            room.page = source[u'page']
        if u'tags' in source:
            room.tags = source[u'tags']
        if u'wish' in source:
            room.wish = source[u'wish']
        if u'full' in source:
            room.full = source[u'full']

        return room

    def to_dict(self):
        # [START_EXCLUDE]
        dest = {
            u'pk': self.pk,
            u'subject': self.subject,
            u'explain': self.explain,
            u'category': self.category,
            u'image': self.image,
            u'leader': self.leader
        }

        if self.deadline:
            dest[u'deadline'] = self.deadline
        if self.duedate:
            dest[u'duedate'] = self.duedate
        if self.create:
            dest[u'create'] = self.create
        if self.book:
            dest[u'book'] = self.book
        if self.user:
            dest[u'user'] = self.user
        if self.page:
            dest[u'page'] = self.page
        if self.tags:
            dest[u'tags'] = self.tags
        if self.wish:
            dest[u'wish'] = self.wish
        if self.full:
            dest[u'full'] = self.full

        return dest

    def user_progress(self, user):
        pair = []
        idx = np.argsort(self.page)

        page = 0
        for i in idx[::-1]:
            if self.user[i] == user:
                page = self.page[i]
            book = get_object_or_404(Book, id=self.book)
            percentage = int((self.page[i] / book.page) * 100)
            percentage = str(percentage) + '%'
            user_obj = get_object_or_404(User, email=self.user[i])
            u = UserProgress(user=user_obj, progress=percentage)
            pair.append(u)
        return page, pair

    def get_absolute_url(self):
        sub = get_object_or_404(SubCategory, slug=self.category)
        return reverse_lazy('book:room_single', args=(sub.main.slug, self.category, self.pk,))

    def get_book_title(self):
        book = get_object_or_404(Book, id=self.book)
        return book.name

    def get_user_num(self):
        rooms = db.collection(self.category).where(u'pk', u'==', self.pk).stream()

        for room in rooms:
            room_obj = Room.from_dict(room.to_dict())
            return len(room_obj.user)

    def __repr__(self):
        return(
            u'Room(pk={}, subject={}, explain={}, category={}, image={}, leader={}, duedate={}, create={}, book={}, \
            user={}, page={}, tags={}, wish={}, full={})'
            .format(self.pk, self.subject, self.explain, self.category, self.duedate, self.create, self.book,
                    self.leader, self.user, self.page, self.tags, self.wish, self.full))


class Comments(object):
    def __init__(self, pk, contents, user, create=0.0):
        self.pk = pk
        self.contents = contents
        self.user = user
        self.create = create

        self.doc_id = None

    @staticmethod
    def from_dict(source):
        # [START_EXCLUDE]
        comment = Comments(source[u'pk'], source[u'contents'], source[u'user'])

        if u'create' in source:
            comment.create = source[u'create']

        return comment

    def to_dict(self):
        # [START_EXCLUDE]
        dest = {
            u'pk': self.pk,
            u'contents': self.contents,
            u'user': self.user,
        }

        if self.create:
            dest[u'create'] = self.create

        return dest

    def get_sub(self):
        sub_collections = db.collection(self.doc_id).order_by(u'create').stream()
        context = []
        for sub in sub_collections:
            context.append(Comments.from_dict(sub.to_dict()))

            local = time.localtime(context[-1].create)
            context[-1].create = str(local.tm_year) + '년, ' + str(local.tm_mon) + '월 ' + str(local.tm_mday) + '일'
            context[-1].doc_id = sub.id

        return context

    def get_user(self):
        return get_object_or_404(User, email=self.user)

    def __repr__(self):
        return(
            u'Room(pk={}, contents={}, user={}, create={})'
            .format(self.pk, self.contents, self.user, self.create))
