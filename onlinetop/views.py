#アプリ側のviews.py
#ここで各ページの挙動を制御する
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.views import generic
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.core.mail import BadHeaderError, send_mail
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, resolve_url

from django.contrib.auth.decorators import login_required
from accounts import views as accountsviews
from accounts.models import User as MyUser



#Topページ。認証不要。ログイン要求する。
#アドレス直下に配置し、最初に表示させる。
class OnlineTop(generic.TemplateView):
    template_name = 'onlinetop/online_top.html'
    
        
#会員用のTopページ。認証必要。直リン不可
#引数先頭のLoginRequiredMixinはログインしていないと自動でリダイレクトさせる。他のアプリ上でも動作する
class MembershipTop(LoginRequiredMixin, generic.TemplateView):
    raise_exception=True
    template_name = 'onlinetop/membership_top.html'

    #htmlへ反映させるための関数
    def get_context_data(self, **kwargs):
        # 継承元のメソッド呼び出し
        context = super().get_context_data(**kwargs) 
        _a = MyUser.objects.get(pk=self.request.user.id).membershiplicense
        context["membershiplicense"] = _a
        context["username"] = self.request.user
        return context
        
    