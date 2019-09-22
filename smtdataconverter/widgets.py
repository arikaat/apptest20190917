#ファイルのドラッグアンドドロップ機能のテスト

from django import forms
from django.urls import reverse_lazy

#file upload のwidgets用form class
class FileUploadableTextArea(forms.Textarea):
    """画像アップロード可能なテキストエリア"""

    class Media:        #静的なメディア定義　おそらく対応ページと1対1の関係。
        js = ['js/csrf.js', 'js/upload.js']     #javscriptのファイルを指定。pathは'static/'以下

    def __init__(self, attrs=None):     #初期化時の処理。
        super().__init__(attrs)         #forms.Textareaの__init__を呼び出し？
        if 'class' in self.attrs:       #self.attrs内に'class'が含まれているか判別
            self.attrs['class'] += ' uploadable vLargeTextField'    #既存の'class'に　' uploadable vLargeTextField' を追加
        else:
            self.attrs['class'] = 'uploadable vLargeTextField'      #新規'class'に　' uploadable vLargeTextField' を追加

        self.attrs['data-url'] = reverse_lazy('smtdataconverter:upload')    #'data-url'の移動直前にurlを評価したい＝reverse_lazyを使用。reverseだとすぐ変換。
        
        


    