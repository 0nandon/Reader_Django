from django.contrib import admin
from .models import Post, Comment, SubComment


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tag')
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id',)


@admin.register(SubComment)
class SubCommentAdmin(admin.ModelAdmin):
    list_display = ('id',)