#アプリ側のviews.py
#ここで各ページの挙動を制御する
import csv
import io
import sys

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
from django.core.files.storage import default_storage
from django.http import HttpResponse

import pandas as pd     #pandas pip install が必要
import numpy as np      #numpy pip install が必要


from .forms import ConvertForm, FileUploadForm
from accounts import views as accountsviews
from accounts.models import User as MyUser
from .models import DataFile
from .filetype_check import ConvertFile_CheckMain as cls_Check

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
    ___name = ''

    #本来のDataFile入力formのバリデーションOK後の処理。
    #def form_valid(self, form):        #送信ボタン押すとGetリクエスト？
        #以降に送信ボタン別の挙動、入力されたmodelに保存処理など。
    def form_valid(self,form):
        #csvfile = io.TextIOWrapper(form.cleaned_data['upfile'], encoding='utf-8')
        #reader = csv.reader(csvfile)
        
        if self.request.method == "POST":       #自身へのreqoestがPOSTの場合。template内に{% csrf_token %}が必要。
            
            #csvfile = io.TextIOWrapper(form.cleaned_data['dragfiles'])     #()内のurlからファイル読み取りストリーム取得
            _u = form.cleaned_data['dragarea'].lstrip("/")      #ファイルパス修正。先頭の'/'は不要。
            with open( _u,'rt',encoding="utf-8") as _cf:                  #fileopen実行 本番環境では要修正と思われる。
                _readarray = _cf.readlines()
            
            _allarray = list()
            [_allarray.append(_row.strip()) for _row in _readarray ]
            #print(_allarray)

            _checker = cls_Check()
            _res = _checker.Check_Main(_allarray)       #filecheck結果を取得
            _log = _checker.get_log()
            ___name = _cf.name
            #_csvdata = pd.read_csv(_u, header=None, encoding="utf-8")
            #_myarray     = np.array
            #_myarray     = _csvdata.values
            
        # この部分をあなたのコードに差し替えます。
        #eader = csv.reader(csvfile)
        #count = sum(1 for row in reader)
        #result = 'データ件数は{}件です'.format(count)

        # 結果をブラウザに表示させたいときはこちら
        #return self.render_to_response(self.get_context_data(result=result))
           #form.save()

        #return self.render_to_response(self.get_context_data(result=v))

        # 結果をテキストファイルでダウンロードさせたいときはこちら

        if(_res):
            ___logarray = _log.splitlines()     #改行含む文字列をlistに変換
            ___log2array = np.array(___logarray).reshape(-1, 1).tolist()   #1次元配列を2次元配列へ変換
            response = HttpResponse('', content_type='text/csv')        #responseへHttpResponseオブジェクトを生成。内容はNULLで
            response['Content-Disposition'] = 'attachment; filename = "result.csv"'     #ファイルをダウンロードさせたい場合にパラメータ追加
            writer = csv.writer(response)       #csv.writerオブジェクトに渡す
            writer.writerows(___log2array)       #2次元配列を一括書き込み。

            return response                     #レスポンスを返す

    #form の要素に 変数を渡すためのメソッド
    def change_form_object(self, ___value):
        self.___name = ___value

    #本viewからtemplateへ渡すcontextを上書きするメソッド
    #ここでは___nameという本class変数を'name'というinputtextのinitialプロパティに渡している。
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    #元のcontextを呼び出し、次から処理追加。
        context['form'] = ConvertForm( 
            initial = {         #要素の初期表示内容→設定しなおすことで動的に変更可能。
                'name': self.___name            #'name' の初期値として___nameを渡す。
                #'dragarea':"Drop File hire"    #drop処理と競合してしまうので初期値設定不可
                } 
            )        
        return context      #contextを返す＝templateへ渡す。




#変換画面に関連付けるファイルアップロード。専用ページ無し。
def upload(request):
    """ファイルのアップロード用ビュー"""
    form = FileUploadForm(files=request.FILES)  #formObjectはFileUploadForm　request.FILESはこのビューで受け取ったfile
    
    if form.is_valid(): #フォームの入力内容を検証（バリデーション）しBooleanで返す。
        #True = 検証OKの場合
        info = form.save()   #form = FileUploadForm のsave関数の戻り値（タプル、配列）取得
        (url, objfile) = info #左辺の変数タプルにタプル形式をそれぞれ代入
        return JsonResponse({'url': url })      #Json形式で返す。javascriptへ。内容はurlのみ。タプル型は不可っぽい。
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

    