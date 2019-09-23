#アプリ側のviews.py
#ここで各ページの挙動を制御する
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.views import generic
from .forms import LoginForm
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.core.mail import BadHeaderError, send_mail
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import redirect, resolve_url
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm
)
from django.contrib.auth.decorators import login_required
from django.core.files import File

import pandas as pd     #pandas pip install が必要
import numpy as np      #numpy pip install が必要

from .models import User as UserObj
from .forms import TestConvertForm
from accounts import views as accountsviews
from accounts.models import User as MyUser
import sys, os, csv, io

from .models import DataFile
from .filetype_check import ConvertFile_CheckMain as cls_Check
UPLOADE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/files/'

#get_user_model関数
#プロジェクト内で使用している
User = get_user_model()
#Users = UserObj.objects

#テスト用20190922
class Convert(LoginRequiredMixin, generic.FormView):
    model = DataFile
    template_name = 'accounts/convert.html'
    success_url = reverse_lazy('accounts:convert')
    form_class = TestConvertForm
    __path = ''

    #本来のDataFile入力formのバリデーションOK後の処理。
    #def form_valid(self, form):        #送信ボタン押すとGetリクエスト？
        #以降に送信ボタン別の挙動、入力されたmodelに保存処理など。
    def form_valid(self,form):
        
        if self.request.method == "POST":       #自身へのreqoestがPOSTの場合。template内に{% csrf_token %}が必要。
            
            file = self.request.FILES['upfile']     #requestから読み込みファイル取得
            __path = os.path.join(UPLOADE_DIR, 't.txt')   #static/filesフォルダpathとfilenameを結合し、書き込みpath生成
            #destination = open(__path, 'wb')       #ファイルの書き込み。取得ファイルと同じファイルをstatic/filesに書き込み



            with open( __path,'wb+') as output:        #fileopen実行 本番環境では要修正と思われる。
            #   __readarray = file.readlines()
                for __chunk in file.chunks():
                    output.write(__chunk)

                output.close
            
            with open( __path, 'rt') as __tfile:
                __readarray = __tfile.readlines()

            __getdata = list()
            [__getdata.append(__row.strip()) for __row in __readarray ]
            
                

            __filename, __exetension = os.path.splitext(__path)

            __checker = cls_Check()
            __res = __checker.Check_Main(__getdata)       #filecheck結果を取得
            __log = __checker.get_log()
            print(__res)

            with open( __path,'wt') as output:        #fileopen実行 本番環境では要修正と思われる。
                output.write('')
            output.close

            
            #os.remove(__path)      #file delete この記述は意味なし。別のボタンイベントと連動させる。どうやってpath取得させるか？

            if(__res):

                __logarray = __log.splitlines()     #改行含む文字列をlistに変換
                __log2array = np.array(__logarray).reshape(-1, 1).tolist()   #1次元配列を2次元配列へ変換
                response = HttpResponse('', content_type='text/csv')        #responseへHttpResponseオブジェクトを生成。内容はNULLで
                response['Content-Disposition'] = 'attachment; filename = "result.csv"'     #ファイルをダウンロードさせたい場合にパラメータ追加
                writer = csv.writer(response)       #csv.writerオブジェクトに渡す
                writer.writerows(__log2array)       #2次元配列を一括書き込み。

                return response

        return super().form_valid(form)

   




    #本viewからtemplateへ渡すcontextを上書きするメソッド
    #ここでは___nameという本class変数を'name'というinputtextのinitialプロパティに渡している。
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    #元のcontextを呼び出し、次から処理追加。
        context['form'] = TestConvertForm( 
            initial = {         #要素の初期表示内容→設定しなおすことで動的に変更可能。
                #'name': self.___name            #'name' の初期値として___nameを渡す。
                #'dragarea':"Drop File hire"    #drop処理と競合してしまうので初期値設定不可
                } 
            )        
        return context      #contextを返す＝templateへ渡す。






#Topページ。認証不要。ログイン要求する。
#アドレス直下に配置し、最初に表示させる。
class Top(generic.TemplateView):
    template_name = 'accounts/top.html'

#Loginフォームの表示。認証不要。
class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'accounts/login.html'

#ログアウト後の表示処理　Topページへ戻る。認証必要・
class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'accounts/top.html'

#ユーザー仮登録し本登録用のメール送信処理。認証不要。
class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'accounts/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('accounts/mail_template/create/subject.txt', context)
        message = render_to_string('accounts/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('accounts:user_create_done')

#ユーザー登録完了表示画面処理。認証不要。
class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'accounts/user_create_done.html'

#ユーザー本登録画面表示処理。認証不要。
#セッション管理してる。1日。
class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'accounts/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()

#ユーザーがログイン済みか確認する。
#他classの引数として使用。
class OnlyYouMixin(UserPassesTestMixin):
    """ユーザー認証処理"""
    raise_exception = True      #403エラー表示するかどうか

    def test_func(self):
        user = self.request.user        #
        return user.pk == self.kwargs['pk'] or user.is_superuser

#ユーザー情報確認画面。認証必要。
class UserDetail(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'accounts/user_detail.html'

#ユーザー情報更新画面。認証必要。
class UserUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'

    def get_success_url(self):
        return resolve_url('accounts:user_detail', pk=self.kwargs['pk'])

#パスワード変更画面。認証必要。
class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'accounts/password_change.html'

#パスワード変更完了画面。認証必要。
class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'accounts/password_change_done.html'

#パスワードリセット画面。認証必要。
class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'accounts/mail_template/password_reset/subject.txt'
    email_template_name = 'accounts/mail_template/password_reset/message.txt'
    template_name = 'accounts/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('accounts:password_reset_done')

#パスワードリセット確認メール送付画面。認証必要。確認メール送る。
class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'accounts/password_reset_done.html'

#パスワードリセット新パスワード入力画面。認証不要。確認メールからのアクセスのみ。
class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'accounts/password_reset_confirm.html'

#パスワードリセット完了画面。確認メールからのアクセスのみ。
class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'accounts/password_reset_complete.html'

#eメールアドレス変更画面。認証必要。
class EmailChange(LoginRequiredMixin, generic.FormView):
    """メールアドレスの変更"""
    template_name = 'accounts/email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('accounts/mail_template/email_change/subject.txt', context)
        message = render_to_string('accounts/mail_template/email_change/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('accounts:email_change_done')

#eメールアドレス変更確認画面。認証必要。確認メール送る
class EmailChangeDone(LoginRequiredMixin, generic.TemplateView):
    """メールアドレスの変更メールを送ったよ"""
    template_name = 'accounts/email_change_done.html'

#eメールアドレス変更完了画面。認証必要。確認メールからのアドレスのみ。
class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    """リンクを踏んだ後に呼ばれるメアド変更ビュー"""
    template_name = 'accounts/email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)


#管理者専用画面。SuperUser認証必要。
#ユーザーがSuperUserか確認する。
#他classの引数として使用。
class OnlyAdminMixin(UserPassesTestMixin):
    """ユーザー認証処理"""
    raise_exception = True      #403エラー表示するかどうか

    def test_func(self):
        user = self.request.user        #本アプリにリクエストしたuserの取得
        return user.pk == user.is_superuser     #userがsuperuserか比較した結果を返す

class UserAdminList(OnlyAdminMixin, generic.ListView):
    raise_exception=True
    model = User
    template_name = 'accounts/user_admin_list.html'

    #def UserList(self):
     #   object_list = User.objects
     #   return render( self, 'accounts/user_list.html', Users )

    

