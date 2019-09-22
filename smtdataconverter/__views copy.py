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
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, resolve_url

from django.contrib.auth.decorators import login_required
from .forms import ConvertForm, FileUploadForm

from accounts import views as accountsviews
from accounts.models import User as MyUser
from .models import DataFile
from django.core.files.storage import default_storage
from django.http import HttpResponse

import pandas as pd     #pandas pip install が必要
import numpy as np      #numpy pip install が必要

import csv
import io
import sys

#get_user_model関数
#プロジェクト内で使用している
User = get_user_model()

#アドレス直下に配置し、最初に表示させる。
#引数先頭のLoginRequiredMixinはログインしていないと自動でリダイレクトさせる。他のアプリ上でも動作する
class _____SmtDataConverterTop(LoginRequiredMixin, generic.TemplateView):
    raise_exception=True
    template_name = 'smtdataconverter/smtdataconverter_top.html'

    #htmlへ反映させるための関数
    def get_context_data(self, **kwargs):
        # 継承元のメソッド呼び出し
        context = super().get_context_data(**kwargs) 
        _a = MyUser.objects.get(pk=self.request.user.id).membershiplicense
        context["membershiplicense"] = _a
        context["username"] = self.request.user
        return context

#変換画面。ここでファイルをドラッグアンドドロップさせて変換実行
class SmtDataConverterTop(LoginRequiredMixin, generic.FormView):
    """変換"""
    model = DataFile
    template_name = 'smtdataconverter/smtdataconverter_top.html'
    success_url = reverse_lazy('smtdataconverter:smtdataconverter_convert_result')
    form_class = ConvertForm

    #本来のDataFile入力formのバリデーションOK後の処理。
    #def form_valid(self, form):        #送信ボタン押すとGetリクエスト？
        #以降に送信ボタン別の挙動、入力されたmodelに保存処理など。
    def form_valid(self,form):
        #csvfile = io.TextIOWrapper(form.cleaned_data['upfile'], encoding='utf-8')
        #reader = csv.reader(csvfile)
        
        if self.request.method == "POST":       #自身へのreqoestがPOSTの場合。template内に{% csrf_token %}が必要。
            #csvfile = io.TextIOWrapper(form.cleaned_data['dragfiles'])     #()内のurlからファイル読み取りストリーム取得
            _u = form.cleaned_data['dragarea'].lstrip("/")      #ファイルパス修正。先頭の'/'は不要。
            #with open( _u,'r',encoding="utf-8") as _cf:                  #fileopen実行 本番環境では要修正と思われる。
                #_allstr = csv.reader(_cf, delimiter=',')
                
            _csvdata = pd.read_csv(_u, header=None, encoding="utf-8")

            v = form.cleaned_data['dragarea']       #ファイル名のみ表示させたい場合、文字列の修正が必要。
        # この部分をあなたのコードに差し替えます。
        #eader = csv.reader(csvfile)
        #count = sum(1 for row in reader)
        #result = 'データ件数は{}件です'.format(count)

        # 結果をブラウザに表示させたいときはこちら
        #return self.render_to_response(self.get_context_data(result=result))
           #form.save()

        return self.render_to_response(self.get_context_data(result=v))

        # 結果をテキストファイルでダウンロードさせたいときはこちら
        #response = HttpResponse(_allstr, content_type='text/csv')
        #response['Content-Disposition'] = 'attachment; filename = "result.csv"'     #ファイルをダウンロードさせたい場合
        #writer = csv.writer(response)
        #for row in _allstr.objects.all():
        #    writer.writerow([row.pk, row.title])
        #return response




#変換画面に関連付けるファイルアップロード。専用ページ無し。
def upload(request):
    """ファイルのアップロード用ビュー"""
    form = FileUploadForm(files=request.FILES)  #formObjectはFileUploadForm　request.FILESはこのビューで受け取ったfile
    
    if form.is_valid(): #フォームの入力内容を検証（バリデーション）しBooleanで返す。
        #True = 検証OKの場合
        info = form.save()   #form = FileUploadForm のsave関数の戻り値（タプル、配列）取得
        (url, objfile) = info #左辺の変数タプルにタプル形式をそれぞれ代入
        return JsonResponse({'url': url})      #Json形式で返す。javascriptへ。内容はurlのみ。タプル型は不可っぽい。
    return HttpResponseBadRequest()             #False=検証NGの場合はHttpResponseBadRequest返す。




#DataFile modelをリスト化するビュー。modelがDBに保存していないので機能しない。
class ConvertResult(LoginRequiredMixin, generic.TemplateView):
    raise_exception=True
    template_name = 'smtdataconverter/smtdataconverter_convert_result.html'

    #def UserList(self):
     #   object_list = User.objects
     #   return render( self, 'accounts/user_list.html', Users )



#DataFile modelをリスト化するビュー。modelがDBに保存していないので機能しない。
class ConvertFileList(LoginRequiredMixin, generic.ListView):
    raise_exception=True
    model = DataFile
    template_name = 'smtdataconverter/convertfile_list.html'

    #def UserList(self):
     #   object_list = User.objects
     #   return render( self, 'accounts/user_list.html', Users )

    