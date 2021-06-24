from django.contrib import admin
from .models import Book, MainCategory, SubCategory


# Register your models here.
@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'name', 'slug', 'score', 'code',)
    search_fields = ['name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tag')