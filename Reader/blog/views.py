from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView, View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Comment, SubComment
from book.models import MainCategory

from book.room_views import return_category
from Reader.context_base import add_base_info
import os


# Create your views here.
class PostList(CreateView):
    model = Post
    context_object_name = 'form_post'
    fields = ['subject', 'explain', 'image', 'tag']
    template_name = 'blog/blog_list.html'
    success_url = None

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.category = get_object_or_404(MainCategory, slug=self.kwargs['slug'])
        self.success_url = reverse_lazy('blog:blog', args=(self.kwargs['slug'],))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_post'] = context['form']
        del context['form']

        context['categories'] = return_category()
        context['posts'] = Post.objects.filter(category__slug=self.kwargs['slug'])
        context['category_now'] = self.kwargs['slug']
        context['recents'] = Post.objects.all()[:3]

        p = Paginator(context['posts'], 5)
        if 'page' in self.kwargs.keys():
            page = p.page(self.kwargs['page'])
        else:
            page = p.page(1)
        context['posts'] = page.object_list
        context['page_obj'] = p
        context['present_page_obj'] = page
        context['present_page'] = page.number

        next_url = reverse_lazy('blog:blog', args=('총류',))
        return add_base_info(context, next_url)


class PostSingle(DetailView):
    model = Post
    template_name = 'blog/blog_single.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments_num'] = self.get_object().get_comments_num()
        next_url = reverse_lazy('blog:single', args=(self.kwargs['pk'],))
        return add_base_info(context, next_url)


def PostSearch(request):
    search = request.POST['search']
    posts = Post.objects.filter(Q(subject__icontains=search) |
                                Q(explain__icontains=search) |
                                Q(tag__name__in=[search])).distinct()
    context = {}
    context['posts'] = posts
    next_url = reverse_lazy('blog:blog', args=('총류',))
    return render(request, 'blog/blog_search.html', add_base_info(context, next_url))


def PostDelete(request, pk):
    post = get_object_or_404(Post, id=pk)
    redirect_url = reverse_lazy('blog:blog', args=(post.category.slug,))

    os.remove(post.image.path)
    os.remove(post.image.thumb_path)
    post.delete()
    return HttpResponseRedirect(redirect_url)


class PostUpdate(View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        subject = request.POST['subject']
        explain = request.POST['explain']

        post.subject = subject
        post.explain = explain
        post.save()
        return HttpResponseRedirect()


class AddComment(View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        explain = request.POST['contents']
        post.comment_set.create(explain=explain, owner=request.user)
        return HttpResponseRedirect()


class Sub(View):
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=self.kwargs['pk'])
        explain = request.POST['contents']
        comment.subcomment_set.create(explain=explain, owner=request.user)
        return HttpResponseRedirect()


class Update(View):
    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=self.kwargs['pk'])
        explain = request.POST['contents']

        comment.explain = explain
        comment.save()
        return HttpResponseRedirect()


def Delete(request, pk):
    Comment.objects.get(id=pk).delete()
    return HttpResponseRedirect()


class SubUpdate(View):
    def post(self, request, *args, **kwargs):
        sub = get_object_or_404(SubComment, id=self.kwargs['pk'])
        explain = request.POST['contents']

        sub.explain = explain
        sub.save()
        return HttpResponseRedirect()


def SubDelete(request, pk):
    SubComment.objects.get(id=pk).delete()
    return HttpResponseRedirect()

