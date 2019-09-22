from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm
)

from django.core.files.storage import default_storage

from .models import DataFile
from .widgets import FileUploadableTextArea

User = get_user_model()

#ファイル変換form
class ConvertForm(forms.ModelForm):

    #name = forms.CharField(
    #    initial= 'file name!'
    #)
    
    class Meta:
        model = DataFile
        fields = ('name', 'dragarea')    #widgetsに指定するときもここに設定忘れずに。field一つでもカンマをつけること！！
        widgets = {     #widgetsに指定するfieldをここで指定
            'name': forms.TextInput(attrs={'class':'uploadfilename'}),  #Javascript等にクラス名を渡す。
            'dragarea': FileUploadableTextArea,  # model内の''で指定された入力エリアにwidgetsを関連付け、イベントを追加する
        }

    #本form classの初期処理。
    #元classにフォーム各要素のclass name 設定を継承して登録
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if(field=='name'):      #file name 表示用 inputtextなら
                field.widget.attrs["class"] = "form-control"    #class name 設定



#widgetsで関連付けられるfileuploadform。動作のみで独自のページは持たない。
class FileUploadForm(forms.Form):
    
    file = forms.FileField()        #formObjectはFileField。weidgetsで'dragfiles'のtextareaに上書き？する。

    #uploadされたfileをdefault_storage へ保存し url を返す。
    def save(self):
        upload_file = self.cleaned_data['file']         #バリデーション後の'file'fieldを取得=Dropされたfileそのものを取得
        file_name = default_storage.save(upload_file.name, upload_file) #uploadされたファイルをdefault_storageに保存してファイル名を返す
        #file_name = upload_file.name                                   #保存せずにファイル名のみ返す
        file_url = default_storage.url(file_name)                       #ファイルurlを取得
        
        return file_url, upload_file     #ファイルurlを返す=viewへ値を渡す。
        #return file_name   #ファイル名を返す

