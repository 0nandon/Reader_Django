from django.db import models
from taggit.managers import TaggableManager
from login.models import User
from django.urls import reverse_lazy


# Create your models here.
class MainCategory(models.Model):
    code = models.IntegerField(default=0, blank=True, null=True)
    name = models.CharField('NAME', max_length=100, blank=True)
    slug = models.SlugField('SLUG', unique=True, allow_unicode=True, blank=True, null=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    code = models.IntegerField(default=0, blank=True, null=True)
    name = models.CharField('NAME', max_length=100)
    slug = models.SlugField('SLUG', unique=True, allow_unicode=True, blank=True, null=True)
    main = models.ForeignKey(MainCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Book(models.Model):
    # find key
    key = models.IntegerField(default=0)
    name = models.CharField('NAME', max_length=100, blank=True)
    slug = models.SlugField('SLUG', unique=True, allow_unicode=True, blank=True, null=True)

    explain = models.TextField('EXPLAIN', blank=True)
    score = models.FloatField(default=0)
    page = models.IntegerField(default=0)
    code = models.FloatField(default=0)
    tag = TaggableManager(blank=True)

    author = models.CharField('AUTHOR', max_length=100, blank=True)
    publication = models.CharField('PUBLICATION', max_length=100, blank=True)
    publication_date = models.IntegerField(default=0)
    create_dt = models.DateTimeField('CREATE_DATE', auto_now_add=True)

    # 이미지 필드
    image = models.ImageField(upload_to='book/%Y/%m', blank=True, null=True)

    # 외래키 필드
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    wish = models.ManyToManyField(User, blank=True, null=True)

    class Meta:
        db_table = 'books'
        verbose_name = 'book'
        verbose_name_plural = 'books'
        ordering = ('-create_dt',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('book:book_single', args=(self.slug,))


class Review(models.Model):
    subject = models.TextField('SUBJECT', blank=True, null=True)
    explain = models.TextField('EXPLAIN')
    score = models.FloatField(default=0, blank=True)
    create_dt = models.DateTimeField('CREATE_DATE', auto_now_add=True)
    modify_dt = models.DateTimeField('MODIFY_DATE', auto_now=True)

    # 외래키
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'reviews'
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
        ordering = ('-create_dt',)
