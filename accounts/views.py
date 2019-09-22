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
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import redirect, resolve_url
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm
)
from django.contrib.auth.decorators import login_required
from .models import User as UserObj


#get_user_model関数
#プロジェクト内で使用している
User = get_user_model()
#Users = UserObj.objects

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

    

