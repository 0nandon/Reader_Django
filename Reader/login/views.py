
from django.contrib.auth import views as auth_view
from django.contrib import auth
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View
from django.http import HttpResponseRedirect
from .forms import CustomAuthenticationForm, CustomUserCreationForm
# Create your views here.


class SignIn(auth_view.LoginView):
    template_name = 'login/login.html'
    form_class = CustomAuthenticationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = reverse_lazy('home')
        context['form_signup'] = CustomUserCreationForm
        context['slug'] = '총류'
        return context


class SignUp(View):
    form_class = CustomUserCreationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, 'login/signup.html', { 'form': CustomAuthenticationForm,
                                                'form_signup': form, 'slug': '총류' })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()
            auth.login(request, user)  # 회원 가입 되자마자 로그인
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            return render(request, 'login/signup.html', { 'form': CustomAuthenticationForm,
                                                'form_signup': form, 'slug': '총류' })
