#uploadされたfileのformatをcheckする。
#check結果に応じてconvert_xxxを呼び出す。
from django.shortcuts import render
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
from django.http import Http404, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, resolve_url
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from weakref import WeakValueDictionary

import pandas as pd     #pandas pip install が必要
import numpy as np      #numpy pip install が必要

from .forms import ConvertForm, FileUploadForm
from accounts import views as accountsviews
from .models import DataFile


import csv
import io
import sys



#ファイルをチェックし結果を返すクラス
class ConvertFile_CheckMain():

    def __init__(self):
        self.___log = ""
        self.___result = False

    def Check_Main(self, list_array):
        self.___yvc = Check_VIOSTEXT(list_array)
        self.___result = self.___yvc.Check()
        self.___log = self.___yvc.get_Log()
        return self.___result

    def get_log(self):
        return self.___log 

#ファイルタイプを検査する基底クラス
class Check_Base(object):
    def __init__(self, list_array):
        self.___log = ''
        try:
            self.___data = list_array        #list型（配列）参照渡し
            self.___imported = True
            self.add_Log('list_array import success.')      #処理メッセージ
        except:                         #参照渡し失敗
            self.___imported = False
            self.add_Log('list_array import fialed.')       #処理メッセージ
            self.___result      = False                     #この時点で失敗

    def __str__(self):
        return self.get_Result()           
       
    def add_Log(self, ___str):
        self.___log = self.___log + '\n' + ___str
        return  self.___log

    def get_Log(self):
        return self.___log

    def get_Result(self):
        return self.___result

    def get_Inported(self):
        return self.___imported

    def get_Data(self):
        return self.___data


#VIOSTEXTをチェックするスーパークラス
class Check_VIOSTEXT(Check_Base):
    
    def __init__(self, ___data):
        super().__init__(___data)
        #super()はメソッドを継承するのみ。各ローカル変数は継承元のget_メソッドで取得する。
        self.___data = self.get_Data()      
        self.___Imported = self.get_Inported()      

    def Check(self):
        if(self.___Imported):
            #先頭に'PCBNAME='が存在するか？
            ___cstr = self.___data[0]
            if not('PCBNAME=' in ___cstr): return False

            for (___i1, ___cstr) in enumerate(self.___data):
                if('End_of_ID' in ___cstr ):
                    ___r = True
                    break
            if not(___r):return False
            ___r = False

            for (___i2, ___cstr) in enumerate(self.___data[___i1:len(self.___data)]):
                if('&B.MNT' in ___cstr ):
                    ___r = True
                    break
            if not(___r):return False
            ___r = False

            for (___i3, ___cstr) in enumerate(self.___data[___i2:len(self.___data)]):
                if('&B.MNT' in ___cstr ):
                    ___r = True
                    break
            if not(___r):return False
            ___r = False

            for (___i4, ___cstr) in enumerate(self.___data[___i3:len(self.___data)]):
                if('&B.OPT' in ___cstr ):
                    ___r = True
                    break
            if not(___r):return False
            ___r = False

            for (___i5, ___cstr) in enumerate(self.___data[___i4:len(self.___data)]):
                if('End_of_BD' in ___cstr ):
                    ___r = True
                    break
            if not(___r):return False
            ___r = False

            for (___i6, ___cstr) in enumerate(self.___data[___i5:len(self.___data)]):
                if('End_of_FD' in ___cstr ):
                    ___r = True
                    break
            if not(___r):return False

            self.add_Log('Now Data VIOS-TEXT.')    #先頭に改行添付して___resultに連結 + 先頭にr追加でエスケープ回避
            return True
        else:
            self.add_Log('Now Data Non VIOS-TEXT.') #先頭に改行添付して___resultに連結 + 先頭にr追加でエスケープ回避
            return False
      
