from django.db import models
from taggit.managers import TaggableManager
from login.models import User
from login.fields import ThumbnailImageField
from book.models import MainCategory
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
# Create your models here.


class Post(models.Model):
    subject = models.TextField('SUBJECT', blank=True, null=True)
    explain = models.TextField('EXPLAIN')
    create_dt = models.DateTimeField('CREATE_DATE', auto_now_add=True)
    modify_dt = models.DateTimeField('MODIFY_DATE', auto_now=True)
    image = ThumbnailImageField(upload_to='blog/%Y/%m', blank=True, null=True)
    tag = TaggableManager(blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        ordering = ('-create_dt',)

    def get_comments_num(self):
        num = 0
        post = get_object_or_404(Post, id=self.id)
        comments = post.comment_set.all()
        for comment in comments:
            num += comment.subcomment_set.count() + 1

        return num

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse_lazy('blog:single', args=(self.id,))

    def get_previous(self):
        return self.get_previous_by_create_dt()

    def get_next(self):
        return self.get_next_by_create_dt()


class Comment(models.Model):
    explain = models.TextField('EXPLAIN')
    create_dt = models.DateTimeField('CREATE_DATE', auto_now_add=True)
    modify_dt = models.DateTimeField('MODIFY_DATE', auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'comments'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ('-create_dt',)


class SubComment(models.Model):
    explain = models.TextField('EXPLAIN')
    create_dt = models.DateTimeField('CREATE_DATE', auto_now_add=True)
    modify_dt = models.DateTimeField('MODIFY_DATE', auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'subs'
        verbose_name = 'sub'
        verbose_name_plural = 'subs'
        ordering = ('-create_dt',)


